# -*- coding: utf-8 -*-
"""
Example usage of GlanceCrossSurfaceFrictionlessCheckoutAuditor
Demonstrates end-to-end multi-surface audit from lock screen to 1-tap buy.
"""

from client import GlanceCrossSurfaceFrictionlessCheckoutAuditor

def main():
    auditor = GlanceCrossSurfaceFrictionlessCheckoutAuditor()

    sess_a = "SESS-MBL-88219"
    tok_a = auditor.generate_session_token(sess_a)

    sess_b = "SESS-TV-44109"
    tok_b = auditor.generate_session_token(sess_b)

    scenarios = [
        {
            "name": "Flow 1: Ultra-Fast Screen Zero to Instant 1-Tap Buy",
            "session_id": sess_a,
            "token": tok_a,
            "path": ["SCREEN_ZERO_GLANCE", "INTERACTIVE_TRAY", "1TAP_CHECKOUT"],
            "latencies": {"wake_to_tray_ms": 280.0, "tray_to_buy_ms": 410.0}
        },
        {
            "name": "Flow 2: High-Latency Cross-Device Mirror (Lock Screen to Smart TV)",
            "session_id": sess_b,
            "token": tok_b,
            "path": ["SCREEN_ZERO_GLANCE", "SMART_TV_MIRROR", "PRODUCT_DETAIL", "1TAP_CHECKOUT"],
            "latencies": {"glance_to_tv_ms": 2100.0, "tv_to_phone_ms": 1850.0, "detail_to_buy_ms": 950.0}
        }
    ]

    print("================================================================")
    print("Glance Cross-Surface Frictionless Checkout Auditor - Live Runs")
    print("================================================================\n")

    for sc in scenarios:
        res = auditor.audit_cross_surface_journey(
            session_id=sc["session_id"],
            session_token=sc["token"],
            touchpoint_sequence=sc["path"],
            surface_latencies_ms=sc["latencies"]
        )
        print(f"[{sc['name']}]")
        print(f"  Session ID             : {res['session_id']} (HMAC Verified: {res['session_integrity_verified']})")
        print(f"  Conversion Probability : {res['net_conversion_probability_pct']}% ({res['conversion_health_grade']})")
        print(f"  Handoff Latency Penalty: -{res['latency_friction_penalty_pct']}% (Total: {res['total_journey_latency_ms']}ms)")
        print("  Touchpoint Attribution Weights:")
        for tp, wt in res["touchpoint_attribution_weights_pct"].items():
            print(f"    * {tp:<24} : {wt}%")
        if res["identified_funnel_bottlenecks"]:
            print("  Friction Points Detected:")
            for bn in res["identified_funnel_bottlenecks"]:
                print(f"    ! {bn['from_surface']} -> {bn['to_surface']} ({bn['transition_rate_pct']}% rate) : {bn['friction_verdict']}")
        print()

if __name__ == "__main__":
    main()
