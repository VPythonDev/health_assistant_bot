import os

import asyncpg


class Database:
    attempts = 3

    def __init__(self):
        # Pool of connections
        self.db_pool = None

    async def init_pool(self):
        # Pool of connections
        dsn = os.getenv("dsn")  # Строка подключения (DSN)
        self.db_pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5)

    async def check_registration(self, user_id):
        """Check user in DB"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    query = "SELECT * FROM users WHERE user_id = $1"

                    user_data = await conn.fetchrow(query, user_id)

                    if user_data:
                        return True
                    else:
                        return False

                except Exception:
                    continue

        raise Exception("Database error occurred during registration check after multiple attempts")

    async def get_user_data(self, user_id):
        """Get user data"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    query = "SELECT full_name, gender, reminders_number, notes_number FROM users WHERE user_id = $1"

                    user_data = await conn.fetchrow(query, user_id)

                    full_name = user_data["full_name"]
                    gender = user_data["gender"]
                    reminders_number = user_data["reminders_number"]
                    notes_number = user_data["notes_number"]

                    return full_name, gender, reminders_number, notes_number
                except Exception:
                    continue

        raise Exception(f"Database error occurred during get user data after multiple attempts")

    async def registration(self, user_id, full_name=None, gender=None):
        """Registration new user"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = "INSERT INTO users (user_id, full_name, gender) VALUES ($1, $2, $3)"
                        await conn.execute(query, user_id, full_name, gender)

                        return True
                except Exception:
                    continue

        return False

    async def update_last_activity(self, user_id):
        """Update user's last activity"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = "UPDATE users SET last_activity = NOW() WHERE user_id = $1"
                        await conn.execute(query, user_id)
                        return
                except Exception:
                    continue

    async def update_user_full_name(self, user_id, new_name):
        """Update user full name"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = "UPDATE users SET full_name = $1 WHERE user_id = $2"
                        await conn.execute(query, new_name, user_id)
                        return
                except Exception:
                    continue

        raise Exception(f"Database error occurred during update user full name after multiple attempts")

    async def update_gender(self, user_id, new_gender):
        """Update user gender"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = "UPDATE users SET gender = $1 WHERE user_id = $2"
                        await conn.execute(query, new_gender, user_id)
                        return
                except Exception:
                    continue

        raise Exception(f"Database error occurred during update gender after multiple attempts")

    async def anonymization(self, user_id):
        """User anonymization"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = "UPDATE users SET full_name = NULL, gender = NULL WHERE user_id = $1"
                        await conn.execute(query, user_id)
                        return
                except Exception:
                    continue

        raise Exception(f"Database error occurred during anonymization after multiple attempts")

    async def deanonymization(self, user_id, name):
        """User deanonymization"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = "UPDATE users SET full_name = $1, gender = 'Do not specify' WHERE user_id = $2"
                        await conn.execute(query, name, user_id)
                        return
                except Exception:
                    continue

        raise Exception(f"Database error occurred during deanonymization after multiple attempts")

    async def close_connections(self):
        """Close all connections"""
        if self.db_pool:
            await self.db_pool.close()


db = Database()
