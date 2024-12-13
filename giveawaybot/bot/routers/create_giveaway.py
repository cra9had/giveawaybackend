import datetime
import os.path
import mimetypes

from aiogram import Router, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions, ChatMemberAdministrator, ChatMemberOwner, \
    MessageOriginChannel
from django.conf import settings
from bot.db import get_user_channels, create_channel
from bot.db import create_giveaway as create_giveaway_db
from bot.states import GiveawayCreation
from bot.utils import get_current_date_time_string, is_valid_future_datetime, parse_user_datetime, start_giveaway
from bot.keyboards import (get_confirm_description_keyboard, get_with_media_keyboard,
                           get_preview_giveaway_keyboard, get_use_referral_system_keyboard,
                           referral_counter_keyboard, SetReferralCounter, choice_channel_keyboard, SelectChannel,
                           get_cancel_channel_adding_keyboard, get_recheck_keyboard,
                           get_terms_of_participation_panel_keyboard, EditTermsOfParticipation)


router = Router()


@router.message(Command("create"))
async def create_giveaway(message: Message, state: FSMContext):
    await message.answer("Введите количество победителей от 1 до 50 (только число):")
    await state.set_state(GiveawayCreation.participants_number)


@router.message(GiveawayCreation.participants_number)
async def set_participants_number(message: Message, state: FSMContext):
    text = message.text
    if not text.isdigit():
        return await message.answer("Введите число!")
    number = int(text)
    if not 1 <= number <= 50:
        return await message.answer("Количество победителей должно быть от 1 до 50!")

    await message.answer("""<b>Введите название розыгрыша:</b>
    
Можно использовать максимум 50 символов.

<em>Это название будет отображаться у пользователя в списке розыгрышей в боте. Подойдите к названию максимально отвественно, чтобы ваши участники могли легко идентифицировать ваш розыгрыш среди всех остальных в разделе "активные розыгрыши".</em>
""")
    await state.update_data({
        "participants_number": number
    })
    await state.set_state(GiveawayCreation.giveaway_title)


@router.message(GiveawayCreation.giveaway_title)
async def set_giveaway_title(message: Message, state: FSMContext):
    text = message.text
    if len(text) > 50:
        return await message.answer("Можно использовать максимум 50 символов.")
    await message.answer("""
<b>Введите текст подробного описания розыгрыша:</b> 

Можно использовать максимум 2500 символов.

<em>Подробно опишите условия розыгрыша для ваших подписчиков. После старта розыгрыша введённый текст будет опубликован во все привязанные к нему каналы.</em>
""")
    await state.update_data({
        "giveaway_title": text
    })
    await state.set_state(GiveawayCreation.giveaway_description)


@router.message(GiveawayCreation.giveaway_description)
async def set_giveaway_description(message: Message, state: FSMContext):
    text = message.text
    if len(text) > 2500:
        return await message.answer("Можно использовать максимум 2500 символов.")

    await state.update_data({
        "giveaway_description": text
    })
    await message.answer(text, reply_markup=get_confirm_description_keyboard())


