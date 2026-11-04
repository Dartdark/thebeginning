"""Research-only event account engine for the November 4 evaluation audit.

No import-time market reads. `simulate` consumes a caller-built chronological
tape; it never manufactures quotes, OHLC paths, fills or missing returns.
One asset has one price at an event, including when sleeves oppose each other.

Trade event columns (float array): row,trade_id,key,asset,action,side,raw_fill,
stop_points,requested_quantity,fill_kind. Actions +1 enter/-1 exit. Fill kind
0 market,1 limit,2 stop; raw fills get adverse configured slippage except limits.
Prices are executable reference marks: the caller must insert the actual source
fill level at that asset/event or explicitly declare its uncertainty outside
this engine. Event time can be compressed, but no relevant active mark omitted.
"""
from dataclasses import dataclass
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import numpy as np
from numba import njit

EVENT_COLUMNS=('row','trade_id','key','asset','action','side','raw_fill',
               'stop_points','requested_quantity','fill_kind')
ACTIVE=0;PASSED=1;FAILED=2;EXPIRED=3;UNKNOWN=4
REASONS={0:'end_of_tape',1:'realized_target_after_flatten',2:'intraday_floor',
         3:'post_liquidation_floor',4:'expiry',5:'missing_held_price',
         6:'source_fill_does_not_match_event_price',7:'late_flat_deadline',
         8:'open_at_session_boundary',9:'duplicate_or_invalid_entry',10:'missing_exact_expiry_price'}

@dataclass(frozen=True)
class EvalRules:
    nominal_start: float
    target_profit: float
    trail: float
    dll: float
    max_micro_contracts: int
    floor_cap: float=np.inf  # Eval cap is NOT nominal_start+100 (that is PA).
    target_buffer: float=50.
    target_guard: bool=True

EOD50=EvalRules(50000.,3000.,2000.,1000.,60,53000.)
EOD150=EvalRules(150000.,9000.,4000.,2000.,120,159000.)

def modeled_expiry(purchase,calendar_days=30):
    """Declared research convention only; an actual purchased expiry overrides.

    Add30 calendar dates to the purchase date and end at17:00Chicago. Official
    billing language mixes30days from purchase with Day30 close; exact purchased
    dashboard expiry is authoritative. The engine itself requires an explicit
    expiry epoch rather than treating21trading sessions as30calendar days.
    """
    if isinstance(purchase,str):purchase=datetime.fromisoformat(purchase)
    if purchase.tzinfo is None:raise ValueError('Purchase timezone required')
    local=purchase.astimezone(ZoneInfo('America/Chicago'))
    day=local.date()+timedelta(days=calendar_days)
    return int(datetime(day.year,day.month,day.day,17,tzinfo=local.tzinfo).timestamp())

@njit(cache=True)
def _equity(cash,net,basis,price,pv):
    eq=cash
    for a in range(len(price)):
        eq-=basis[a]
        if net[a]!=0:
            if not np.isfinite(price[a]):return np.nan
            eq+=net[a]*price[a]*pv[a]
    return eq

@njit(cache=True)
def _liquidate(cash,q,net,basis,price,pv,fee,slip):
    """One broker net order per asset, not gross opposing virtual orders."""
    eq=_equity(cash,net,basis,price,pv);cost=0.
    for a in range(len(price)):cost+=abs(net[a])*(fee[a]+slip[a]*pv[a])
    q[:]=0.;net[:]=0.;basis[:]=0.
    return eq-cost,cost

@njit(cache=True)
def _net_exposure(net,newasset=-1,newside=0,newqty=0):
    total=0.
    for a in range(len(net)):
        value=net[a]+(newside*newqty if a==newasset else 0.)
        total+=abs(value)
    return total

@njit(cache=True)
def _stop_reserve(q,side,entry,asset,stop,price,pv,fee,slip):
    reserve=0.
    for i in range(len(q)):
        if q[i]>0:
            if not np.isfinite(stop[i]) or stop[i]<=0 or not np.isfinite(price[asset[i]]):return np.inf
            st=entry[i]-side[i]*stop[i]
            reserve+=max(0.,(price[asset[i]]-st)*side[i]*pv[asset[i]])*q[i]
            reserve+=q[i]*(fee[asset[i]]+slip[asset[i]]*pv[asset[i]])
    return reserve

