def is_mobile_primary(conn, workload_id):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT a.is_mobile_primary
        FROM workloads w
        JOIN verticals v ON v.id = w.vertical_id
        JOIN industries i ON i.id = v.industry_id
        JOIN archetypes a ON a.id = i.archetype_id
        WHERE w.id = %s
        """,
        (workload_id,),
    )
    row = cur.fetchone()
    if row is None:
        return False
    return bool(row["is_mobile_primary"])


def get_recommendations(conn, workload_id, scale_level):
    if is_mobile_primary(conn, workload_id):
        return None

    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.id, p.name, p.brand, p.form_factor, p.notes, stp.rank
        FROM products p
        JOIN scale_tier_products stp ON stp.product_id = p.id
        JOIN scale_tiers st ON st.id = stp.scale_tier_id
        WHERE st.workload_id = %s
          AND st.scale_level = %s
        ORDER BY stp.rank ASC
        """,
        (workload_id, scale_level),
    )
    rows = cur.fetchall()

    return [dict(r) for r in rows]
