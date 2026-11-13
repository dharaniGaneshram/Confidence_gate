import json

from modules.input_handler import validate_highlighter_input
from modules.coverage_checker import check_coverage
from modules.margin_calculator import calculate_score_margin
from modules.self_checker import check_evidence_sufficiency
from modules.confidence_gate import assign_confidence
from modules.router import route_request
from modules.config_loader import load_config
from modules.output_generator import generate_output
from pathlib import Path
from datetime import datetime


# Temporary Solver for testing
def dummy_solver(question, context):

    print("\nSolver received the question:")
    print(question)

    print("\nSolver received the context:")
    print(context)

    return "Dummy answer generated for testing."


# Re-evaluate Confidence Gate after evidence expansion
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

# Temporary Highlighter widening function
def temporary_highlighter_widen(data):

    print("\nRequesting additional evidence from Highlighter...")

    # Temporary simulation only.
    # Replace with Member 1's actual widening function.
    return data


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

    # STEP 7: Load original full document
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
        solver=dummy_solver,
        original_data=validated_data,
        highlighter_widen=temporary_highlighter_widen,
        evaluate_gate=lambda data: evaluate_gate(data, config)
    )

    # Generate a unique log filename for every execution
    input_filename = Path(input_path).stem

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    log_filename = f"run_{input_filename}_{timestamp}"

    generate_output(
        confidence_result,
        router_result,
        margin_result,
        config["paths"]["output_folder"],
        question_id=log_filename
)
    # STEP 9: Final Router output
    print("\n========== FINAL ROUTER RESULT ==========")

    print("Route:", router_result["route"])
    print("Answer:", router_result["answer"])

    # Generate final JSON output

    final_output = generate_output(
        confidence_result=confidence_result,
        router_result=router_result,
        margin_result=margin_result,
        output_folder=config["paths"]["output_folder"],
        question_id="question_001"
    )

    if "final_confidence" in router_result:
        print("Final Confidence:", router_result["final_confidence"])

    if "widen_attempts" in router_result:
        print("Widen Attempts:", router_result["widen_attempts"])


if __name__ == "__main__":
    main()
