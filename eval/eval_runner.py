import sys
import os
import time
import json
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
from validator.cross_layer import validate_cross_layer
from validator.repair import validate_and_repair


REAL_PROMPTS = [
    "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
    "Create a task management app with projects, tasks, deadlines, and team members who can comment.",
    "Build an online bookstore with book listings, shopping cart, checkout, and order history.",
    "Make a fitness tracking app with workouts, progress charts, and a coach role who can assign plans.",
    "Build a hotel booking platform with room listings, reservations, guest reviews, and admin approval for new listings.",
]

EDGE_CASE_PROMPTS = [
    "Make an app.",  # vague
    "Build a chat app where messages are private but also fully public for moderation, and users can delete others' messages but also can't.",  # conflicting
    "I need something for my business.",  # underspecified
    "Build a social network with posts, likes, comments, follow system, direct messages, stories, live streaming, marketplace, and crypto payments.",  # overloaded/ambiguous scope
    "Build an app with users and stuff.",  # vague
]


def run_single(prompt: str) -> dict:
    start = time.time()
    log = []
    try:
        intent = extract_intent(prompt)
        design = design_system(intent.model_dump())
        schemas = generate_schemas(design.model_dump())

        errors_before = validate_cross_layer(schemas)
        schemas = validate_and_repair(schemas, log)
        errors_after = validate_cross_layer(schemas)

        elapsed = round(time.time() - start, 2)

        return {
            "prompt": prompt[:60] + ("..." if len(prompt) > 60 else ""),
            "success": len(errors_after) == 0,
            "errors_before_repair": len(errors_before),
            "errors_after_repair": len(errors_after),
            "repair_attempts": len([l for l in log if l.get("status") == "errors_found"]),
            "latency_seconds": elapsed,
            "assumptions_made": intent.assumptions,
            "failure_type": None if len(errors_after) == 0 else "unresolved_validation_errors",
        }
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return {
            "prompt": prompt[:60] + ("..." if len(prompt) > 60 else ""),
            "success": False,
            "errors_before_repair": None,
            "errors_after_repair": None,
            "repair_attempts": len(log),
            "latency_seconds": elapsed,
            "assumptions_made": [],
            "failure_type": f"exception: {type(e).__name__}: {str(e)[:100]}",
        }


def main():
    results = []

    print("=== REAL PROMPTS ===")
    for p in REAL_PROMPTS:
        print(f"Running: {p[:60]}...")
        r = run_single(p)
        r["category"] = "real"
        results.append(r)
        print(f"  -> success={r['success']}, latency={r['latency_seconds']}s, repairs={r['repair_attempts']}")

    print("\n=== EDGE CASES ===")
    for p in EDGE_CASE_PROMPTS:
        print(f"Running: {p[:60]}...")
        r = run_single(p)
        r["category"] = "edge_case"
        results.append(r)
        print(f"  -> success={r['success']}, latency={r['latency_seconds']}s, repairs={r['repair_attempts']}")

    # Summary metrics
    total = len(results)
    successes = sum(1 for r in results if r["success"])
    avg_latency = round(sum(r["latency_seconds"] for r in results) / total, 2)
    total_repairs = sum(r["repair_attempts"] for r in results)

    print("\n=== SUMMARY ===")
    print(f"Total runs: {total}")
    print(f"Success rate: {successes}/{total} ({round(successes/total*100,1)}%)")
    print(f"Average latency: {avg_latency}s")
    print(f"Total repair attempts triggered: {total_repairs}")

    # Save to CSV for the submission
    with open("eval/eval_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "category", "prompt", "success", "errors_before_repair", "errors_after_repair",
            "repair_attempts", "latency_seconds", "failure_type", "assumptions_made"
        ])
        writer.writeheader()
        for r in results:
            row = dict(r)
            row["assumptions_made"] = "; ".join(row["assumptions_made"]) if row["assumptions_made"] else ""
            writer.writerow(row)

    print("\n✅ Saved detailed results to eval/eval_results.csv")


if __name__ == "__main__":
    main()