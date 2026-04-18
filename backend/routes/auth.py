from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from app import bcrypt
from models.user import User

from psycopg2 import errors as pg_errors

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
	data = request.get_json(silent=True) or {}
	email = data.get("email")
	password = data.get("password")

	if not email or not password:
		return jsonify({"error": "Email and password are required"}), 400

	if len(password) < 8:
		return jsonify({"error": "Password must be at least 8 characters"}), 400

	if User.get_by_email(email) is not None:
		return jsonify({"error": "Email already registered"}), 400

	password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
	try:
		User.create(email, password_hash)
	except pg_errors.UniqueViolation:
		return jsonify({"error": "Email already registered"}), 400
	return jsonify({"message": "User registered successfully"}), 201


@auth_bp.post("/login")
def login():
	data = request.get_json(silent=True) or {}
	email = data.get("email")
	password = data.get("password")

	if not email or not password:
		return jsonify({"error": "Email and password are required"}), 400

	user = User.get_by_email(email)
	if user is None or not bcrypt.check_password_hash(user.password_hash, password):
		return jsonify({"error": "Invalid email or password"}), 401

	login_user(user)
	return jsonify(
		{
			"message": "Logged in",
			"user": {"id": user.id, "email": user.email},
		}
	), 200


@auth_bp.post("/logout")
@login_required
def logout():
	logout_user()
	return jsonify({"message": "Logged out"}), 200


@auth_bp.get("/me")
@login_required
def me():
	return jsonify({"id": current_user.id, "email": current_user.email}), 200