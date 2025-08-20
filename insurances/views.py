from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ModelViewSet

from all_fixture.errors.list_error import INSURANCE_ERROR
from all_fixture.errors.serializers_error import InsurancesErrorIdSerializer
from all_fixture.views_fixture import INSURANCE_ID, INSURANCE_SETTINGS
from insurances.models import Insurances
from insurances.serializers import InsuranceSerializer


@extend_schema(tags=[INSURANCE_SETTINGS["name"]])
@extend_schema_view(
    retrieve=extend_schema(
        summary="Информация о страховке",
        description="Получение информации о страховке",
        parameters=[INSURANCE_ID],
        responses={
            200: OpenApiResponse(
                response=InsuranceSerializer,
                description="Успешное получение страховок",
            ),
            404: OpenApiResponse(
                response=InsurancesErrorIdSerializer,
                description="Ошибка: страховка не найдены",
            ),
        },
    ),
    update=extend_schema(
        summary="Полное обновление страховки",
        description="Обновление всех полей страховки",
        request={"multipart/form-data": InsuranceSerializer},
        parameters=[INSURANCE_ID],
        responses={
            200: OpenApiResponse(
                response=InsuranceSerializer,
                description="Успешное обновление страховок",
            ),
            404: OpenApiResponse(
                response=InsurancesErrorIdSerializer,
                description="Ошибка: страховка не найдены",
            ),
        },
    ),
)
class InsurancesView(ModelViewSet):
    queryset = Insurances.objects.all()
    serializer_class = InsuranceSerializer

    def get_object(self):
        try:
            return Insurances.objects.get(pk=self.kwargs["pk"])
        except Insurances.DoesNotExist:
            raise NotFound(INSURANCE_ERROR) from None
