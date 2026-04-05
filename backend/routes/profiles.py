from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from db import get_db


profiles_bp = Blueprint("profiles", __name__)


@profiles_bp.post("/profiles")
@login_required
def create_profile():
	data = request.get_json(silent=True) or {}
	name = data.get("name")
	workload_id = data.get("workload_id")
	scale_level = data.get("scale_level")

	if name is None or workload_id is None or scale_level is None:
		return jsonify({"error": "Name, workload_id, and scale_level are required"}), 400

	if scale_level not in (1, 2, 3):
		return jsonify({"error": "scale_level must be 1, 2, or 3"}), 400

	conn = get_db()
	try:
		workload = conn.execute(
			"SELECT id FROM workloads WHERE id = ?",
			(workload_id,),
		).fetchone()
		if workload is None:
			return jsonify({"error": "Workload not found"}), 404

		cursor = conn.execute(
			(
				"INSERT INTO saved_profiles (user_id, name, workload_id, scale_level) "
				"VALUES (?, ?, ?, ?)"
			),
			(current_user.id, name, workload_id, scale_level),
		)
		conn.commit()

		profile = conn.execute(
			(
				"SELECT id, name, workload_id, scale_level, created_at "
				"FROM saved_profiles WHERE id = ?"
			),
			(cursor.lastrowid,),
		).fetchone()
	finally:
		conn.close()

	return jsonify(
		{
			"id": profile["id"],
			"name": profile["name"],
			"workload_id": profile["workload_id"],
			"scale_level": profile["scale_level"],
			"created_at": profile["created_at"],
		}
	), 201


@profiles_bp.get("/profiles")
@login_required
def list_profiles():
	conn = get_db()
	try:
		rows = conn.execute(
			(
				"SELECT sp.id, sp.name, sp.workload_id, w.name AS workload_name, "
				"sp.scale_level, st.scale_label, sp.created_at "
				"FROM saved_profiles sp "
				"JOIN workloads w ON sp.workload_id = w.id "
				"JOIN scale_tiers st ON st.workload_id = sp.workload_id "
				"AND st.scale_level = sp.scale_level "
				"WHERE sp.user_id = ? "
				"ORDER BY sp.created_at DESC"
			),
			(current_user.id,),
		).fetchall()
	finally:
		conn.close()

	profiles = [
		{
			"id": row["id"],
			"name": row["name"],
			"workload_id": row["workload_id"],
			"workload_name": row["workload_name"],
			"scale_level": row["scale_level"],
			"scale_label": row["scale_label"],
			"created_at": row["created_at"],
		}
		for row in rows
	]
	return jsonify(profiles), 200