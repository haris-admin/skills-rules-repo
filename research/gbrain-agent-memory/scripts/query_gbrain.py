#!/usr/bin/env python3
"""
Garry Tan GBrain Hybrid Retrieval & Memory Simulator CLI.
Demonstrates:
1. Lexical BM25 keyword search
2. Semantic vector search (simulated cosine similarity)
3. Reciprocal Rank Fusion (RRF) combining both rankings
4. Knowledge Graph link traversal for entity context
5. Dream Cycle overnight memory consolidation status
"""

import argparse
import json

SAMPLE_GBRAIN_INDEX = [
    {
        "id": "doc_001",
        "title": "Undispute Pre-Chargeback Network Specs",
        "entity": "Undispute",
        "tags": ["fintech", "disputes", "chargebacks", "visa", "mastercard"],
        "content": "Undispute resolves transactions in a 48h pre-chargeback grace window avoiding $35-$50 fees.",
        "bm25_score": 0.88,
        "semantic_score": 0.94,
        "linked_entities": ["TAPEase", "Visa CE 3.0", "Haris Habib"]
    },
    {
        "id": "doc_002",
        "title": "Simplifii-OS Cognitive Architecture & W3C COGA",
        "entity": "Simplifii-OS",
        "tags": ["neurodiversity", "adhd", "dyslexia", "coga", "accessibility"],
        "content": "Simplifii-OS uses trimodal UI, matte surfaces, and Pareto micro-steps for neurodivergent learners.",
        "bm25_score": 0.92,
        "semantic_score": 0.89,
        "linked_entities": ["Pareto Task Decomposer", "Haris Habib"]
    },
    {
        "id": "doc_003",
        "title": "AML Hive AUSTRAC Compliance Engine",
        "entity": "AML Hive",
        "tags": ["austrac", "compliance", "asic", "regtech", "pep"],
        "content": "Automated ASIC registry queries and PEP checks for Tranche 2 reporting entities.",
        "bm25_score": 0.75,
        "semantic_score": 0.82,
        "linked_entities": ["Haris Habib", "ASIC Register"]
    }
]

def reciprocal_rank_fusion(docs, k=60):
    """
    RRF Score = 1 / (k + rank_bm25) + 1 / (k + rank_semantic)
    Standard RRF algorithm used in GBrain.
    """
    # Sort by BM25
    bm25_sorted = sorted(docs, key=lambda x: x["bm25_score"], reverse=True)
    # Sort by Semantic
    semantic_sorted = sorted(docs, key=lambda x: x["semantic_score"], reverse=True)

    scores = {}
    for rank, doc in enumerate(bm25_sorted):
        doc_id = doc["id"]
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + (rank + 1)))

    for rank, doc in enumerate(semantic_sorted):
        doc_id = doc["id"]
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + (rank + 1)))

    fused = []
    for doc in docs:
        doc_copy = dict(doc)
        doc_copy["rrf_score"] = round(scores[doc["id"]], 5)
        fused.append(doc_copy)

    fused.sort(key=lambda x: x["rrf_score"], reverse=True)
    return fused

def main():
    parser = argparse.ArgumentParser(description="Garry Tan GBrain Hybrid Retrieval Simulator")
    parser.add_argument("--query", type=str, default="neurodivergent dispute resolution", help="Search query")
    parser.add_argument("--dream-cycle", action="store_true", help="Simulate overnight Dream Cycle consolidation")
    parser.add_argument("--demo", action="store_true", help="Run with demo index")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    if args.dream_cycle:
        dream_status = {
            "status": "Dream Cycle Active",
            "last_cycle_completed": "2026-09-17 03:15:00 AEST",
            "nodes_consolidated": 142,
            "edges_inferred": 38,
            "orphan_notes_linked": 6,
            "vector_index_vacuumed": True
        }
        if args.json:
            print(json.dumps(dream_status, indent=2))
        else:
            print("🌙 GBRAIN DREAM CYCLE REPORT")
            print("Status: Memory consolidated, knowledge graph updated.")
            print(f"Nodes Consolidated: {dream_status['nodes_consolidated']}")
            print(f"Edges Inferred:     {dream_status['edges_inferred']}")
        return

    results = reciprocal_rank_fusion(SAMPLE_GBRAIN_INDEX)

    if args.json:
        print(json.dumps({"query": args.query, "results": results}, indent=2))
        return

    print("=" * 80)
    print(f" 🧠 GBRAIN HYBRID RETRIEVAL (BM25 + pgvector + RRF)")
    print(f" Query: '{args.query}'")
    print("=" * 80)
    print(f"{'Rank':<5} | {'Doc Title':<36} | {'RRF Score':<10} | {'Entity':<14}")
    print("-" * 80)

    for idx, doc in enumerate(results, start=1):
        print(f" #{idx:<4} | {doc['title'][:34]:<36} | {doc['rrf_score']:<10} | {doc['entity']:<14}")
        print(f"        Linked Graph Entities: {', '.join(doc['linked_entities'])}")
        print(f"        Snippet: {doc['content']}")
        print("-" * 80)

    print("💡 MEMORY ARCHITECTURE: Garry Tan's GBrain balances lexical accuracy with semantic recall.")
    print("=" * 80)

if __name__ == "__main__":
    main()
