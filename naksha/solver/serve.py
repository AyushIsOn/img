#!/usr/bin/env python3
"""A small HTTP front end so the iOS app can design what it actually scanned.

    python3 serve.py                      # binds 0.0.0.0:8000
    python3 serve.py --port 9000

Then set `solverEndpoint` in the app to http://<your-mac-ip>:8000

Endpoints
    GET  /health          liveness, and the local addresses to try
    POST /design          ScannedRoom[] plus RequirementSet in, design JSON out
    GET  /sample/2bhk     the bundled sample, handy for checking connectivity

Deliberately built on the standard library. This runs on a laptop on the same
Wi-Fi as the phone for a few minutes at a time, so a web framework and its
dependency tree would be cost without benefit. It is a development server and
is not intended to face the internet.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import traceback
import warnings
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

warnings.filterwarnings("ignore")

try:
    from naksha.design import bill_of_quantities, design_floor, maximum_demand, validate
    from naksha.ingest import design_from_request
    from naksha.plans import CATALOGUE
except ModuleNotFoundError as exc:
    # A missing dependency is the single most likely first run problem, and a
    # bare traceback does not tell you what to type. This does.
    print(f"\n  Missing dependency: {exc.name}\n")
    print("  The server needs networkx. Install it, from this folder:\n")
    print("      python3 -m pip install -r requirements.txt\n")
    print("  If pip refuses with 'externally-managed-environment', which")
    print("  Homebrew Python does, use a virtual environment instead:\n")
    print("      python3 -m venv .venv")
    print("      source .venv/bin/activate")
    print("      pip install -r requirements.txt\n")
    print("  Then run this again. Remember that a new terminal needs")
    print("  'source .venv/bin/activate' before python3 serve.py.\n")
    raise SystemExit(1)

MAX_BODY = 2 * 1024 * 1024      # a floor plan payload is kilobytes, not megabytes


def design_payload(d) -> dict:
    """The same shape run.py writes, so the app has one contract to decode."""
    return {
        "plan": {
            "name": d.plan.name,
            "ceiling_height": d.plan.ceiling_height,
            "rooms": [{"name": r.name, "kind": r.kind,
                       "polygon": [list(p) for p in r.polygon],
                       "area": round(r.area, 2)} for r in d.plan.rooms],
            "doors": [{"position": list(dr.position), "room_a": dr.room_a,
                       "room_b": dr.room_b, "width": dr.width,
                       "is_entry": dr.is_entry} for dr in d.plan.doors],
        },
        "board": list(d.board),
        "points": [{"id": p.id, "kind": p.kind, "room": p.room,
                    "xy": list(p.xy), "height": p.height, "watts": p.watts,
                    "label": p.label, "vguard_category": p.vguard_category}
                   for p in d.points],
        "circuits": [{"id": c.id, "kind": c.kind, "mcb_amps": c.mcb_amps,
                      "cable_mm2": c.cable_mm2,
                      "connected_watts": c.connected_watts,
                      "route_length_m": c.route_length,
                      "vdrop_percent": c.vdrop_percent,
                      "point_ids": [p.id for p in c.points],
                      "route_edges": [[list(u), list(v)]
                                      for u, v in c.route_edges]}
                     for c in d.circuits],
        "summary": {
            "floor_area_m2": round(d.plan.area, 2),
            "connected_load_w": d.connected_load,
            "maximum_demand_w": maximum_demand(d)["total"],
            "sanctioned_load_w": d.reqs.sanctioned_load_w,
            "conduit_m": d.total_route_length,
        },
        "checks": validate(d),
        "bill_of_quantities": bill_of_quantities(d),
    }


def local_addresses() -> list:
    """Best guess at the addresses the phone can reach, for the setup step."""
    out = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))       # no traffic sent, just picks a route
        out.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None,
                                       socket.AF_INET):
            ip = info[4][0]
            if ip not in out and not ip.startswith("127."):
                out.append(ip)
    except OSError:
        pass
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "naksha/0.1"

    # ------------------------------------------------------------- plumbing
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))

    # ------------------------------------------------------------------ GET
    def do_GET(self) -> None:
        if self.path.rstrip("/") in ("/health", ""):
            self._send(200, {"status": "ok",
                             "addresses": local_addresses(),
                             "plans": sorted(CATALOGUE)})
            return
        if self.path.startswith("/sample/"):
            key = self.path.rsplit("/", 1)[-1]
            if key not in CATALOGUE:
                self._send(404, {"error": f"unknown plan {key}",
                                 "available": sorted(CATALOGUE)})
                return
            mk_plan, mk_reqs = CATALOGUE[key]
            self._send(200, design_payload(design_floor(mk_plan(), mk_reqs())))
            return
        self._send(404, {"error": "not found",
                         "try": ["/health", "/design", "/sample/2bhk"]})

    # ----------------------------------------------------------------- POST
    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/design":
            self._send(404, {"error": "post to /design"})
            return

        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            self._send(400, {"error": "empty body"})
            return
        if length > MAX_BODY:
            self._send(413, {"error": "body too large"})
            return

        try:
            body = json.loads(self.rfile.read(length))
        except json.JSONDecodeError as exc:
            self._send(400, {"error": f"invalid JSON: {exc}"})
            return

        rooms = body.get("rooms") or []
        if not rooms:
            self._send(400, {"error": "no rooms supplied, scan or sketch at "
                                      "least one room first"})
            return

        try:
            design = design_from_request(body)
        except Exception as exc:                     # noqa: BLE001
            # A malformed scan should return a readable reason, not a stack
            # trace on the phone, but the trace still belongs in the log.
            traceback.print_exc()
            self._send(422, {"error": f"could not design this plan: {exc}"})
            return

        print(f"  designed {len(design.plan.rooms)} rooms, "
              f"{len(design.points)} points, {len(design.circuits)} circuits, "
              f"{design.total_route_length:.1f} m conduit")
        self._send(200, design_payload(design))


def main() -> None:
    ap = argparse.ArgumentParser(description="NAKSHA solver server")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    addrs = local_addresses()
    print()
    print("NAKSHA solver listening on port", args.port)
    print("-" * 58)
    if addrs:
        print("  Set solverEndpoint in the app to one of:")
        for a in addrs:
            print(f"    http://{a}:{args.port}")
    else:
        print("  Could not detect a LAN address. Find it with: ipconfig getifaddr en0")
    print()
    print("  Check from the Mac:  curl http://localhost:%d/health" % args.port)
    print("  The phone must be on the same Wi-Fi network.")
    print("-" * 58)
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
