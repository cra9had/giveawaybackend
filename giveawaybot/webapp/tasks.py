import random
from django.db import transaction
from celery import shared_task
from django.utils import timezone
from .models import GiveAway, Ticket
from .services.checker import check_terms_of_participation


@shared_task
def finalize_giveaway(giveaway_id: int):
    # Получаем объект розыгрыша
    giveaway = GiveAway.objects.get(pk=giveaway_id)
    tickets = list(Ticket.objects.filter(giveaway=giveaway))
    # giveaway.add_log({
    #     "text": "Загрузка участников розыгрыша...",
    # })
    #
    # giveaway.add_log({
    #     "text": "Участники загружены!",
    # })
    # giveaway.add_log({
    #     "text": f"Количество участников - {unique_participants_count}",
    # })

    if not tickets:
        # Если участников вообще нет, завершить задачу
        print("Нет участников для розыгрыша.")
        giveaway.add_log({
            "text": "Недостаточно участников для розыгрыша!",
            "error": True,
        })
        return

    # Список для финальных победителей
    winners = []
    # giveaway.add_log({
    #     "text": "Начинаем розыгрыш!",
    # })
    # Отбор участников для каждого места
    for place in range(1, giveaway.winners_count + 1):
        giveaway.add_log({
            "type": "choice_participant",
            "position": place,
        })
        if not tickets:
            print("Участники закончились. Призовые места распределены по оставшимся участникам.")
            break

        while tickets:
            # Выбираем случайного участника
            selected_ticket = random.choice(tickets)
            ticket_user = selected_ticket.participant
            user_link = f"<a href='https://t.me/{ticket_user.telegram_username}'>{ticket_user.telegram_username}</a>"
            giveaway.add_log({
                # "text": f"Выбран билет: {selected_ticket} {user_link}",
                "type": "select_ticket",
                "selected_ticket": selected_ticket.number_ticket,
                "username": ticket_user.telegram_username,
            })

            # Проверяем, соответствует ли участник условиям
            check_terms = check_terms_of_participation(ticket_user.jwt_token, giveaway.terms_of_participation)
            if check_terms.get("status") is True:
                giveaway.add_log({
                    # "text": "Условия выполнены!",
                    "type": "check_terms",
                    "errors": []
                })
                winners.append((place, selected_ticket))
                giveaway.add_log({
                    # "text": f"Участник с билетом {selected_ticket} {user_link} побеждает и занимает {place} место в розыгрыше!"
                    "type": "participant_win",
                    "selected_ticket": selected_ticket.number_ticket,
                    "user_link": user_link,
                    "position": place,
                })
                # Удаляем участника из списка, чтобы он не мог быть выбран повторно
                tickets.remove(selected_ticket)
                break
            else:
                giveaway.add_log({
                    # "text": "Условия не выполнены! Выбираем следущего участника"
                    "type": "check_terms",
                    "errors": check_terms.get("errors")
                })

                # Если не соответствует, пробуем выбрать другого участника
                tickets.remove(selected_ticket)

                # Если участников больше нет, прекращаем отбор
                if not tickets:
                    print("Остальные участники не прошли проверку условий.")
                    break
    # giveaway.add_log({
    #     "text": "Поздравляем победителей!"
    # })

    # Сохраняем результаты
    with transaction.atomic():
        for place, winner in winners:
            # Пример сохранения победителя с указанием места
            winner.position = place
            winner.is_winner = True
            winner.save()
        giveaway.status = "end"
        giveaway.end_datetime = timezone.now()
        giveaway.save()


def start_giveaway(giveaway_id: int):
    giveaway = GiveAway.objects.get(pk=giveaway_id)
    if giveaway.status != 'created':
        return
    giveaway.status = 'in_progress'

    import pytz
    from django.utils.timezone import localtime
    print(f"Scheduled ETA: {localtime(giveaway.end_datetime)}")
    print(f"UTC ETA: {giveaway.end_datetime.astimezone(pytz.UTC)}")
    finalize_giveaway.apply_async(
        args=[giveaway_id],
        eta=giveaway.end_datetime  # `eta` is the exact time to execute the task
    )
    giveaway.save()

