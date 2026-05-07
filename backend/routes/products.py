from flask import Blueprint, jsonify
from db import get_db

products_bp = Blueprint("products", __name__)


@products_bp.get("/products")
def products():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products ORDER BY id ASC")
        rows = cur.fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()
