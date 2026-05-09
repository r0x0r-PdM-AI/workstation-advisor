import json
from typing import Any, cast

from flask import Blueprint, request, jsonify
from app import limiter
from db import get_db
from engine.rules import get_recommendations
from llm.client import call_llm
from llm.prompts import (
    build_extraction_system_prompt,
    build_reasoning_system_prompt,
    build_reasoning_user_message,
    format_taxonomy_for_prompt,
)

recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.post("/recommend")
def recommend():
    data = request.get_json(silent=True) or {}

    workload_id = data.get("workload_id")
    scale_level = data.get("scale_level")

    if workload_id is None or scale_level is None:
        return jsonify({"error": "workload_id and scale_level are required"}), 400

    if not isinstance(workload_id, int) or not isinstance(scale_level, int):
        return jsonify({"error": "workload_id and scale_level must be integers"}), 400

    if scale_level not in (1, 2, 3):
        return jsonify({"error": "scale_level must be 1, 2, or 3"}), 400

    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name FROM workloads WHERE id = %s", (workload_id,)
        )
        workload = cur.fetchone()
        if workload is None:
            return jsonify({"error": f"workload_id {workload_id} not found"}), 404

        cur.execute(
            "SELECT scale_label FROM scale_tiers WHERE workload_id = %s AND scale_level = %s",
            (workload_id, scale_level),
        )
        scale_tier = cur.fetchone()
        scale_label = scale_tier["scale_label"] if scale_tier else None

        results = get_recommendations(conn, workload_id, scale_level)

        if results is None:
            return jsonify({
                "workload": workload["name"],
                "scale_label": scale_label,
                "recommendations": [],
                "message": (
                    "Not Available — this workload requires a mobile workstation, "
                    "which is out of scope for v1.0."
                ),
            }), 200

        return jsonify({
            "workload": workload["name"],
            "scale_label": scale_label,
            "recommendations": [
                {
                    "rank": r["rank"],
                    "product": r["name"],
                    "brand": r["brand"],
                    "form_factor": r["form_factor"],
                    "notes": r["notes"],
                }
                for r in results
            ],
        }), 200
    finally:
        conn.close()


@recommend_bp.post("/recommend/natural")
@limiter.limit("3 per hour")
def recommend_natural():
    data = request.get_json(silent=True) or {}
    description = data.get("description")

    if description is None or not isinstance(description, str) or not description.strip():
        return jsonify({"error": "description is required"}), 400

    if len(description.strip()) < 20:
        return jsonify({"error": "Please describe your work in more detail"}), 400

    if len(description) > 2000:
        return jsonify({
            "error": "Description is too long. Please keep it under 2000 characters."
        }), 400

    conn = get_db()
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM workloads ORDER BY id")
        workloads = cur.fetchall()

        taxonomy_str = format_taxonomy_for_prompt(cast(list[dict[str, Any]], workloads))
        extraction_system_prompt = build_extraction_system_prompt(taxonomy_str)
        extraction_raw = call_llm(extraction_system_prompt, description.strip())

        try:
            extraction = json.loads(extraction_raw)
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse LLM response"}), 500

        if extraction.get("confidence") == "low":
            return jsonify({
                "error": (
                    "We could not match your description to a known workload. "
                    "Please be more specific about what you do and the scale you work at."
                )
            }), 400

        workload_id = extraction.get("workload_id")
        scale_level = extraction.get("scale_level")
        matched_workload_name = extraction.get("matched_workload_name", "")

        if not isinstance(workload_id, int) or not isinstance(scale_level, int):
            return jsonify({"error": "Failed to parse LLM response"}), 500

        results = get_recommendations(conn, workload_id, scale_level)
        if results is None:
            return jsonify({
                "matched_workload": matched_workload_name,
                "scale_level": scale_level,
                "recommendations": [],
                "message": (
                    "Not Available — this workload requires a mobile workstation, "
                    "which is out of scope for v1.0."
                ),
            }), 200
        if len(results) == 0:
            return jsonify({"error": "No products found for your workload profile"}), 404

        product_ids = [r["id"] for r in results]
        placeholders = ",".join(["%s"] * len(product_ids))
        cur.execute(
            f"SELECT id, name, max_cpu_cores, max_ram_gb, max_gpu_vram_gb, gpu_vram_range "
            f"FROM products WHERE id IN ({placeholders})",
            product_ids,
        )
        product_details = {row["id"]: row for row in cur.fetchall()}

        reasoning_products = [
            {
                "product_id": r["id"],
                "name": r["name"],
                "max_cpu_cores": product_details[r["id"]]["max_cpu_cores"] if r["id"] in product_details else None,
                "max_ram_gb": product_details[r["id"]]["max_ram_gb"] if r["id"] in product_details else None,
                "max_gpu_vram_gb": product_details[r["id"]]["max_gpu_vram_gb"] if r["id"] in product_details else None,
                "gpu_vram_range": product_details[r["id"]]["gpu_vram_range"] if r["id"] in product_details else None,
            }
            for r in results
        ]

        reasoning_user_message = build_reasoning_user_message(
            user_description=description.strip(),
            workload_name=matched_workload_name,
            scale_level=scale_level,
            products=reasoning_products,
        )
        reasoning_system_prompt = build_reasoning_system_prompt()

        reasoning_items = []
        try:
            reasoning_raw = call_llm(reasoning_system_prompt, reasoning_user_message)
            reasoning_parsed = json.loads(reasoning_raw)
            if isinstance(reasoning_parsed, dict):
                candidate = reasoning_parsed.get("reasoning", [])
                if isinstance(candidate, list):
                    reasoning_items = candidate
        except json.JSONDecodeError:
            reasoning_items = []

        explanations_by_product_id = {
            item.get("product_id"): item.get("explanation", "")
            for item in reasoning_items
            if isinstance(item, dict) and isinstance(item.get("product_id"), int)
        }

        return jsonify({
            "workload_id": workload_id,
            "matched_workload": matched_workload_name,
            "scale_level": scale_level,
            "recommendations": [
                {
                    "rank": r["rank"],
                    "product": r["name"],
                    "brand": r["brand"],
                    "form_factor": r["form_factor"],
                    "notes": r["notes"],
                    "explanation": explanations_by_product_id.get(r["id"], ""),
                }
                for r in results
            ],
        }), 200
    finally:
        if cur is not None:
            cur.close()
        conn.close()
