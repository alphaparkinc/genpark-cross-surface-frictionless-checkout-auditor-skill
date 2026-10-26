# -*- coding: utf-8 -*-
"""
Glance Cross-Surface Frictionless Checkout Auditor Client
Audits and optimizes the zero-hop conversion journey across Screen Zero lock screens, smart TVs, and instant checkout.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
import hashlib
import hmac
from typing import Dict, Any, List

class GlanceCrossSurfaceFrictionlessCheckoutAuditor:
    """
    Audits cross-device handoffs between smartphone lock screens and ambient TV screens,
    computing Markov Multi-Touch Attribution (MTA) and latency drop-off penalties.
    """

    DEFAULT_BASE_TRANSITIONS = {
        "SCREEN_ZERO_GLANCE": {"INTERACTIVE_TRAY": 0.42, "SMART_TV_MIRROR": 0.18, "DROPOFF": 0.40},
        "INTERACTIVE_TRAY": {"PRODUCT_DETAIL": 0.65, "1TAP_CHECKOUT": 0.20, "DROPOFF": 0.15},
        "SMART_TV_MIRROR": {"1TAP_CHECKOUT": 0.35, "PRODUCT_DETAIL": 0.40, "DROPOFF": 0.25},
        "PRODUCT_DETAIL": {"1TAP_CHECKOUT": 0.72, "DROPOFF": 0.28},
        "1TAP_CHECKOUT": {"CONVERSION": 0.88, "DROPOFF": 0.12}
    }

    def __init__(self, latency_decay_hazard: float = 0.00045, secret_key: str = "GlanceSecretAuditKey2026"):
        self.hazard = latency_decay_hazard
        self.secret = secret_key.encode("utf-8")

    def verify_session_hmac(self, session_id: str, client_token: str) -> bool:
        """Verifies session integrity token generated across OEM hardware boundary."""
        expected = hmac.new(self.secret, session_id.encode("utf-8"), hashlib.sha256).hexdigest()[:16]
        return hmac.compare_digest(expected, client_token)

    def generate_session_token(self, session_id: str) -> str:
        """Generates HMAC token for cross-surface handoff authentication."""
        return hmac.new(self.secret, session_id.encode("utf-8"), hashlib.sha256).hexdigest()[:16]

    def calculate_handoff_latency_penalty(self, latencies_ms: Dict[str, float]) -> float:
        """
        Calculates conversion probability decay as handoff latency grows.
        Returns penalty factor between 0.0 (no penalty) and 0.60 (severe drop).
        """
        total_latency = sum(latencies_ms.values())
        # Exponential hazard decay
        survival = math.exp(-self.hazard * max(0.0, total_latency - 1200.0))
        return round(max(0.0, min(0.60, 1.0 - survival)), 3)

    def calculate_markov_attribution(self, observed_path: List[str]) -> Dict[str, float]:
        """
        Computes heuristic removal effect attribution for the observed sequence of touchpoints.
        """
        if not observed_path:
            return {}

        weights = {}
        total_touchpoints = len(observed_path)
        for idx, touchpoint in enumerate(observed_path):
            # Positional U-shaped attribution with heavy weighting on initial glance (discovery) and final 1-tap checkout
            if idx == 0:
                pos_weight = 0.35
            elif idx == total_touchpoints - 1:
                pos_weight = 0.40
            else:
                pos_weight = 0.25 / max(1, total_touchpoints - 2)
            weights[touchpoint] = weights.get(touchpoint, 0.0) + pos_weight

        # Normalize to 100%
        sum_w = sum(weights.values())
        return {k: round((v / sum_w) * 100.0, 1) for k, v in weights.items()}

    def audit_cross_surface_journey(
        self,
        session_id: str,
        session_token: str,
        touchpoint_sequence: List[str],
        surface_latencies_ms: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Audits full cross-surface session for conversion efficiency, latency friction, and attribution.
        """
        if surface_latencies_ms is None:
            surface_latencies_ms = {
                "screen_zero_to_tray_ms": 350.0,
                "tray_to_detail_ms": 820.0,
                "detail_to_checkout_ms": 640.0
            }

        is_valid = self.verify_session_hmac(session_id, session_token)
        latency_penalty = self.calculate_handoff_latency_penalty(surface_latencies_ms)
        attribution = self.calculate_markov_attribution(touchpoint_sequence)

        # Baseline end-to-end conversion calculation
        current_prob = 1.0
        bottlenecks = []
        for i in range(len(touchpoint_sequence) - 1):
            curr_step = touchpoint_sequence[i]
            next_step = touchpoint_sequence[i + 1]
            t_map = self.DEFAULT_BASE_TRANSITIONS.get(curr_step, {})
            p_trans = t_map.get(next_step, 0.5)
            current_prob *= p_trans

            if p_trans < 0.45:
                bottlenecks.append({
                    "from_surface": curr_step,
                    "to_surface": next_step,
                    "transition_rate_pct": round(p_trans * 100.0, 1),
                    "friction_verdict": "HIGH_DROPOFF_RISK"
                })

        adjusted_conversion = round(max(0.1, current_prob * (1.0 - latency_penalty)) * 100.0, 2)

        return {
            "session_id": session_id,
            "session_integrity_verified": is_valid,
            "net_conversion_probability_pct": adjusted_conversion,
            "latency_friction_penalty_pct": round(latency_penalty * 100.0, 1),
            "total_journey_latency_ms": sum(surface_latencies_ms.values()),
            "conversion_health_grade": "OPTIMIZED_ZERO_HOP" if adjusted_conversion >= 15.0 else ("FRICTION_DETECTED" if adjusted_conversion >= 8.0 else "POOR_EXPERIENCE"),
            "touchpoint_attribution_weights_pct": attribution,
            "identified_funnel_bottlenecks": bottlenecks
        }
