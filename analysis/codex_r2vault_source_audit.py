"""Arithmetic on visually verified R2Vault PDF claims; no market-price returns."""
from pathlib import Path
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"agents/codex/inputs/r2vault/source.pdf"
OUT=ROOT/"analysis/outputs/codex_r2vault"


def audit():
    annual={2017:20305,2018:5145,2019:11980,2020:32580,2021:37000,
            2022:13085,2023:28015,2024:32525,2025:29645,2026:55500}
    full=dict(net=265780,trades=2518,printed_average=105.55,profit_factor=1.23,
              win_percent=69.54,max_drawdown=17420,sharpe=.44,time_in_market_percent=28.99,
              printed_period="2017-01-13..2026-08-31",adjusted_net=190300.45)
    ins=dict(net=180635,trades=1947,printed_average=92.78,profit_factor=1.20,
             win_percent=69.08,max_drawdown=17420,printed_period="2017-01-19..2024-12-31")
    oos=dict(net=88675,trades=564,profit_factor=1.37,win_percent=71.45,
             printed_period="2025-01-15..2026-08-31")
    native=dict(gross_profit=1417805,gross_loss=1152025,winning_trades=1751,losing_trades=767,
                largest_win=4950,largest_loss=-2205,printed_average_win=809.71,printed_average_loss=-1501.99,
                max_close_to_close_drawdown=-16500,mc_paths=10000,mc_trade_percent=100,
                mc_smallest_drawdown=-12915,mc_largest_drawdown=-63225,
                title="Backtesting Strategy Performance Report: @NQ -5Minutes",chart_starting_equity=100000)
    statistical_adjusted=full["net"]-native["gross_profit"]/math.sqrt(native["winning_trades"])-native["gross_loss"]/math.sqrt(native["losing_trades"])
    checks=dict(
        annual_sum=sum(annual.values()),annual_sum_matches_full=sum(annual.values())==full["net"],
        annual2017_24=sum(v for y,v in annual.items() if y<=2024),
        annual2017_24_matches_IS=sum(v for y,v in annual.items() if y<=2024)==ins["net"],
        annual2025_26=annual[2025]+annual[2026],full_mean_exact=full["net"]/full["trades"],
        full_mean_product=full["trades"]*full["printed_average"],
        full_rounding_residual=full["net"]-full["trades"]*full["printed_average"],
        IS_mean_exact=ins["net"]/ins["trades"],IS_mean_product=ins["trades"]*ins["printed_average"],
        IS_rounding_residual=ins["net"]-ins["trades"]*ins["printed_average"],
        OOS_mean_implied=oos["net"]/oos["trades"],
        IS_plus_OOS_net=ins["net"]+oos["net"],IS_plus_OOS_trades=ins["trades"]+oos["trades"],
        full_minus_IS_OOS_net=full["net"]-ins["net"]-oos["net"],
        full_minus_IS_OOS_trades=full["trades"]-ins["trades"]-oos["trades"],
        annual2025_26_minus_OOS=annual[2025]+annual[2026]-oos["net"],
        native_gross_difference=native["gross_profit"]-native["gross_loss"],
        native_profit_factor=native["gross_profit"]/native["gross_loss"],
        native_win_percent=native["winning_trades"]*100/full["trades"],
        native_average_win=native["gross_profit"]/native["winning_trades"],
        native_average_loss=-native["gross_loss"]/native["losing_trades"],
        statistical_count_adjustment_net=statistical_adjusted,
        statistical_adjustment_matches_printed_cents=round(statistical_adjusted,2)==full["adjusted_net"],
        full_minus_adjusted=full["net"]-full["adjusted_net"],
        full_minus_adjusted_per_trade=(full["net"]-full["adjusted_net"])/full["trades"],
        printed_stop_points_per_NQ=1500/20,printed_target_points_per_NQ=800/20,
    )
    assert checks["annual_sum_matches_full"] and checks["annual2017_24_matches_IS"]
    assert round(checks["full_mean_exact"],2)==full["printed_average"]
    assert round(checks["IS_mean_exact"],2)==ins["printed_average"]
    assert checks["native_gross_difference"]==full["net"]
    assert checks["statistical_adjustment_matches_printed_cents"]
    return dict(source_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),
                visually_verified_pdf_pages=[3,4,5,6,7,8,9],native_page7_images_reviewed=2,
                full=full,in_sample=ins,out_of_sample=oos,annual=annual,native_screenshot=native,
                arithmetic=checks,new_strategy_return_trials=0,
                interpretations={
                    "adjusted_net":"Exactly reproduced by net-GP/sqrt(wins)-GL/sqrt(losses); no basis to infer fees from this difference.",
                    "split_gap":"The displayed intervals omitJan1-14,2025 and differ at2017start. If same version,7trades/-3530 net remain unallocated; not a proven mismatch.",
                    "calendar_gap":"Annual2025+2026 profit85145 is3530 below the Jan15,2025+OOS88675, consistent with omitted early2025 losses if definitions match.",
                    "drawdown":"Native MC explicitly labels16500 max close-to-closeDD, different from reported17420 maxDD; do not conflate definitions.",
                    "fill_gaps":"Largestwin4950 exceeds800target and largestloss2205 exceeds1500stop; favorable/adverse gap fills or other unspecified rules may explain this, not guaranteed brackets.",
                    "R2_exit":"For standard intercept OLS R2 in[0,1], threshold2 cannot trigger an R2 take-profit exit.",
                })


if __name__=="__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    result=audit()
    (OUT/"source_claims_audit.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result["arithmetic"],indent=2))