@njit(cache=True)
def _run(prices,times,sessions,events,pv,fee,slip,cutoffs,expiry,
         nominal,target,trail,dll,maxcontracts,cap,targetbuffer,targetguard,
         initialcash,initialfloor,riskfraction,cushionbuffer,aggregate_reserve,
         block_key_after_rejection,fill_tolerance,nodes,segmin,segmax,segmissing,aggregate_fraction,record_logs):
    ntrades=int(np.max(events[:,1]))+1 if len(events) else 1
    nkeys=int(np.max(events[:,2]))+1 if len(events) else 1
    q=np.zeros(ntrades);side=np.zeros(ntrades);entry=np.zeros(ntrades)
    net=np.zeros(prices.shape[1]);basis=np.zeros(prices.shape[1])
    asset=np.zeros(ntrades,np.int64);stop=np.zeros(ntrades)
    blocked=np.zeros(nkeys,np.bool_)
    cash=initialcash;floor=initialfloor;peak=max(cash,floor+trail)
    session_start=cash;current=-1;paused=False;e=0;open_count=0
    status=ACTIVE;reason=0;finished=-1;minimum=cash;minbound=cash;maxexposure=0.;skipped=0;nodeidx=0
    fills=0;rejected=0;trimmed=0;dlls=0;forcedflats=0;liqcost=0.;fees=0.;slippage=0.
    # event logs: row,trade_id,action,accepted_qty,fill,fee,after_equity,reason.
    log=np.full((len(events)+3*int(sessions[-1]-sessions[0]+1)+4 if record_logs else 0,8),np.nan);ln=0
    row=0
    while row<len(prices):
        finished=row
        if times[row]>=expiry:
            # Expiry is an account boundary; never grant subsequent source PnL.
            if open_count>0:
                if times[row]>expiry:status=UNKNOWN;reason=10;break
                if not np.isfinite(_equity(cash,net,basis,prices[row],pv)):
                    status=UNKNOWN;reason=5;break
                cash,cost=_liquidate(cash,q,net,basis,prices[row],pv,fee,slip);liqcost+=cost;open_count=0
            status=EXPIRED;reason=4;break
        ses=sessions[row]
        if ses!=current:
            if current>=0:
                if open_count>0:status=UNKNOWN;reason=8;break
                peak=max(peak,cash);floor=max(floor,min(peak-trail,cap))
            current=ses;session_start=cash;paused=False;blocked[:]=False
        price=prices[row]
        eq=_equity(cash,net,basis,price,pv)
        if not np.isfinite(eq):status=UNKNOWN;reason=5;break
        minimum=min(minimum,eq)
        # Account floor is inclusive, checked before target and source orders.
        if eq<=floor:
            cash,cost=_liquidate(cash,q,net,basis,price,pv,fee,slip);liqcost+=cost;open_count=0
            status=FAILED;reason=2;break
        if dll>0 and eq<=session_start-dll and not paused:
            cash,cost=_liquidate(cash,q,net,basis,price,pv,fee,slip);liqcost+=cost;dlls+=1;paused=True;open_count=0
            minimum=min(minimum,cash)
            if record_logs:
                log[ln]=np.array([row,-1.,-2.,0.,np.nan,cost,cash,2.]);ln+=1
            if cash<=floor:status=FAILED;reason=3;break
        # Target protection models actual flattening costs, not free threshold fills.
        eq=_equity(cash,net,basis,price,pv)
        if targetguard and not paused and eq>=nominal+target+targetbuffer:
            cash,cost=_liquidate(cash,q,net,basis,price,pv,fee,slip);liqcost+=cost;open_count=0
            if cash<=floor:status=FAILED;reason=3;break
            if cash>=nominal+target:status=PASSED;reason=1;break
            paused=True
        if cutoffs[ses]>0 and times[row]>=cutoffs[ses]:
            if open_count>0:
                if times[row]>cutoffs[ses]:status=UNKNOWN;reason=7;break
                cash,cost=_liquidate(cash,q,net,basis,price,pv,fee,slip);liqcost+=cost;forcedflats+=1;open_count=0
                if cash<=floor:status=FAILED;reason=3;break
            paused=True
        eq=_equity(cash,net,basis,price,pv)
        if _net_exposure(net)==0 and eq>=nominal+target:
            # Opposing source sleeves may leave virtual tickets open although
            # the broker position is flat. Their locked basis is realized
            # account equity; clearing bookkeeping needs no market order/cost.
            cash,cost=_liquidate(cash,q,net,basis,price,pv,fee,slip);liqcost+=cost;open_count=0
            status=PASSED;reason=1;break
        # Input is sorted exit-before-entry at a shared time/price; unknown ties
        # must be declared by caller. No policy silently prefers a target over risk.
        while e<len(events) and int(events[e,0])==row:
            v=events[e];tid=int(v[1]);key=int(v[2]);a=int(v[3]);action=int(v[4]);s=int(v[5]);raw=v[6];st=v[7];req=int(v[8]);kind=int(v[9]);e+=1
            if action==-1 and q[tid]==0:continue
            if action==1 and (paused or blocked[key]):continue
            if action==1 and req==0:continue  # An unallocated source key needs no executable quote.
            if action==-1 and (a!=asset[tid] or s!=side[tid]):
                status=UNKNOWN;reason=9;break
            order_side=s if action==1 else -s
            limit_ok=kind==1 and (raw-price[a])*order_side>=-fill_tolerance
            if not np.isfinite(price[a]) or not np.isfinite(raw) or (abs(price[a]-raw)>fill_tolerance and not limit_ok):
                status=UNKNOWN;reason=6;break
            if action==1:
                if q[tid]>0 or req<0 or abs(s)!=1:status=UNKNOWN;reason=9;break
                qty=req
                if riskfraction>0:
                    if not np.isfinite(st) or st<=0:qty=0
                    else:
                        eq=_equity(cash,net,basis,price,pv)
                        reserve=_stop_reserve(q,side,entry,asset,stop,price,pv,fee,slip) if aggregate_reserve else 0.
                        headroom=max(0.,eq-floor-cushionbuffer)
                        dllroom=max(0.,eq-session_start+dll) if dll>0 else np.inf
                        budget=max(0.,min(headroom*riskfraction,headroom*aggregate_fraction-reserve,dllroom-reserve))
                        per=st*pv[a]+2*fee[a]+2*slip[a]*pv[a]
                        qty=min(qty,int(np.floor(budget/per)))
                if qty<req:trimmed+=1
                if qty<=0 or _net_exposure(net,a,s,qty)>maxcontracts:
                    rejected+=1
                    if block_key_after_rejection:blocked[key]=True
                    if record_logs:
                        log[ln]=np.array([row,tid,action,0.,raw,0.,_equity(cash,net,basis,price,pv),1.]);ln+=1
                    continue
                px=raw+s*(0. if kind==1 else slip[a]);charge=qty*fee[a]
                q[tid]=qty;side[tid]=s;entry[tid]=px;asset[tid]=a;stop[tid]=st
                open_count+=1
                net[a]+=s*qty;basis[a]+=px*s*qty*pv[a]
                cash-=charge;fees+=charge;slippage+=qty*abs(px-raw)*pv[a];fills+=1
            elif action==-1:
                qty=q[tid];s=int(side[tid]);a=asset[tid]
                px=raw-s*(0. if kind==1 else slip[a]);charge=qty*fee[a]
                cash+=(px-entry[tid])*s*qty*pv[a]-charge
                net[a]-=s*qty;basis[a]-=entry[tid]*s*qty*pv[a]
                fees+=charge;slippage+=qty*abs(px-raw)*pv[a];fills+=1;q[tid]=0.;open_count-=1
            else:status=UNKNOWN;reason=9;break
            eq=_equity(cash,net,basis,price,pv);minimum=min(minimum,eq)
            maxexposure=max(maxexposure,_net_exposure(net))
            if record_logs:
                log[ln]=np.array([row,tid,action,qty,px,charge,eq,0.]);ln+=1
            if eq<=floor:
                cash,cost=_liquidate(cash,q,net,basis,price,pv,fee,slip);liqcost+=cost;open_count=0
                status=FAILED;reason=2;break
            if dll>0 and eq<=session_start-dll:
                cash,cost=_liquidate(cash,q,net,basis,price,pv,fee,slip);liqcost+=cost;dlls+=1;paused=True;open_count=0
                if cash<=floor:status=FAILED;reason=3;break
            eq=_equity(cash,net,basis,price,pv)
            if _net_exposure(net)==0 and eq>=nominal+target:
                cash,cost=_liquidate(cash,q,net,basis,price,pv,fee,slip);liqcost+=cost;open_count=0
                status=PASSED;reason=1;break
        if status!=ACTIVE:break
        # Between source events positions are fixed. Bounds are used only to
        # PROVE safety; ambiguous segments still walk the same raw quote tape.
        while nodeidx<len(nodes) and nodes[nodeidx]<row:nodeidx+=1
        if nodeidx+1<len(nodes) and nodes[nodeidx]==row:
            nex=nodes[nodeidx+1];lower=cash;upper=cash;finite=True
            for a in range(len(price)):
                lower-=basis[a];upper-=basis[a]
                if net[a]!=0:
                    if segmissing[nodeidx,a]:finite=False;break
                    if net[a]>0:
                        lower+=net[a]*pv[a]*segmin[nodeidx,a]
                        upper+=net[a]*pv[a]*segmax[nodeidx,a]
                    else:
                        lower+=net[a]*pv[a]*segmax[nodeidx,a]
                        upper+=net[a]*pv[a]*segmin[nodeidx,a]
            riskline=floor
            if dll>0 and not paused:riskline=max(riskline,session_start-dll)
            can_target=targetguard and not paused and upper>=nominal+target+targetbuffer
            cross_cutoff=(cutoffs[ses]>0 and times[row]<cutoffs[ses] and times[nex]>cutoffs[ses] and open_count>0)
            if finite and lower>riskline and not can_target and times[nex]<expiry and not cross_cutoff:
                minbound=min(minbound,lower);skipped+=max(0,nex-row-1);row=nex;continue
        row+=1
    finaleq=_equity(cash,net,basis,prices[max(0,finished)],pv) if len(prices) else cash
    minimum=min(minimum,finaleq) if np.isfinite(finaleq) else minimum
    return np.array([status,reason,finished,cash,finaleq,floor,minimum,maxexposure,fills,rejected,trimmed,dlls,forcedflats,fees,slippage,liqcost,np.count_nonzero(q),min(minbound,minimum),skipped]),log[:ln]

