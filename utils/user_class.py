class User:
    def __init__(self, user_id, full_name=None, gender=None):
        self.user_id = user_id
        self.full_name = full_name
        self.gender = gender

    def translate_gender(self):
        """Translate english gender into russian"""
        gender_words = {"Male": "Мужской",
                        "Female": "Женский",
                        "Do not specify": "Не указан"}

        return gender_words.get(self.gender)
