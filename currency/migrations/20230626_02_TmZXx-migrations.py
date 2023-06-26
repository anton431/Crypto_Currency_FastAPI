"""
currency table
users table
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS currency(
            id SERIAL PRIMARY KEY,
            name VARCHAR(3),
            price DECIMAL(8, 2),
            time TIMESTAMP
        )
        """,
        """
        DROP TABLE IF EXISTS currency;
        """,
    ),
step(
        """
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username VARCHAR(20),
            hashed_password VARCHAR(70),
            budget INT
        )
        """,
        """
        DROP TABLE IF EXISTS users;
        """,
    ),
]