from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    waiting_for_anonymity = State()
    waiting_for_full_name = State()
    waiting_for_gender = State()


class MenuState(StatesGroup):
    waiting_for_choice = State()


class ProfileState(StatesGroup):
    waiting_for_choice = State()


class EditProfileState(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_gender = State()
    back = State()


class AnonimProfileState(StatesGroup):
    waiting_for_choice = State()


class DeanonymizationState(StatesGroup):
    waiting_for_name = State()
