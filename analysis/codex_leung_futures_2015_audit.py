"""Deterministic formula checks for uploaded SSRN 2695405; no market-return test."""
from pathlib import Path
import hashlib
import json
import math


def xou_future(s, tau, q, theta_q, sigma):
    a = math.exp(-q * tau)
    return math.exp(a * math.log(s) + (1-a) * (theta_q-sigma*sigma/(2*q))
                    + sigma*sigma/(4*q)*(1-a*a))


def main():
    # Figure 4(b), p17: historical and pricing parameters are distinct.
    p, q, theta_p, theta_q, sigma, tau = 8.57, 4.08, 3.03, 3.06, 1.63, 66/252
    s = math.exp(3.1)  # declared synthetic spot, not an observed market print
    f = xou_future(s, tau, q, theta_q, sigma)
    threshold = (q*theta_q-p*theta_p)/(q-p)
    physical_drift = math.exp(-q*tau)*f*(p*(theta_p-math.log(s))-q*(theta_q-math.log(s)))
    # Independent finite-difference Ito check: time-to-maturity falls as time advances.
    h, dt = s*1e-4, 1e-5
    fs = (xou_future(s+h,tau,q,theta_q,sigma)-xou_future(s-h,tau,q,theta_q,sigma))/(2*h)
    fss = (xou_future(s+h,tau,q,theta_q,sigma)-2*f+xou_future(s-h,tau,q,theta_q,sigma))/(h*h)
    ft = -(xou_future(s,tau+dt,q,theta_q,sigma)-xou_future(s,tau-dt,q,theta_q,sigma))/(2*dt)
    ito_drift = ft + p*(theta_p-math.log(s))*s*fs + 0.5*sigma*sigma*s*s*fss
    assert math.isclose(physical_drift, ito_drift, abs_tol=1e-5)
    assert math.log(s) > threshold and physical_drift < 0
    # A futures curve priced under the same measure has zero undiscounted drift.
    same_measure_drift = math.exp(-q*tau)*f*(q*(theta_q-math.log(s))-q*(theta_q-math.log(s)))
    assert same_measure_drift == 0
    result = dict(scope="source formula and synthetic arithmetic only; no historical trading returns",
        source="SSRN 2695405, uploaded November 25 2015 version, pp6,13,17",
        source_pdf_sha256="dc5bd948d1eda42ac927d3e925ff9b7ee4d019e7d0266bfc4b214bc9a14acdae",
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        parameters=dict(mu_p=p,mu_q=q,theta_p=theta_p,theta_q=theta_q,sigma=sigma,tau=tau),
        synthetic_spot=s, log_spot=math.log(s), log_drift_threshold=threshold,
        eq_2_12_printed_greater_than_condition=True, actual_futures_drift=physical_drift,
        independent_finite_difference_ito_drift=ito_drift,
        interpretation="Eq2.12 greater-than direction needs mu_q>mu_p; it reverses for Figure4b parameters",
        same_measure_undiscounted_futures_drift=same_measure_drift,
        generator_notation="Objectives use historical P, but printed Eqs4.2-4.4 use pricing Q tilde drifts; numerical implementation unverified")
    out=Path("analysis/outputs/codex_leung_futures_2015")
    out.mkdir(parents=True,exist_ok=True)
    (out/"checks.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
