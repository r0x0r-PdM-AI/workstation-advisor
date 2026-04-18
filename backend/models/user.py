from __future__ import annotations

from typing import Optional

from flask_login import UserMixin

from db import get_db


class User(UserMixin):
    def __init__(self, id: int, email: str, password_hash: str) -> None:
        self.id = id
        self.email = email
        self.password_hash = password_hash
        

    @staticmethod
    def get_by_id(user_id: int) -> Optional["User"]:
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, email, password_hash FROM users WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return User(
            id=row["id"],  # type: ignore[index]
            email=row["email"],  # type: ignore[index]
            password_hash=row["password_hash"],  # type: ignore[index]
        )

    @staticmethod
    def get_by_email(email: str) -> Optional["User"]:
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, email, password_hash FROM users WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return User(
            id=row["id"],  # type: ignore[index]
            email=row["email"],  # type: ignore[index]
            password_hash=row["password_hash"],  # type: ignore[index]
        )

    @staticmethod
    def create(email: str, password_hash: str) -> "User":
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, password_hash),
            )
            conn.commit()
            user_id = cur.fetchone()["id"]  # type: ignore[index]
        finally:
            conn.close()

        if user_id is None:
            raise RuntimeError("Failed to create user")

        user = User.get_by_id(user_id)
        if user is None:
            raise RuntimeError("Failed to load created user")

        return user
