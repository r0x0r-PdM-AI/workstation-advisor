from flask import Blueprint, jsonify
from db import get_db

taxonomy_bp = Blueprint("taxonomy", __name__)


@taxonomy_bp.get("/taxonomy")
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
