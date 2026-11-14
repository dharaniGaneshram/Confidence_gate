# -----------------------------------------
# SOLVER CALL HELPER
# -----------------------------------------

def call_solver(
    route,
    question,
    context,
    document,
    solver,
    check_fits,
    max_new_tokens
):

    # Check whether the input fits before calling Solver.

    fit_result = check_fits(
        document if route in ["full", "recite"] else context,
        question,
        max_new_tokens,
        route
    )

    if fit_result is not True:
        raise RuntimeError(
            f"Input does not fit for the {route} route. "
            "Check the actual check_fits implementation."
        )

    # Call Solver using the four-argument contract.

    solver_result = solver(
        route,
        question,
        context,
        document
    )

    if not isinstance(solver_result, dict):
        raise TypeError("Solver must return a dictionary.")

    status = solver_result.get("status")

    if status != "ok":
        raise RuntimeError(
            f"Solver failed. Status: {status}. "
            f"Details: {solver_result.get('error', 'No additional details')}"
        )

    return solver_result


# -----------------------------------------
# ROUTE 1: DIRECT
# -----------------------------------------

def direct_route(
    question,
    selected_evidence,
    solver,
    check_fits,
    full_document,
    max_new_tokens
):

    evidence_text = "\n".join(
        sentence.text for sentence in selected_evidence
    )

    solver_result = call_solver(
        "direct",
        question,
        evidence_text,
        full_document,
        solver,
        check_fits,
        max_new_tokens
    )

    return {
        "route": "direct",
        "answer": solver_result["answer"],
        "route_used": solver_result.get("route_used"),
        "total_input_tokens": solver_result.get("total_input_tokens"),
        "total_output_tokens": solver_result.get("total_output_tokens"),
        "total_time_s": solver_result.get("total_time_s"),
        "widen_attempts": 0
    }


# -----------------------------------------
# ROUTE 2: RECITE
# -----------------------------------------

def recite_route(
    question,
    selected_evidence,
    solver,
    check_fits,
    full_document,
    max_new_tokens
):

    evidence_text = "\n".join(
        sentence.text for sentence in selected_evidence
    )

    solver_result = call_solver(
        "recite",
        question,
        evidence_text,
        full_document,
        solver,
        check_fits,
        max_new_tokens
    )

    return {
        "route": "recite",
        "answer": solver_result["answer"],
        "route_used": solver_result.get("route_used"),
        "total_input_tokens": solver_result.get("total_input_tokens"),
        "total_output_tokens": solver_result.get("total_output_tokens"),
        "total_time_s": solver_result.get("total_time_s"),
        "fallback": solver_result.get("fallback"),
        "widen_attempts": 0
    }


# -----------------------------------------
# ROUTE 3: FULL DOCUMENT
# -----------------------------------------

def full_document_route(
    question,
    full_document,
    solver,
    check_fits,
    max_new_tokens
):

    solver_result = call_solver(
        "full",
        question,
        full_document,
        full_document,
        solver,
        check_fits,
        max_new_tokens
    )

    return {
        "route": "full",
        "answer": solver_result["answer"],
        "route_used": solver_result.get("route_used"),
        "total_input_tokens": solver_result.get("total_input_tokens"),
        "total_output_tokens": solver_result.get("total_output_tokens"),
        "total_time_s": solver_result.get("total_time_s"),
        "fallback": solver_result.get("fallback"),
        "widen_attempts": 0
    }


# -----------------------------------------
# ROUTE 4: MEDIUM CONFIDENCE EXPANSION
# -----------------------------------------

def handle_expansion(
    original_data,
    highlighter_widen,
    evaluate_gate,
    solver,
    check_fits,
    full_document,
    max_new_tokens
):

    # Ask Highlighter for additional evidence once.

    expanded_data = highlighter_widen(original_data)

    # Re-evaluate Confidence Gate.

    new_confidence_result = evaluate_gate(expanded_data)

    new_confidence = new_confidence_result["confidence"]

    selected_evidence = expanded_data.selected_evidence
    question = expanded_data.question

    print("\nConfidence after expansion:", new_confidence)

    if new_confidence == "high":

        result = direct_route(
            question,
            selected_evidence,
            solver,
            check_fits,
            full_document,
            max_new_tokens
        )

    elif new_confidence in ["medium", "low"]:

        result = recite_route(
            question,
            selected_evidence,
            solver,
            check_fits,
            full_document,
            max_new_tokens
        )

    elif new_confidence == "very_low":

        result = full_document_route(
            question,
            full_document,
            solver,
            check_fits,
            max_new_tokens
        )

    else:

        raise ValueError(
            f"Invalid confidence level: {new_confidence}"
        )

    result["widen_attempts"] = 1
    result["final_confidence"] = new_confidence

    return result


# -----------------------------------------
# MAIN ROUTER
# -----------------------------------------

def route_request(
    confidence_result,
    question,
    selected_evidence,
    full_document,
    solver,
    check_fits,
    max_new_tokens,
    original_data=None,
    highlighter_widen=None,
    evaluate_gate=None
):

    confidence = confidence_result["confidence"]

    if confidence == "high":

        print("Route: DIRECT")

        return direct_route(
            question,
            selected_evidence,
            solver,
            check_fits,
            full_document,
            max_new_tokens
        )

    elif confidence == "medium":

        print("Route: EXPAND")

        if (
            highlighter_widen is None
            or evaluate_gate is None
            or original_data is None
        ):

            raise ValueError(
                "Original data, Highlighter widening "
                "and Gate evaluation functions are required."
            )

        return handle_expansion(
            original_data,
            highlighter_widen,
            evaluate_gate,
            solver,
            check_fits,
            full_document,
            max_new_tokens
        )

    elif confidence == "low":

        print("Route: RECITE")

        return recite_route(
            question,
            selected_evidence,
            solver,
            check_fits,
            full_document,
            max_new_tokens
        )

    elif confidence == "very_low":

        print("Route: FULL")

        return full_document_route(
            question,
            full_document,
            solver,
            check_fits,
            max_new_tokens
        )

    else:

        raise ValueError(
            f"Unknown confidence level: {confidence}"
        )