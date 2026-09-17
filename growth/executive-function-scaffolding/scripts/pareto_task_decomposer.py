#!/usr/bin/env python3
"""
Pareto Task Decomposer & Activation Energy Scaffolding CLI.
Breaks down overwhelming projects and assessment briefs into the 5 highest-mark-density
micro-steps (Pareto Steps) to overcome ADHD task paralysis.
"""

import argparse
import json

DECOMPOSITION_TEMPLATES = {
    "essay": [
        {"step": 1, "action": "Copy essay question into blank doc and bold key directive verbs (e.g. 'Critically analyse')", "est_minutes": 5, "dopamine_reward": "Micro-win: Canvas is no longer empty"},
        {"step": 2, "action": "Find 3 academic citations that support opposing sides of the argument", "est_minutes": 25, "dopamine_reward": "Evidence baseline established"},
        {"step": 3, "action": "Write 3 bullet points answering the prompt directly in plain conversational English", "est_minutes": 15, "dopamine_reward": "Core thesis locked"},
        {"step": 4, "action": "Draft 1 paragraph per bullet point incorporating 1 citation each", "est_minutes": 40, "dopamine_reward": "First rough draft complete"},
        {"step": 5, "action": "Read draft out loud once to fix awkward phrasing and check word count", "est_minutes": 15, "dopamine_reward": "Final polish achieved"}
    ],
    "startup_mvp": [
        {"step": 1, "action": "Write the 1-sentence value proposition and core customer profile in a markdown doc", "est_minutes": 10, "dopamine_reward": "Mission clarified"},
        {"step": 2, "action": "Create the simplest possible smoke test landing page with a single 'Join Waitlist' CTA", "est_minutes": 60, "dopamine_reward": "Live public link generated"},
        {"step": 3, "action": "Share landing page directly with 5 target prospects via LinkedIn or email", "est_minutes": 20, "dopamine_reward": "First outreach loop executed"},
        {"step": 4, "action": "Conduct 2 Mom-Test style discovery conversations with responding leads", "est_minutes": 45, "dopamine_reward": "Real customer qualitative signals collected"},
        {"step": 5, "action": "Calculate RAT scorecard and decide whether to write production code", "est_minutes": 15, "dopamine_reward": "Defensible investment decision made"}
    ],
    "generic": [
        {"step": 1, "action": "Create task folder and gather all raw input files in one place", "est_minutes": 5, "dopamine_reward": "Activation hurdle cleared"},
        {"step": 2, "action": "Identify the single highest-impact deliverable required by the deadline", "est_minutes": 10, "dopamine_reward": "Target locked"},
        {"step": 3, "action": "Complete a 15-minute rough sketch or bullet outline (zero self-editing allowed)", "est_minutes": 15, "dopamine_reward": "Skeleton created"},
        {"step": 4, "action": "Flesh out the central component until it works end-to-end", "est_minutes": 45, "dopamine_reward": "Core engine functioning"},
        {"step": 5, "action": "Review against rubric or criteria checklist and mark complete", "est_minutes": 15, "dopamine_reward": "Task officially finished"}
    ]
}

def decompose(task_title, category="generic"):
    steps = DECOMPOSITION_TEMPLATES.get(category, DECOMPOSITION_TEMPLATES["generic"])
    total_time = sum(s["est_minutes"] for s in steps)
    return {
        "task_title": task_title,
        "category": category,
        "total_estimated_minutes": total_time,
        "pareto_steps": steps
    }

def main():
    parser = argparse.ArgumentParser(description="Pareto Task Decomposer CLI for ADHD Executive Function")
    parser.add_argument("--task", type=str, default="Complete University Law Essay", help="Name or title of overwhelming project")
    parser.add_argument("--type", choices=["essay", "startup_mvp", "generic"], default="essay", help="Task archetype")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    result = decompose(args.task, args.type)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("=" * 80)
    print(f" ⚡ PARETO TASK DECOMPOSITION: {result['task_title']}")
    print(f" Total Estimated Focus Time: {result['total_estimated_minutes']} minutes (Split across 5 micro-steps)")
    print("=" * 80)

    for item in result["pareto_steps"]:
        print(f" [Step {item['step']}] ({item['est_minutes']} min) {item['action']}")
        print(f"          🎉 Dopamine Reward: {item['dopamine_reward']}")
        print("-" * 80)

    print("💡 STRATEGY: Do only Step 1 today. Once Step 1 is done, activation inertia is broken.")
    print("=" * 80)

if __name__ == "__main__":
    main()
