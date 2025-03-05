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


class GenerateBPGraphState(StatesGroup):
    waiting_for_period = State()
    waiting_for_confirmation = State()


class RemindersState(StatesGroup):
    waiting_for_choice = State()


class CreateReminderState(StatesGroup):
    waiting_for_text = State()
    waiting_for_type = State()
    waiting_for_mode = State()
    waiting_for_interval = State()
    waiting_for_cron_schedule = State()
    waiting_for_date_time = State()


class DeleteReminderState(StatesGroup):
    waiting_for_number = State()


class NotesState(StatesGroup):
    waiting_for_choice = State()


class CreateNoteState(StatesGroup):
    waiting_for_text = State()


class DeleteNoteState(StatesGroup):
    waiting_for_number = State()
    