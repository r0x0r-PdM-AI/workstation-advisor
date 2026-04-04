from __future__ import annotations

from typing import Optional

from flask_login import UserMixin

from db import get_db


class User(UserMixin):
    def __init__(self, id: int, email: str, password_hash: str, created_at: str) -> None:
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def get_by_id(user_id: int) -> Optional["User"]:
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            created_at=row["created_at"],
        )

    @staticmethod
    def get_by_email(email: str) -> Optional["User"]:
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            created_at=row["created_at"],
        )

    @staticmethod
    def create(email: str, password_hash: str) -> "User":
        conn = get_db()
        try:
            cursor = conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash),
            )
            conn.commit()
            user_id = cursor.lastrowid
        finally:
            conn.close()

        if user_id is None:
            raise RuntimeError("Failed to create user")

        user = User.get_by_id(user_id)
        if user is None:
            raise RuntimeError("Failed to load created user")

        return user
