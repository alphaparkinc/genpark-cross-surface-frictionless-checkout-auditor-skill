# -*- coding: utf-8 -*-
"""
Glance Cross-Surface Frictionless Checkout Auditor MCP Server
Exposes cross-surface conversion auditing tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GlanceCrossSurfaceFrictionlessCheckoutAuditor

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "glance-cross-surface-frictionless-checkout-auditor", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "audit_cross_surface_journey",
                        "description": "Audits and optimizes the zero-hop conversion journey across Screen Zero lock screens, smart TVs, and instant checkout.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "session_token": {"type": "string"},
                                "touchpoint_sequence": {"type": "array", "items": {"type": "string"}},
                                "surface_latencies_ms": {"type": "object"}
                            },
                            "required": ["session_id", "touchpoint_sequence"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "audit_cross_surface_journey":
            auditor = GlanceCrossSurfaceFrictionlessCheckoutAuditor()
            token = args.get("session_token")
            session_id = args.get("session_id", "GLANCE-SESS-001")
            if not token:
                token = auditor.generate_session_token(session_id)

            res = auditor.audit_cross_surface_journey(
                session_id=session_id,
                session_token=token,
                touchpoint_sequence=args.get("touchpoint_sequence", ["SCREEN_ZERO_GLANCE", "INTERACTIVE_TRAY", "PRODUCT_DETAIL", "1TAP_CHECKOUT"]),
                surface_latencies_ms=args.get("surface_latencies_ms")
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        auditor = GlanceCrossSurfaceFrictionlessCheckoutAuditor()
        tok = auditor.generate_session_token("TEST-SESS")
        test_res = auditor.audit_cross_surface_journey("TEST-SESS", tok, ["SCREEN_ZERO_GLANCE", "1TAP_CHECKOUT"])
        print(f"Test Conversion: {test_res['net_conversion_probability_pct']}%")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
