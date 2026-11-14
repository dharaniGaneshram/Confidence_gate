
import json

from datetime import datetime
from modules.input_handler import validate_highlighter_input
from modules.coverage_checker import check_coverage
from modules.margin_calculator import calculate_score_margin
from modules.self_checker import check_evidence_sufficiency
from modules.confidence_gate import assign_confidence
from modules.router import route_request
from modules.config_loader import load_config
from modules.output_generator import generate_output


# -----------------------------------------
# TEMPORARY SOLVER FOR TESTING
# -----------------------------------------

def solver(route, question, context, document):

    print("\nSolver received the route:")
    print(route)

    print("\nSolver received the question:")
    print(question)

    print("\nSolver received the context:")
    print(context)

    print("\nSolver received the document:")
    print(document)

    # Temporary response matching the new Solver contract
    return {
        "status": "ok",
        "route_used": route,
        "answer": "Dummy answer generated for testing.",
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_time_s": 0
    }


# -----------------------------------------
# TEMPORARY CHECK FITS FOR TESTING
# -----------------------------------------

def check_fits(document, question, max_new_tokens, task):

    # Temporary implementation.
    # Replace with the actual check_fits from teammate's Solver.
    return True


# -----------------------------------------
# RE-EVALUATE CONFIDENCE AFTER EXPANSION
# -----------------------------------------

def evaluate_gate(data, config):

    coverage_result = check_coverage(
        data.question,
        data.selected_evidence
    )

    margin_result = calculate_score_margin(
        data.sentences,
        data.budget_hit
    )

    self_check_result = check_evidence_sufficiency(
        data.question,
        data.selected_evidence
    )

    return assign_confidence(
        coverage_result,
        margin_result,
        self_check_result,
        config
    )


# -----------------------------------------
# TEMPORARY HIGHLIGHTER WIDENING
# -----------------------------------------

def temporary_highlighter_widen(data):

    print("\nRequesting additional evidence from Highlighter...")

    # Temporary simulation only.
    # Replace with Member 1's actual widening function.

    return data


# -----------------------------------------
# MAIN
# -----------------------------------------

def main():

    # STEP 1: Load configuration

    config = load_config()

    print("Configuration loaded successfully!")

    print("\n========== CONFIDENCE-GATED EVIDENCE SHORTENING ==========\n")

    # STEP 2: Load Highlighter JSON

    print("1. INPUT VALIDATION")

    input_path = config["paths"]["input_file"]

    with open(input_path, "r", encoding="utf-8") as file:
        input_data = json.load(file)

    validated_data = validate_highlighter_input(input_data)

    print("Highlighter input validated successfully!")

    # STEP 3: Evidence Coverage

    print("\n2. EVIDENCE COVERAGE")

    coverage_result = check_coverage(
        validated_data.question,
        validated_data.selected_evidence
    )

    print("Coverage Score:", coverage_result["coverage_score"])
    print("Missing Words:", coverage_result["missing_words"])

    # STEP 4: Score Margin

    print("\n3. SCORE MARGIN")

    margin_result = calculate_score_margin(
        validated_data.sentences,
        validated_data.budget_hit
    )

    print("Score Margin:", margin_result["score_margin"])
    print("Reliable:", margin_result["reliable"])
    print("Reason:", margin_result["reason"])

    # STEP 5: LLM Self-Check

    print("\n4. LLM SELF-CHECK")

    self_check_result = check_evidence_sufficiency(
        validated_data.question,
        validated_data.selected_evidence
    )

    print("Classification:", self_check_result["self_check"])
    print("Reason:", self_check_result["reason"])

    # STEP 6: Confidence Gate

    print("\n5. CONFIDENCE GATE")

    confidence_result = assign_confidence(
        coverage_result,
        margin_result,
        self_check_result,
        config
    )

    print(
        "Final Confidence:",
        confidence_result["confidence"].upper()
    )

    print("\nReasons:")

    for reason in confidence_result["reasons"]:
        print("-", reason)

    # STEP 7: Load Full Document

    document_path = config["paths"]["document_file"]

    with open(document_path, "r", encoding="utf-8") as file:
        full_document = file.read()

    # STEP 8: Router

    print("\n6. ROUTER")

    router_result = route_request(
        confidence_result=confidence_result,
        question=validated_data.question,
        selected_evidence=validated_data.selected_evidence,
        full_document=full_document,
        solver=solver,
        check_fits=check_fits,
        max_new_tokens=config["solver"]["max_new_tokens"],
        original_data=validated_data,
        highlighter_widen=temporary_highlighter_widen,
        evaluate_gate=lambda data: evaluate_gate(data, config)
    )

    # STEP 9: Generate Unique Output Filename

    dataset_name = input_data.get(
    "dataset_name",
    config["router"]["default_dataset_name"]
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    log_filename = f"{dataset_name}_{timestamp}"

    generate_output(
        confidence_result,
        router_result,
        margin_result,
        config["paths"]["output_folder"],
        question_id=log_filename
    )

    # STEP 10: Display Final Result

    print("\n========== FINAL ROUTER RESULT ==========")

    print("Route:", router_result["route"])

    print("Answer:", router_result["answer"])

    if "final_confidence" in router_result:
        print("Final Confidence:", router_result["final_confidence"])

    if "widen_attempts" in router_result:
        print("Widen Attempts:", router_result["widen_attempts"])

    if "fallback" in router_result:
        print("Fallback:", router_result["fallback"])

    if "route_used" in router_result:
        print("Solver Route Used:", router_result["route_used"])

    if "total_input_tokens" in router_result:
        print("Input Tokens:", router_result["total_input_tokens"])

    if "total_output_tokens" in router_result:
        print("Output Tokens:", router_result["total_output_tokens"])

    if "total_time_s" in router_result:
        print("Solver Time:", router_result["total_time_s"])


if __name__ == "__main__":
    main()
