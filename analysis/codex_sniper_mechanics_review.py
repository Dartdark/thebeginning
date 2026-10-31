"""Disconnected callback checks; no broker, price history, fills model or alpha test.

The algorithm/template and selected engine methods are loaded unchanged from
pinned public MIT-licensed files. Only transport/data objects are substituted.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "agents/codex/inputs/sniper_review_20261027/public_upstream"
UPSTREAM = "bee959dc464749f7cce66e766249ccdbb2d4869a"


class Direction(Enum):
    LONG = "long"
    SHORT = "short"


class Offset(Enum):
    NONE = "none"
    OPEN = "open"
    CLOSE = "close"


class OrderType(Enum):
    LIMIT = "limit"


@dataclass
class Tick:
    ask_price_1: float = 99.75
    ask_volume_1: float = 5
    bid_price_1: float = 99.5
    bid_volume_1: float = 5


@dataclass
class Trade:
    vt_orderid: str
    price: float
    volume: float


@dataclass
class Order:
    vt_orderid: str
    active: bool = True
    traded: float = 0
    gateway_name: str = "DISCONNECTED_FAKE"

    def is_active(self):
        return self.active

    def create_cancel_request(self):
        return SimpleNamespace(vt_orderid=self.vt_orderid)


def integer_rounding(volume, step):
    """Substitute helper, deliberately limited to integer test inputs."""
    assert step == 1 and volume == int(volume), (volume, step)
    return float(Decimal(str(volume)))


def class_node(filename, name):
    tree = ast.parse((SOURCE / filename).read_text())
    return next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)


def load_runtime():
    ns = dict(Enum=Enum, Direction=Direction, Offset=Offset, OrderType=OrderType,
              TickData=Tick, TradeData=Trade, OrderData=Order, Event=SimpleNamespace,
              ContractData=SimpleNamespace, OrderRequest=SimpleNamespace,
              CancelRequest=SimpleNamespace, APP_NAME="AlgoTrading",
              round_to=integer_rounding)
    for filename, name in [("base.py", "AlgoStatus"), ("template.py", "AlgoTemplate")]:
        code = ast.fix_missing_locations(ast.Module(body=[class_node(filename, name)], type_ignores=[]))
        exec(compile(code, str(SOURCE / filename), "exec"), ns)
    engine = class_node("engine.py", "AlgoEngine")
    methods = {"send_order", "cancel_order", "process_order_event", "process_trade_event"}
    body = [n for n in engine.body if isinstance(n, ast.FunctionDef) and n.name in methods]
    assert {n.name for n in body} == methods
    isolated = ast.ClassDef(name="AlgoEngine", bases=[], keywords=[], body=body, decorator_list=[])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[isolated], type_ignores=[])),
                 str(SOURCE / "engine.py"), "exec"), ns)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[class_node("sniper_algo.py", "SniperAlgo")],
                                                    type_ignores=[])),
                 str(SOURCE / "sniper_algo.py"), "exec"), ns)
    return ns


class FakeMain:
    def __init__(self):
        self.requests, self.cancels, self.orders = [], [], {}

    def get_contract(self, symbol):
        assert symbol == "REVIEW.TEST"
        return SimpleNamespace(symbol="REVIEW", exchange="TEST", min_volume=1,
                               gateway_name="DISCONNECTED_FAKE")

    def send_order(self, req, gateway):
        assert gateway == "DISCONNECTED_FAKE"
        oid = f"SIM.{len(self.requests) + 1}"
        self.orders[oid] = Order(oid)
        self.requests.append(dict(id=oid, direction=req.direction.value, offset=req.offset.value,
                                  limit=req.price, volume=req.volume, type=req.type.value))
        return oid

    def get_order(self, oid):
        return self.orders.get(oid)

    def cancel_order(self, req, gateway):
        assert gateway == "DISCONNECTED_FAKE"
        self.cancels.append(req.vt_orderid)


def run_checks():
    ns = load_runtime()
    rows = []

    def make(volume=5, direction=Direction.LONG, offset=Offset.OPEN, start=True):
        e = ns["AlgoEngine"]()
        e.main_engine = FakeMain()
        e.orderid_algo_map = {}
        e.logs, e.events = [], []
        e.write_log = lambda message, algo=None: e.logs.append(message)
        e.put_algo_event = lambda algo, data: e.events.append(data)
        a = ns["SniperAlgo"](e, "RESEARCH_ONLY", "REVIEW.TEST", direction, offset, 100, volume, {})
        if start:
            a.start()
        return a, e

    def ack(e, oid, active=True, traded=0):
        order = Order(oid, active=active, traded=traded)
        e.main_engine.orders[oid] = order
        e.process_order_event(SimpleNamespace(data=order))

    def fill(e, oid, volume):
        e.process_trade_event(SimpleNamespace(data=Trade(oid, 100, volume)))

    def save(name, a, e, note, category="behavior"):
        rows.append(dict(case=name, assertion_passed=True, category=category, observation=note,
                         traded=a.traded, target=a.volume, tracked_order=a.vt_orderid,
                         status=a.status.value, active_order_ids=list(a.active_orders),
                         requests=e.main_engine.requests.copy(), cancels=e.main_engine.cancels.copy()))

    a, e = make(start=False)
    a.update_tick(Tick())
    assert not e.main_engine.requests
    save("01_paused", a, e, "Template status gate blocks tick dispatch while paused.")

    a, e = make()
    a.update_tick(Tick(ask_price_1=100.25))
    assert not e.main_engine.requests
    save("02_unfavorable_buy", a, e, "Ask above buy cap produces no order.")

    a, e = make()
    a.update_tick(Tick(ask_volume_1=2))
    req = e.main_engine.requests[-1]
    assert req["volume"] == 2 and req["limit"] == 100 and req["type"] == "limit"
    save("03_buy_cap_and_size", a, e, "Two requested at caller limit 100; observed ask 99.75 is not a simulated fill.")

    a, e = make(direction=Direction.SHORT, offset=Offset.CLOSE)
    a.update_tick(Tick(bid_price_1=100.25, bid_volume_1=1))
    req = e.main_engine.requests[-1]
    assert req["volume"] == 1 and req["direction"] == "short" and req["offset"] == "close"
    save("04_sell_and_offset", a, e, "Bid depth caps sell size; CLOSE offset passes through.")

    a, e = make()
    a.update_tick(Tick()); ack(e, "SIM.1"); fill(e, "SIM.1", 2)
    assert a.traded == 2
    a.update_tick(Tick()); ack(e, "SIM.1", active=False, traded=2)
    a.update_tick(Tick(ask_volume_1=8))
    assert e.main_engine.requests[-1]["volume"] == 3
    save("05_partial_fill_remainder", a, e, "After trade callback and terminal acknowledgement, remaining quantity is three.")

    a, e = make(volume=2)
    a.update_tick(Tick()); ack(e, "SIM.1"); fill(e, "SIM.1", 2)
    assert a.status == ns["AlgoStatus"].FINISHED
    a.update_tick(Tick())
    assert len(e.main_engine.requests) == 1
    save("06_completion", a, e, "Inherited trade accounting precedes callback; completion suppresses new tick orders.")

    a, e = make()
    a.update_tick(Tick()); ack(e, "SIM.1")
    a.update_tick(Tick(ask_price_1=99.5))
    assert e.main_engine.cancels == ["SIM.1"] and len(e.main_engine.requests) == 1
    save("07_cancel_next_tick", a, e, "A favorable quote does not prevent the next-tick cancellation policy.")

    a, e = make()
    a.update_tick(Tick()); ack(e, "SIM.1")
    for _ in range(3):
        a.update_tick(Tick())
    assert e.main_engine.cancels == ["SIM.1"] * 3
    save("08_repeat_cancel", a, e, "Each new tick repeats cancellation while terminal acknowledgement is pending.")

    a, e = make()
    a.update_tick(Tick()); a.update_tick(Tick())
    assert a.vt_orderid == "SIM.1" and not a.active_orders and not e.main_engine.cancels
    assert len(e.main_engine.requests) == 1
    save("09_wait_for_ack", a, e, "Retained ID blocks resubmission; active_orders is empty until an order callback.")

    a, e = make()
    a.update_tick(Tick(ask_price_1=0, ask_volume_1=2))
    assert e.main_engine.requests[-1]["volume"] == 2
    save("10_invalid_zero_ask", a, e, "Zero ask with positive size triggers a gateway request at limit 100.", "safety_gap_demo")

    a, e = make()
    a.update_tick(Tick(ask_volume_1=0))
    assert not e.main_engine.requests and a.vt_orderid == ""
    save("11_zero_depth_guard", a, e, "Upstream engine rejects rounded zero volume before fake-gateway send.")

    a, e = make(volume=1)
    a.update_tick(Tick()); ack(e, "SIM.1"); ack(e, "SIM.1", active=False)
    a.update_tick(Tick()); ack(e, "SIM.2")
    ack(e, "SIM.1", active=False)
    assert a.vt_orderid == "" and "SIM.2" in a.active_orders
    a.update_tick(Tick()); ack(e, "SIM.3")
    assert set(a.active_orders) == {"SIM.2", "SIM.3"}
    save("12_delayed_old_terminal", a, e, "Old terminal event clears newer ID; two one-unit live children for target one.", "safety_gap_demo")

    a, e = make()
    a.update_tick(Tick()); ack(e, "SIM.1")
    ack(e, "SIM.1", active=False, traded=2)
    assert a.traded == 0
    a.update_tick(Tick()); ack(e, "SIM.2")
    assert e.main_engine.requests[-1]["volume"] == 5
    fill(e, "SIM.1", 2); fill(e, "SIM.2", 5)
    assert a.traded == 7 and a.volume == 5
    save("13_delayed_trade_overfill", a, e, "Delayed trade after known partial-fill cancellation permits seven filled against target five.", "safety_gap_demo")

    a, e = make()
    a.update_tick(Tick()); ack(e, "SIM.1")
    for _ in range(3):
        a.update_timer()
    assert not e.main_engine.cancels and a.status == ns["AlgoStatus"].RUNNING
    save("14_no_timer_deadline", a, e, "No timer-based expiry/flatten rule is supplied; an external controller is required.", "external_control_required")

    assert len(rows) == 14
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "analysis/outputs/codex_sniper_mechanics_20261027")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Refusing to overwrite an existing review output directory")
    rows = run_checks()
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCE.iterdir()) if p.is_file()}
    code_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    summary = dict(kind="synthetic mechanics only", upstream_commit=UPSTREAM,
                   preregistration="4b01fec", code_commit=code_sha,
                   assertions_completed=len(rows),
                   safety_gap_demonstrations=sum(r["category"] == "safety_gap_demo" for r in rows),
                   new_economic_evaluations=0, market_returns_examined=False,
                   gateway_connected=False, source_sha256=hashes,
                   limits=["No installed vn.py integration test", "Fake gateway and simplified data objects",
                           "Integer volume rounding helper only", "No queue, latency, fills, costs or P&L model",
                           "Stress cases are constructed, not observed historical events"])
    args.output.mkdir(parents=True)
    (args.output / "cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
