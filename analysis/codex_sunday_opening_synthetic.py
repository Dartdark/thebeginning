"""Execution regression checks; synthetic data only, no return trials."""
from types import SimpleNamespace
import numpy as np
from codex_sunday_opening_screen import replay


def main():
    row=dict(row=0,date='2020-01-05',first_eligible_flat_index=1037,
             source_week_filter_down=True,source_week_change_pct=-1.,
             entry_to_1912_expected_minutes=116,entry_to_1912_present_minutes=116)
    arrays={k:np.full((1,1440),100.) for k in ('o','h','l','c')}
    arrays['h'][0,1037]=300.  # pre-entry high must not generate a target fill
    x=replay(SimpleNamespace(**arrays),row,True,1,True)
    assert x['kind']=='time'
    arrays['h'][0,1038]=300.; arrays['l'][0,1038]=0.
    x=replay(SimpleNamespace(**arrays),row,False,1,False)
    assert x['kind']=='stop' and x['ambiguous'] and x['stop']==20.25
    assert abs(x['net_mnq']+161.54)<1e-8
    sparse={k:np.full((1,1440),np.nan) for k in ('o','h','l','c')}
    for a in sparse.values(): a[0,[1037,1038]]=100.
    sparse['l'][0,1038]=0.
    assert replay(SimpleNamespace(**sparse),row)['kind']=='stop'
    for a in sparse.values():
        a[:]=np.nan; a[0,[1037,1153,1154]]=100.
    assert replay(SimpleNamespace(**sparse),row)['status']=='unresolved_entry_at_or_after_exit_threshold'
    for a in arrays.values(): a[:]=100.
    arrays['h'][0,1038]=151.4
    one=replay(SimpleNamespace(**arrays),row,False,1,False)
    two=replay(SimpleNamespace(**arrays),row,False,2,False)
    assert one['kind']=='target' and two['kind']=='time'
    print('PASS: close chronology, stop-first ambiguity, actual-fill anchors, early exits, delayed entries, V2 replay.')


if __name__=='__main__':
    main()
