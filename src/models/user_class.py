class User:
    users = {}

    def __init__(self, user_id, full_name=None, gender=None):
        self.user_id = user_id
        self.full_name = full_name
        self.gender = gender

        # Добавляем переменные для хранения дат
        self.measurement_dates = []  # Список уникальных дат
        self.current_day_index = 0  # Текущий индекс в списке дат

        self.users[user_id] = self

    @classmethod
    def get_user(cls, user_id):
        """Get user form users"""
        return cls.users.get(user_id)

    def translate_gender(self):
        """Translates english gender into russian"""
        gender_words = {"Male": "Мужской",
                        "Female": "Женский",
                        "Do not specify": "Не указан"}

        return gender_words.get(self.gender)
