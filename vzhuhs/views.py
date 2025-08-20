import logging
import random

from dal import autocomplete
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from all_fixture.views_fixture import VZHUH_SETTINGS
from hotels.models import Hotel
from tours.models import Tour
from vzhuhs.filters import VzhuhFilter
from vzhuhs.models import Vzhuh
from vzhuhs.serializers import VzhuhSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="Список Вжухов",
        tags=[VZHUH_SETTINGS["name"]],
        parameters=[
            OpenApiParameter(
                name="departure_city",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по городу вылета",
                required=True,
            ),
        ],
    ),
    retrieve=extend_schema(exclude=True),
)
class VzhuhViewSet(ReadOnlyModelViewSet):
    """
    - Возвращает только записи с `is_published=True`.

    - Добавлена фильтрация по `departure_city` - городу отправления, поле обязательное.
    """

    queryset = Vzhuh.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = VzhuhFilter
    serializer_class = VzhuhSerializer

    SESSION_KEY = "vzhuh_history"
    MAX_HISTORY = 500  # Максимальная длина истории

    def get_queryset(self):
        return (
            Vzhuh.objects.prefetch_related(
                "tours__hotel__hotel_photos",
                "hotels__tours",
                "hotels__hotel_photos",
                "photos",
            )
            .filter(
                is_published=True,
            )
            .distinct()
            .order_by("?")
        )

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        all_ids = set(qs.values_list("id", flat=True))
        if not all_ids:
            return Response({"error": "Вжух не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Получаем историю показов
        seen = request.session.get(self.SESSION_KEY, [])
        # Ограничиваем размер истории
        if len(seen) > self.MAX_HISTORY:
            # fmt: off
            seen = seen[-self.MAX_HISTORY:]
            # fmt: on

        # Создаем список доступных ID
        remaining = [item_id for item_id in all_ids if item_id not in seen]

        if not remaining:
            # При сбросе цикла исключаем последний показанный
            last_seen = seen[-1] if seen else None
            pool = [item_id for item_id in all_ids if item_id != last_seen]
            if not pool:  # На случай, если всего 1 объект
                pool = list(all_ids)
            chosen_id = random.choice(pool)
            seen = [chosen_id]  # Начинаем новую историю
        else:
            # Если сущностей всего 2, чередуем их
            if len(all_ids) == 2 and len(seen) > 1:
                if seen[-1] == seen[-2]:
                    # Если последняя сущность такая же, как предыдущая, выбираем другую
                    seen.pop()
                    chosen_id = next(item_id for item_id in all_ids if item_id != seen[-1])
                    seen.append(chosen_id)
                else:
                    chosen_id = remaining[random.randint(0, len(remaining) - 1)]
                    seen.append(chosen_id)
            else:
                # Более эффективный выбор случайного элемента
                chosen_id = remaining[random.randint(0, len(remaining) - 1)]
                seen.append(chosen_id)

        # Обновляем сессию
        request.session[self.SESSION_KEY] = seen
        request.session.modified = True

        # Безопасное получение объекта
        try:
            instance = qs.get(id=chosen_id)
        except Vzhuh.DoesNotExist:
            # Удаляем несуществующий ID из истории
            seen.remove(chosen_id)
            request.session[self.SESSION_KEY] = seen
            request.session.modified = True
            return Response({"error": "Объект больше не доступен"}, status=410)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class VzhuhAutocompleteHotel(autocomplete.Select2QuerySetView):
    """
    Autocomplete-представление для выбора отелей, отфильтрованных по городу прибытия
    и исключающих уже выбранные отели.

    Используется в админке при создании/редактировании объекта Vzhuh.
    """

    def get_queryset(self):
        qs = Hotel.objects.all()
        arrival_city = self.forwarded.get("arrival_city", None)
        selected_ids = self.forwarded.get("hotels", [])

        if arrival_city:
            qs = qs.filter(city__icontains=arrival_city)
        if selected_ids:
            qs = qs.exclude(id__in=selected_ids)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class VzhuhAutocompleteTour(autocomplete.Select2QuerySetView):
    """
    Autocomplete-представление для выбора туров, отфильтрованных по городу прибытия
    и исключающих уже выбранные туры.

    Используется в админке при создании/редактировании объекта Vzhuh.
    """

    def get_queryset(self):
        qs = Tour.objects.all()
        departure_city = self.forwarded.get("departure_city", None)
        arrival_city = self.forwarded.get("arrival_city", None)
        selected_ids = self.forwarded.get("tours", [])

        if departure_city and arrival_city:
            qs = qs.filter(Q(arrival_city__icontains=arrival_city) & Q(departure_city__icontains=departure_city))
        if selected_ids:
            qs = qs.exclude(id__in=selected_ids)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
