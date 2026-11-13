import json
import os


def generate_output(
    confidence_result,
    router_result,
    margin_result,
    output_folder,
    question_id="question_001"
):

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Combine Confidence Gate and Router results
    final_output = {
        "confidence_gate": {
            "confidence": confidence_result["confidence"],
            "signals": confidence_result["signals"],
            "score_margin": {
                "value": confidence_result["signals"]["margin"],
                "reliable": confidence_result["signals"]["margin_reliable"],
                "budget_hit": margin_result["budget_hit"],
                "reason": margin_result["reason"]
            },
            "reasons": confidence_result["reasons"]
        },

        "router": {
            "route": router_result["route"],
            "answer": router_result.get("answer"),
            "widen_attempts": router_result.get("widen_attempts", 0),
            "final_confidence": router_result.get(
                "final_confidence",
                confidence_result["confidence"]
            ),
            "context": router_result.get("context", ""),
            "notes": router_result.get("notes", "")
        }
    }

    # Generate output file path
    output_path = os.path.join(
        output_folder,
        f"{question_id}.json"
    )

    # Save JSON file
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            final_output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nJSON output generated successfully!")
    print("Output file:", output_path)

    return final_output