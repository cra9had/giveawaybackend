import random
from django.db import transaction
from celery import shared_task
from django.utils import timezone
from webapp.models import GiveAway, Ticket
from webapp.services.checker import check_terms_of_participation


@shared_task
def finalize_giveaway(giveaway_id: int):
    # Получаем объект розыгрыша
    giveaway = GiveAway.objects.get(pk=giveaway_id)
    tickets = list(Ticket.objects.filter(giveaway=giveaway))
    unique_participants_count = Ticket.objects.filter(giveaway=giveaway).values('participant').distinct().count()
    giveaway.add_log({
        "text": "Загрузка участников розыгрыша...",
    })

    giveaway.add_log({
        "text": "Участники загружены!",
    })
    giveaway.add_log({
        "text": f"Количество участников - {unique_participants_count}",
    })

    if not tickets:
        # Если участников вообще нет, завершить задачу
        print("Нет участников для розыгрыша.")
        giveaway.add_log({
            "text": "Недостаточно участников для розыгрыша!",
        })
        return

    # Список для финальных победителей
    winners = []
    giveaway.add_log({
        "text": "Начинаем розыгрыш!",
    })
    # Отбор участников для каждого места
    for place in range(1, giveaway.winners_count + 1):
        giveaway.add_log({
            "text": f"Выбираем победителя на {place} место",
        })
        if not tickets:
            print("Участники закончились. Призовые места распределены по оставшимся участникам.")
            break

        while tickets:
            # Выбираем случайного участника
            selected_ticket = random.choice(tickets)
            ticket_user = selected_ticket.participant
            user_link = f"(<a href='https://t.me/{ticket_user.telegram_username}'>{ticket_user.first_name})"
            giveaway.add_log({
                "text": f"Выбран билет: {selected_ticket} {user_link}",
            })
            giveaway.add_log({
                "text": "Проверяем выполнение условий розыгрыша"
            })
            # Проверяем, соответствует ли участник условиям
            if check_terms_of_participation(ticket_user.jwt_token, giveaway.terms_of_participation):
                giveaway.add_log({
                    "text": "Условия выполнены!"
                })
                winners.append((place, selected_ticket))
                giveaway.add_log({
                    "text": f"Участник с билетом {selected_ticket} {user_link} побеждает и занимает {place} место в розыгрыше!"
                })
                # Удаляем участника из списка, чтобы он не мог быть выбран повторно
                tickets.remove(selected_ticket)
                break
            else:
                giveaway.add_log({
                    "text": "Условия не выполнены! Выбираем следущего участника"
                })

                # Если не соответствует, пробуем выбрать другого участника
                tickets.remove(selected_ticket)

                # Если участников больше нет, прекращаем отбор
                if not tickets:
                    print("Остальные участники не прошли проверку условий.")
                    break
    giveaway.add_log({
        "text": "Поздравляем победителей!"
    })

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
