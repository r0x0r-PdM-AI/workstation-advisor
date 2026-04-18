from flask import Blueprint, request, jsonify
from db import get_db
from engine.rules import get_recommendations, is_mobile_primary

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


@recommend_bp.get("/taxonomy")
def taxonomy():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, is_mobile_primary FROM archetypes ORDER BY id")
        archetypes = cur.fetchall()
        cur.execute("SELECT id, archetype_id, name FROM industries ORDER BY id")
        industries = cur.fetchall()
        cur.execute("SELECT id, industry_id, name FROM verticals ORDER BY id")
        verticals = cur.fetchall()
        cur.execute("SELECT id, vertical_id, name FROM workloads ORDER BY id")
        workloads = cur.fetchall()

        work_by_vertical = {}
        for w in workloads:
            work_by_vertical.setdefault(w["vertical_id"], []).append(
                {"id": w["id"], "name": w["name"]}
            )

        vert_by_industry = {}
        for v in verticals:
            vert_by_industry.setdefault(v["industry_id"], []).append(
                {
                    "id": v["id"],
                    "name": v["name"],
                    "workloads": work_by_vertical.get(v["id"], []),
                }
            )

        ind_by_archetype = {}
        for i in industries:
            ind_by_archetype.setdefault(i["archetype_id"], []).append(
                {
                    "id": i["id"],
                    "name": i["name"],
                    "verticals": vert_by_industry.get(i["id"], []),
                }
            )

        result = [
            {
                "id": a["id"],
                "name": a["name"],
                "is_mobile_primary": a["is_mobile_primary"],
                "industries": ind_by_archetype.get(a["id"], []),
            }
            for a in archetypes
        ]

        return jsonify(result), 200
    finally:
        conn.close()


@recommend_bp.get("/products")
def products():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products ORDER BY id ASC")
        rows = cur.fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()