@router.callback_query(F.data == "edit_description")
async def edit_description(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("""
<b>Введите текст подробного описания розыгрыша:</b> 

Можно использовать максимум 2500 символов.

<em>Подробно опишите условия розыгрыша для ваших подписчиков. После старта розыгрыша введённый текст будет опубликован во все привязанные к нему каналы.</em>
""")
    await state.set_state(GiveawayCreation.giveaway_description)


@router.callback_query(F.data == "confirm_description")
async def confirm_description(call: CallbackQuery, state: FSMContext):
    await state.update_data({
        "with_media": False
    })
    await call.message.delete()
    await call.message.answer("Хотите добавить картинку/gif/видео для розыгрыша?",
                              reply_markup=get_with_media_keyboard())


@router.callback_query(F.data == "create_giveaway_with_media")
@router.callback_query(F.data == "change_giveaway_media")
async def ask_for_media(call: CallbackQuery, state: FSMContext):
    await call.message.answer("""
Отправьте картинку/gif/видео для розыгрыша.

<em>Используйте стандартную отправку. Не присылайте методом "без сжатия".</em>    

<b>Внимание! Видео должно быть в формате MP4, а его размер не превышать 5МБ.</b>
""")
    await state.set_state(GiveawayCreation.giveaway_media)


@router.message(GiveawayCreation.giveaway_media, F.photo | F.video)
async def create_giveaway_media(message: Message, state: FSMContext):
    if message.photo:
        file = message.photo[-1]
        extension = ".jpg"
    else:
        file = message.video
        mime_type = file.mime_type  # Example: "video/mp4"
        extension = mimetypes.guess_extension(mime_type) or ".mp4"

    file_info = await message.bot.get_file(file.file_id)
    file_path = file_info.file_path
    file_name = f"{file.file_unique_id}{extension}"
    # Construct the local file path
    save_path = os.path.join(
        settings.MEDIA_ROOT,
        settings.SAVE_GIVEAWAY_MEDIA_TO,
        file_name  # Use file_unique_id as the filename
    )
    await message.bot.download_file(file_path, save_path)
    await state.update_data({
        "with_media": True,
        "show_media_above_text": False,
        "media_path": os.path.join(settings.SAVE_GIVEAWAY_MEDIA_TO, file_name)
    })
    await preview_giveaway(message, state)


async def preview_giveaway(message: Message, state: FSMContext, with_preview_keyboard: bool = True):
    data = await state.get_data()
    show_above_text = data.get("show_media_above_text", False)
    if with_preview_keyboard:
        reply_keyboard = get_preview_giveaway_keyboard(show_above_text)
    else:
        reply_keyboard = None
    await message.answer(f"""  
{data.get('giveaway_title')}

{data.get('giveaway_description')}

Участников: <b>0</b>
Призовых мест: <b>{data.get('participants_number', 0)}</b>
Дата розыгрыша: <b>{data.get('output_end_datetime', '00:00, 00.00.0000')}</b>
""", link_preview_options=LinkPreviewOptions(
    url=f"{settings.DOMAIN}/media/{data.get('media_path')}",
    show_above_text=show_above_text,),
    reply_markup=reply_keyboard)


@router.callback_query(F.data == "change_giveaway_media_position")
async def change_media_position(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data({
        "show_media_above_text": not data.get("show_media_above_text", False)
    })
    await callback.message.delete()
    await preview_giveaway(callback.message, state)


@router.callback_query(F.data == "confirm_giveaway_media")
@router.callback_query(F.data == "create_giveaway_with_out_media")
async def ask_for_giveaway_end_datetime(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"""
Укажите время завершения розыгрыша в формате (ЧЧ:ММ ДД.ММ.ГГГГ)

Например: <em>{get_current_date_time_string(timedelta_hours=1)}</em>

Внимание! Бот работает по часовому поясу Астана (GMT+5). Актуальное время в боте: {get_current_date_time_string()}    
""")
    await state.set_state(GiveawayCreation.giveaway_end_datetime)


@router.message(GiveawayCreation.giveaway_end_datetime)
async def set_giveaway_end_datetime(message: Message, state: FSMContext):
    text = message.text
    user_datetime = parse_user_datetime(text)

    if user_datetime and is_valid_future_datetime(user_datetime):
        serialized_datetime = user_datetime.isoformat()
        await state.update_data(giveaway_end_datetime=serialized_datetime)
        await state.update_data(output_end_datetime=text)
        await user_referral_system(message, state)
    else:
        await message.answer("Дата и время розыгрыша должны быть позже настоящего времени и должна быть в формате (ЧЧ:ММ ДД.ММ.ГГГГ)")


@router.callback_query(F.data == "use_referral_system")
async def referral_system_counter(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text="""
Выберите количество друзей, которое должен пригласить участник для получения билета розыгрыша.

Например: если выбрали «2», то участник будет получать по одному билету розыгрыша за КАЖДЫХ ДВОИХ приглашенных друзей.

Приглашенный участник - это пользователь, который подписался на каналы розыгрыша и проверил подписку в боте. Если участник просто перешёл по реферальной ссылке, но не подписался на каналы, он не будет учитываться.

<b>Внимание! Количество друзей, которое нужно пригласить, нельзя будет изменить после запуска розыгрыша.</b>
""", reply_markup=referral_counter_keyboard())


@router.callback_query(F.data == "cancel_referral_system")
async def cancel_referral_system(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await user_referral_system(call.message, state)


async def user_referral_system(message: Message, state: FSMContext):
    await message.answer("""
Хотите использовать реферальную систему приглашений?

С помощью реферальной системы участники смогут приглашать в розыгрыш друзей и получать дополнительные шансы на победу. Это помогает продвигать розыгрыш с помощью вашей аудитории.

На следующем шаге вы сможете выбрать, сколько друзей нужно пригласить участнику для получения +1 дополнительного призового билета.

Каждый полученный бонусный билет может стать выигрышным при подведении результатов. Участники могут пригласить любое количество друзей без ограничений. Все приглашённые друзья в свою очередь подпишутся на каналы, прикреплённые к розыгрышу.

<b>Внимание! Данный функционал нельзя будет отключить после запуска розыгрыша.</b>        
""", reply_markup=get_use_referral_system_keyboard())


@router.callback_query(SetReferralCounter.filter())
async def set_referral_counter(call: CallbackQuery, state: FSMContext, callback_data: SetReferralCounter):
    amount = callback_data.amount
    await state.update_data({
        "use_referral_system": True,
        "referral_amount": amount,
    })
    await call.message.delete()
    await terms_of_participation_panel(call.message, state)


@router.callback_query(F.data == "dont_use_referral_system")
async def dont_use_referral_system(call: CallbackQuery, state: FSMContext):
    await terms_of_participation_panel(call.message, state)


async def terms_of_participation_panel(message: Message, state: FSMContext):
    data = await state.get_data()
    terms_of_participation = data.get("terms_of_participation", {
        "confirm_phone_required": False,
        "confirm_email_required": False,
        "deposit": {
            "required": False,
            "sum": 0
        },
        "bet": {
            "required": False,
            "sum": 0
        }
    })
    if not data.get("terms_of_participation", None):
        await state.update_data(terms_of_participation=terms_of_participation)
    await message.answer("Выберите условия, чтобы стать участником розыгрыша",
                         reply_markup=get_terms_of_participation_panel_keyboard(terms_of_participation))


@router.callback_query(EditTermsOfParticipation.filter())
async def edit_terms_of_participation(call: CallbackQuery, state: FSMContext, callback_data: EditTermsOfParticipation):
    data = await state.get_data()
    terms_of_participation = data.get("terms_of_participation")
    await call.message.delete()
    if callback_data.name == "deposit":
        await state.set_state(GiveawayCreation.set_deposit_sum)
        await call.message.answer("Введите минимальную сумму депозита (0, чтобы отменить)")
    elif callback_data.name == "bet":
        await state.set_state(GiveawayCreation.set_bet_sum)
        await call.message.answer("Введите минимальную сумму ставки (0, чтобы отменить)")
    else:
        terms_of_participation.update({
            callback_data.name: not terms_of_participation.get(callback_data.name),
        })
        await state.update_data(terms_of_participation=terms_of_participation)
        await terms_of_participation_panel(call.message, state)


@router.message(GiveawayCreation.set_deposit_sum)
async def set_deposit_sum(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Пришлите число!")
    data = await state.get_data()
    terms_of_participation = data.get("terms_of_participation")
    terms_of_participation["deposit"]["sum"] = int(message.text)
    await state.update_data(terms_of_participation=terms_of_participation)
    await terms_of_participation_panel(message, state)


@router.message(GiveawayCreation.set_bet_sum)
async def set_bet_sum(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Пришлите число!")
    data = await state.get_data()
    terms_of_participation = data.get("terms_of_participation")
    terms_of_participation["bet"]["sum"] = int(message.text)
    await state.update_data(terms_of_participation=terms_of_participation)
    await terms_of_participation_panel(message, state)


@router.callback_query(F.data == "confirm_terms")
async def confirm_terms(call: CallbackQuery, state: FSMContext):
    await giveaway_created(call.message, state)


async def giveaway_created(message: Message, state: FSMContext):
    await preview_giveaway(message, state, with_preview_keyboard=False)
    user_channels = await get_user_channels(message.chat.id)
    print(user_channels)

    await message.answer("""
Розыгрыш успешно создан, но не запущен!

Выберите канал из списка или добавьте новый
""", reply_markup=choice_channel_keyboard(user_channels))


@router.callback_query(SelectChannel.filter())
async def select_channel(call: CallbackQuery, state: FSMContext, callback_data: SelectChannel):
    user_channels = await get_user_channels(call.message.chat.id)
    await state.update_data(selected_channel_pk=callback_data.channel_pk)
    await call.message.edit_reply_markup(reply_markup=choice_channel_keyboard(user_channels, selected_channel_pk=callback_data.channel_pk))


@router.callback_query(F.data == "add_channel")
async def add_channel(call: CallbackQuery, state: FSMContext):
    me = await call.bot.get_me()
    await state.set_state(GiveawayCreation.adding_channel)
    await call.message.answer(f"""
Сделайте бота <code>@{me.username}</code> администратором в подключаемом канале со следующими правами:
- Публикация сообщений
- Редактирование сообщений
- Добавление подписчиков 

После этого перешлите любое сообщение из канала в этот бот
""", reply_markup=get_cancel_channel_adding_keyboard())


@router.callback_query(F.data == "cancel_channel_adding")
async def cancel_channel_adding(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.set_state()


@router.message(GiveawayCreation.adding_channel)
async def add_channel_from_forwarded_message(message: Message, state: FSMContext):
    bot = message.bot

    if message.forward_origin:  # Check if the message is forwarded
        original_chat_id = message.forward_from_chat.id if message.forward_from_chat else None
        if original_chat_id:
            try:
                bot_member = await bot.get_chat_member(chat_id=original_chat_id, user_id=bot.id)
                channel_info = await bot.get_chat(chat_id=original_chat_id)
                channel_name = channel_info.title

                if isinstance(bot_member, ChatMemberAdministrator) or isinstance(bot_member, ChatMemberOwner):
                    can_post_messages = getattr(bot_member, "can_post_messages", False)
                    can_edit_messages = getattr(bot_member, "can_edit_messages", False)
                    can_invite_users = getattr(bot_member, "can_invite_users", False)
                    if can_post_messages and can_edit_messages and can_invite_users:
                        channel = await create_channel(original_chat_id, message.chat.id, channel_name)
                        await state.update_data(selected_channel_pk=channel.pk)
                        await state.set_state()
                        return await giveaway_created(message, state)
            except TelegramAPIError as e:
                return await message.answer("Убедитесь, что бот добавлен в администраторы канала")

    await message.answer("Добавьте бота в администраторы канала и вручите необходимые права")


@router.callback_query(F.data == "start_giveaway")
async def recheck_giveaway(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("selected_channel_pk"):
        return await call.message.answer("Сначала выберите канал для розыгрыша!")
    await preview_giveaway(call.message, state, with_preview_keyboard=False)
    await call.message.answer("Проверь картинку, текст, дату и время подведения итогов розыгрыша. Всё готово для запуска? ",
                              reply_markup=get_recheck_keyboard())


@router.callback_query(F.data == "recheck_confirmed")
async def recheck_confirmed(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    giveaway = await create_giveaway_db(
        channel_pk=data.get("selected_channel_pk"),
        title=data.get("giveaway_title"),
        description=data.get("giveaway_description"),
        end_datetime=datetime.datetime.fromisoformat(data.get("giveaway_end_datetime")),
        winners_count=data.get("participants_number"),
        is_referral_system=data.get("use_referral_system"),
        referral_invites_count=data.get("referral_amount", 0),
        terms_of_participation=data.get("terms_of_participation"),
        image=os.path.join(settings.MEDIA_ROOT, data.get("media_path", "")),
        show_image_above_text=data.get("show_media_above_text", False),

    )
    await start_giveaway(call.bot, giveaway)
    await call.message.answer("Розыгрыш успешно запушен!")
