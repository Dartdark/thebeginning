"""SSRN2419243: synthetic source-mechanics checks, not a return backtest."""
import hashlib
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np


def scores(average_yields, current_yields):
    """Literal p12 direction; declared global median over all 55 pair magnitudes."""
    pairs=[]
    for i in range(11):
        for j in range(i+1,11):
            avg=average_yields[j]-average_yields[i]
            if avg == 0:
                raise ValueError("Source normalization divides by zero average differential")
            value=(current_yields[j]-current_yields[i]-avg)/abs(avg)
            pairs.append((i,j,value))
    median=np.median([abs(v) for _,_,v in pairs])
    result=np.zeros(11,dtype=int)
    for i,j,v in pairs:
        if abs(v)>median:
            result[i]+=int(np.sign(v));result[j]-=int(np.sign(v))
    return result


def main():
    # A country2 rate rise against unchanged country1 produces +country1/-country2,
    # the opposite of the verbal buy-rising-relative-rate hypothesis. This is the
    # unfiltered pair attribution, not a two-country version of the full strategy.
    avg_gap=2.0-1.0
    current_gap=3.0-1.0
    sub=(current_gap-avg_gap)/abs(avg_gap)
    assert sub>0
    # First seeded synthetic yield panel, no return data or fitted parameters.
    rng=np.random.default_rng(2419243)
    average=rng.uniform(.1,5,11)
    current=average+rng.normal(0,.1,11)
    s=scores(average,current)
    gross=np.abs(s[:-1]).sum()  # source trades ten xxxUSD instruments; USD signal omitted
    weight=float(np.abs(s[:-1]).max()/gross)
    assert weight>.2
    assert s.sum()==0
    try:
        scores(np.ones(11)*2,np.ones(11)*2.1)
    except ValueError:
        zero_case=True
    else:
        raise AssertionError("Zero differential must not silently define a signal")
    clocks=[]
    for date in ["2014-03-20","2014-04-10"]:
        london=datetime.fromisoformat(date+"T18:00").replace(tzinfo=ZoneInfo("Europe/London"))
        ny=datetime.fromisoformat(date+"T17:00").replace(tzinfo=ZoneInfo("America/New_York"))
        clocks.append(dict(date=date,london_close_ct=london.astimezone(ZoneInfo("America/Chicago")).isoformat(),
                          ny_close_ct=ny.astimezone(ZoneInfo("America/Chicago")).isoformat()))
    result=dict(scope="deterministic source/clock checks; zero economic trials and no observed market returns",
        source_sha256="94876145e51529535b40b61d60e9475e5c01d17fcedf5be93ad0577751952fe8",
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        pair_example=dict(mean_difference=avg_gap,current_difference=current_gap,subsignal=sub,
            literal_country1_change=1,literal_country2_change=-1,
            finding="Country2 relative rate rises, but literal formula sells its currency"),
        concentration_example=dict(seed=2419243,interpretation="global median, raw scores then normalize ten tradable legs",
            currency_order=["AUD","CAD","CHF","DKK","EUR","GBP","JPY","NOK","NZD","SEK","USD"],
            average_yields=average.tolist(),current_yields=current.tolist(),scores=s.tolist(),
            gross_tradable_score=int(gross),maximum_absolute_weight=weight,
            finding="20% bound does not follow under this declared interpretation; extra sizing rules needed"),
        zero_mean_differential_undefined=zero_case,clocks=clocks)
    path=Path("analysis/outputs/codex_ananta_source_audit/checks.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
