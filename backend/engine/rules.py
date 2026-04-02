def is_mobile_primary(conn, workload_id):
    row = conn.execute(
        """
        SELECT a.is_mobile_primary
        FROM workloads w
        JOIN verticals v ON v.id = w.vertical_id
        JOIN industries i ON i.id = v.industry_id
        JOIN archetypes a ON a.id = i.archetype_id
        WHERE w.id = ?
        """,
        (workload_id,),
    ).fetchone()
    if row is None:
        return False
    return bool(row["is_mobile_primary"])


def get_recommendations(conn, workload_id, scale_level):
    if is_mobile_primary(conn, workload_id):
        return None

    rows = conn.execute(
        """
        SELECT p.id, p.name, p.brand, p.form_factor, p.notes, stp.rank
        FROM products p
        JOIN scale_tier_products stp ON stp.product_id = p.id
        JOIN scale_tiers st ON st.id = stp.scale_tier_id
        WHERE st.workload_id = :workload_id
          AND st.scale_level = :scale_level
        ORDER BY stp.rank ASC
        """,
        {"workload_id": workload_id, "scale_level": scale_level},
    ).fetchall()

    return [dict(r) for r in rows]
