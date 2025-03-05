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

        raise Exception("Database error occurred during check registration after multiple attempts")

    async def fetchrow_user_data(self, user_id):
        """Retrieves user data"""
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

        raise Exception(f"Database error occurred during fetchrow user data after multiple attempts")

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
        """Updates user's last activity"""
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
        """Updates user full name"""
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
        """Updates user gender"""
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

    async def fetch_measurement_dates(self, user_id):
        """Retrieves dates of blood pressure measurements"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    query = """SELECT DISTINCT measurement_time::DATE as dates
FROM blood_pressure
WHERE user_id = $1
ORDER BY dates DESC
"""

                    measurement_dates = await conn.fetch(query, user_id)

                    return measurement_dates
                except Exception:
                    continue

        raise Exception("Database error occurred during fetch measurement dates after multiple attempts")

    async def fetch_bp_entries_for_day(self, date, user_id):
        """Retrieves blood pressure entries for day"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    query = """SELECT systolic_pressure, diastolic_pressure, pulse, remark, measurement_time 
FROM blood_pressure WHERE measurement_time::DATE = $1 AND user_id = $2"""

                    bp_entries = await conn.fetch(query, date, user_id)

                    return bp_entries
                except Exception:
                    continue

        raise Exception("Database error occurred during fetch blood pressure entries for day after multiple attempts")

    async def create_bp_entry(self, user_id, systolic_pressure, diastolic_pressure, pulse, remark):
        """Creates entry in blood pressure entries"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = """INSERT INTO blood_pressure 
(user_id, systolic_pressure, diastolic_pressure, pulse, remark) VALUES ($1, $2, $3, $4, $5)"""

                        await conn.execute(query, user_id, systolic_pressure, diastolic_pressure, pulse, remark)

                        return
                except Exception:
                    continue

        raise Exception("Database error occurred during create entry "
                        "in blood pressure entries after multiple attempts")

    async def fetch_bp_entries_for_period(self, start_date, final_date, user_id):
        """Retrieves blood pressure entries for period"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    query = """SELECT systolic_pressure, diastolic_pressure, pulse, remark, measurement_time 
FROM blood_pressure WHERE measurement_time BETWEEN $1 AND $2 AND user_id = $3"""

                    bp_entries = await conn.fetch(query, start_date, final_date, user_id)

                    return bp_entries
                except Exception:
                    continue

        raise Exception("Database error occurred during fetch blood pressure entries "
                        "for period after multiple attempts")

    async def count_bp_entries(self, user_id):
        """Counts blood pressure entries"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    query = "SELECT COUNT(user_id) FROM blood_pressure WHERE user_id = $1"

                    amount = await conn.fetchrow(query, user_id)

                    return amount
                except Exception:
                    continue

        raise Exception("Database error occurred during count blood pressure entries after multiple attempts")

    async def create_reminder(self, reminder_id, reminder_type, reminder_text, parameters, user_id):
        """Creates reminder in reminders"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = """INSERT INTO reminders 
(reminder_id, reminder_type, reminder_text, parameters, user_id) VALUES ($1, $2, $3, $4, $5)"""

                        await conn.execute(query, reminder_id, reminder_type, reminder_text, parameters, user_id)

                        return True
                except Exception:
                    continue

        raise Exception("Database error occurred during create reminder in reminders after multiple attempts")

    async def fetch_reminders(self, user_id):
        """Retrieves reminders"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    query = """SELECT reminder_id, reminder_type, reminder_text, parameters 
FROM reminders WHERE user_id = $1"""

                    reminders = await conn.fetch(query, user_id)

                    return reminders
                except Exception:
                    continue

        raise Exception("Database error occurred during fetch reminders after multiple attempts")

    async def create_note(self, user_id, note_text):
        """Creates note in notes"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = "INSERT INTO notes (user_id, note_text) VALUES ($1, $2)"

                        await conn.execute(query, user_id, note_text)

                        return True
                except Exception:
                    continue

        raise Exception("Database error occurred during create note in notes after multiple attempts")

    async def fetch_notes(self, user_id):
        """Retrieves notes"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    query = "SELECT note_id, note_text FROM notes WHERE user_id = $1"

                    notes = await conn.fetch(query, user_id)

                    return notes
                except Exception:
                    continue

        raise Exception("Database error occurred during fetch notes after multiple attempts")

    async def delete_note(self, note_id):
        """Deletes note in notes"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = "DELETE FROM notes WHERE note_id = $1"

                        await conn.execute(query, note_id)

                        return
                except Exception:
                    continue

        raise Exception("Database error occurred during delete note in notes after multiple attempts")

    async def update_reminders_number(self, user_id):
        """Updates reminders number"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = """UPDATE users SET reminders_number = 
(SELECT COUNT(reminder_id) FROM reminders WHERE user_id = $1) WHERE user_id = $1"""

                        await conn.execute(query, user_id)

                        return
                except Exception:
                    continue

        raise Exception(f"Database error occurred during update reminders number after multiple attempts")

    async def update_notes_number(self, user_id):
        """Updates notes number"""
        async with self.db_pool.acquire() as conn:
            for attempt in range(self.attempts):
                try:
                    async with conn.transaction():
                        query = """UPDATE users SET notes_number = 
(SELECT COUNT(note_id) FROM notes WHERE user_id = $1) WHERE user_id = $1"""

                        await conn.execute(query, user_id)

                        return
                except Exception:
                    continue

        raise Exception(f"Database error occurred during update notes number after multiple attempts")

    async def close_connections(self):
        """Close all connections"""
        if self.db_pool:
            await self.db_pool.close()


# Database initialization
db = Database()
