def assign_confidence(
    coverage_result,
    margin_result,
    self_check_result,
    config
):

    # Get values from input results
    coverage = coverage_result["coverage_score"]

    margin = margin_result["score_margin"]
    margin_reliable = margin_result["reliable"]

    self_check = self_check_result["self_check"]

    # Load thresholds from config.json
    coverage_thresholds = config["thresholds"]["coverage"]
    margin_thresholds = config["thresholds"]["margin"]

    VERY_LOW = coverage_thresholds["very_low"]
    MEDIUM = coverage_thresholds["medium"]
    HIGH = coverage_thresholds["high"]

    HIGH_MARGIN = margin_thresholds["high"]

    reasons = []

    # STEP 1: Handle LLM failure
    if self_check == "error":

        confidence = "low"

        reasons.append(
            "LLM self-check failed. High confidence cannot be assigned."
        )

    # STEP 2: Very Low Confidence
    elif coverage < VERY_LOW or (
        self_check == "insufficient" and coverage < MEDIUM
    ):

        confidence = "very_low"

        reasons.append(
            "Evidence coverage is very low or evidence is insufficient."
        )

    # STEP 3: High Confidence
    elif (
        coverage >= HIGH
        and self_check == "sufficient"
        and margin_reliable
        and margin is not None
        and margin >= HIGH_MARGIN
    ):

        confidence = "high"

        reasons.append(
            "Good coverage, sufficient evidence and clear score margin."
        )

    # STEP 4: Medium Confidence
    elif (
        coverage >= MEDIUM
        and self_check in ["sufficient", "partially_sufficient"]
        and (
            not margin_reliable
            or margin is None
            or margin >= 0
        )
    ):

        confidence = "medium"

        reasons.append(
            "Evidence is reasonably relevant but confidence is not high."
        )

    # STEP 5: Low Confidence
    else:

        confidence = "low"

        reasons.append(
            "Evidence coverage or sufficiency is not strong enough."
        )

    return {
        "confidence": confidence,

        "signals": {
            "coverage": coverage,
            "margin": margin,
            "margin_reliable": margin_reliable,
            "self_check": self_check
        },

        "reasons": reasons
    }