def simulate(prices,times,sessions,trade_events,point_values,commission_per_side,slippage_points,
             cutoff_times,expiry_time,*,rules=EOD50,initial_equity=None,initial_floor=None,
             risk_fraction=0.,cushion_buffer=0.,aggregate_stop_reserve=True,
             block_key_after_rejection=True,fill_tolerance=1e-7,
             node_rows=None,segment_min=None,segment_max=None,segment_missing=None,
             aggregate_stop_fraction=1.,record_logs=False):
    """Return account outcome and immutable event logs, with explicit UNKNOWN.

    Initial quantities are integer `requested_quantity` on each entry. A positive
    risk_fraction caps new nominal stop exposure from current remaining cushion,
    optionally reserving already-open stop risk; 0 leaves source requested size.
    A rejected entry can block its strategy for that session, preventing phantom
    conditional re-entries after a skipped base. This is a declared allocator
    policy, not a source-replay equivalence claim. All quantities are micro units.
    cutoff_times indexed by integer session are caller-frozen15:59CT epochs.
    Expiry and purchase-time interpretation must be supplied explicitly.
    """
    prices=np.ascontiguousarray(prices,dtype=np.float64)
    times=np.ascontiguousarray(times,dtype=np.int64);sessions=np.ascontiguousarray(sessions,dtype=np.int64)
    events=np.asarray(trade_events,dtype=np.float64).reshape(-1,10)
    if prices.ndim!=2 or len(prices)!=len(times) or len(times)!=len(sessions):raise ValueError('Tape shapes differ')
    if len(times)==0 or np.any(np.diff(times)<0) or np.any(np.diff(sessions)<0):raise ValueError('Nonchronological tape')
    if np.min(sessions)<0:raise ValueError('Nonnegative session indices required')
    if len(events):
        if not np.isfinite(events[:,[0,1,2,3,4,5,8,9]]).all() or np.isinf(events[:,6]).any():raise ValueError('Invalid event fields')
        for c in [0,1,2,3,4,5,8,9]:
            if not np.equal(events[:,c],np.floor(events[:,c])).all():raise ValueError('Event integer field is fractional')
        if (events[:,0]<0).any() or (events[:,0]>=len(times)).any():raise ValueError('Event outside tape')
        if (events[:,1:4]<0).any() or (events[:,3]>=prices.shape[1]).any():raise ValueError('Invalid id/asset')
        if not np.isin(events[:,4],[-1,1]).all() or not np.isin(events[:,5],[-1,1]).all() or not np.isin(events[:,9],[0,1,2]).all():raise ValueError('Invalid action/side/fill kind')
        # Active exits precede new entries. A unit trade that opens AND closes
        # at one event must instead close immediately AFTER its own entry;
        # otherwise an ignored pre-entry exit would create a phantom carry.
        ent=events[events[:,4]==1]
        if len(np.unique(ent[:,1]))!=len(ent):raise ValueError('Trade ids must have a unique entry')
        ex=events[events[:,4]==-1]
        if len(np.unique(ex[:,1]))!=len(ex):raise ValueError('Trade ids must have at most one exit')
        erow={int(v[1]):int(v[0]) for v in ent}
        ownexit=np.array([v[4]==-1 and erow.get(int(v[1]),-1)==int(v[0]) for v in events])
        orderclass=np.where((events[:,4]==-1)&~ownexit,0,1)
        events=events[np.lexsort((ownexit.astype(int),events[:,1],events[:,2],orderclass,events[:,0]))]
        trade_id_map,ids=np.unique(events[:,1].astype(np.int64),return_inverse=True)
        events=events.copy();events[:,1]=ids
    else:trade_id_map=np.zeros(0,dtype=np.int64)
    vectors=[np.ascontiguousarray(x,dtype=np.float64) for x in [point_values,commission_per_side,slippage_points]]
    if any(len(x)!=prices.shape[1] for x in vectors):raise ValueError('Asset vector mismatch')
    if not np.isfinite(vectors).all() or (vectors[0]<=0).any() or any((x<0).any() for x in vectors[1:]):raise ValueError('Invalid costs/pointvalues')
    cutoff=np.asarray(cutoff_times,dtype=np.int64)
    if len(cutoff)<=np.max(sessions):raise ValueError('Missing session cutoffs')
    if not 0<=risk_fraction<=1 or not 0<aggregate_stop_fraction<=1:raise ValueError('Risk fraction outside0..1')
    cash=rules.nominal_start if initial_equity is None else float(initial_equity)
    floor=rules.nominal_start-rules.trail if initial_floor is None else float(initial_floor)
    if node_rows is None:
        nodes=np.zeros(0,dtype=np.int64);mins=np.empty((0,prices.shape[1]));maxs=mins.copy();missing=np.empty((0,prices.shape[1]),dtype=np.bool_)
    else:
        nodes=np.asarray(node_rows,dtype=np.int64)
        if len(nodes)<2 or nodes[0]!=0 or nodes[-1]!=len(prices)-1 or np.any(np.diff(nodes)<=0):raise ValueError('Bad segment nodes')
        if len(events) and not np.isin(events[:,0].astype(int),nodes).all():raise ValueError('Source event omitted from segment nodes')
        if not np.isin(np.r_[0,np.flatnonzero(np.diff(sessions))+1],nodes).all():raise ValueError('Session boundary omitted from segment nodes')
        mins=np.ascontiguousarray(segment_min,dtype=float);maxs=np.ascontiguousarray(segment_max,dtype=float);missing=np.ascontiguousarray(segment_missing,dtype=np.bool_)
        if mins.shape!=(len(nodes)-1,prices.shape[1]) or maxs.shape!=mins.shape or missing.shape!=mins.shape:raise ValueError('Segment shape mismatch')
    values,log=_run(prices,times,sessions,np.ascontiguousarray(events),*vectors,cutoff,int(expiry_time),
        rules.nominal_start,rules.target_profit,rules.trail,rules.dll,rules.max_micro_contracts,
        rules.floor_cap,rules.target_buffer,rules.target_guard,cash,floor,risk_fraction,cushion_buffer,
        aggregate_stop_reserve,block_key_after_rejection,fill_tolerance,nodes,mins,maxs,missing,aggregate_stop_fraction,record_logs)
    keys=('status','reason','last_row','cash','equity','floor','minimum_equity','max_net_micro_exposure',
          'fill_count','rejected_entries','trimmed_entries','dll_pauses','forced_cutoff_flats',
          'commission','source_fill_slippage','liquidation_cost','open_virtual_positions',
          'minimum_equity_lower_bound','skipped_raw_rows')
    result=dict(zip(keys,values.tolist()))
    result['status_name']={0:'active_at_tape_end',1:'pass',2:'fail',3:'expired',4:'unknown'}[int(values[0])]
    result['reason_name']=REASONS[int(values[1])]
    # Minimum equity in fast mode is the visited-node minimum; the bound is
    # conservative across assets and must not be mislabeled exact joint DD.
    result['minimum_equity_scope']='allvisitedquotes' if node_rows is None else 'visitednodes_and_potential-risksegments;see_lower_bound'
    valid=log[:,1]>=0
    log[valid,1]=trade_id_map[log[valid,1].astype(int)]
    return result,log
