from aiogram.fsm.state import State, StatesGroup


class GiveawayCreation(StatesGroup):
    participants_number = State()
    giveaway_title = State()
    giveaway_description = State()
    giveaway_media = State()
    giveaway_end_datetime = State()
    set_bet_sum = State()
    set_deposit_sum = State()
    adding_channel = State()


