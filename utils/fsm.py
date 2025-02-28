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


class BloodPressureState(StatesGroup):
    waiting_for_choice = State()


class CreateBPEntryState(StatesGroup):
    waiting_for_bp = State()
    waiting_for_pulse = State()
    waiting_for_remark = State()
    waiting_for_confirmation = State()
