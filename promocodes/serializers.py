from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, DecimalField, ImageField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from promocodes.models import Promocode
from tours.models import Tour


class PromocodeSerializer(ModelSerializer):
    discount_amount = DecimalField(
        max_digits=10,
        decimal_places=2,
        default="0.17",
    )
    photo = ImageField()

    class Meta:
        model = Promocode
        fields = (
            "id",
            "photo",
            "start_date",
            "end_date",
            "name",
            "code",
            "discount_amount",
            "description",
            "tours",
            "hotels",
            "is_active",
        )


class PromoCodeCheckSerializer(Serializer):
    """
    Сериализатор для проверки промокода.
    Ожидаем что в него будет переданы поля:
     - promo_code - сам промокод
     - tour_id - список id туров, или один тур
     - hotel_id - список id отелей, или один отель
     - start_date - дата начала бронирования/заявки
     - end_date - дата окончания бронирования/заявки
     Возможно даты не нужны. Но нужно предерживаться логики.
     У нас есть отель, заходя вовнутрь него, мы видим список всех номеров, заранее мы передали в квери дату начала
     бронирования и дату окончания бронирования, нам показываются только отфильтрованные данные по номерам в этом отеле.
     Далее,мы выбираем номер, нажимаем кнопку забронировать, и перемещаемся на страницу заявки, куда передаётся вся инфа
     Какой отель, какой номер, какой тип питания, с какой по какую дату мы бронируем, на этом этапе мы знаем цену
     за все дни, переданные из квери к заявку, и они к примеру составляет 100_000. Теперь мы вводим в окно для промокода
     код, необходимо проверить:
     1. Что код действительный, на текущую дату, когда совершается бронирование, если не действительный, выдать ошибку
     2. Берём величину скидки, (до 1.00 - это проценты, всё что выше 1.00 - это фиксированная скидка) и отнимаем от
     total_price_with_discount (почему это поле? потому что оно является последней ценой, перед применение промокода),
     которое должно передавать в заявку.
     3. После удачной проверки промокода, мы изменяем поле applications.price посчитанное значение.
     Необходимо учитывать, что в объекте заявки еще есть поля по стоимости мед страховок, виз, страховок от невыезда
     И эту стоимость не нужно учитывать в вычислении скидки от промокода.
     В идеале мы должны на этапе сохранения видеть стоимость выбранного забронированного номера с учётом скидки, до
     применения промокода, после применения промокода, стоимость изменится, и к ней уже нужно будует прибавлять цены
     страховок и виз. В конечном этапе будем иметь одну стоимость заявки, которую нужно обновить. Так как в момент
     нажатия на кнопку бронировать создаётся заявка, в неё передаются все поля Отеля/Номера/Типа питания/Стоимости/
     /Дат бронирования/, а после этого уже происходит редактирование заявки. Или же без редактирования делать это всё
     в заявке
    """

    promo_code = CharField()
    tour_id = IntegerField(required=False)
    hotel_id = IntegerField(required=False)

    def validate(self, data):
        promo_code_value = data["promo_code"]
        tour_id = data.get("tour_id")
        hotel_id = data.get("hotel_id")

        try:
            promo = Promocode.objects.get(code=promo_code_value)
        except Promocode.DoesNotExist:
            raise ValidationError("Промокод не найден.") from None

        if not promo.is_valid():
            raise ValidationError("Промокод просрочен или неактивен.") from None

        if tour_id:
            if not promo.tours.filter(id=tour_id).exists():
                raise ValidationError("Промокод не действует на данный тур.")
            tour = get_object_or_404(Tour, id=tour_id)
            return {
                "tour_price": tour.total_price,
                "discount_amount": promo.discount_amount,
                "total_price": promo.apply_discount(tour.total_price),
            }

        elif hotel_id:
            if not promo.hotels.filter(id=hotel_id).exists():
                raise ValidationError("Промокод не действует на данный отель.") from None
            # hotel = get_object_or_404(Hotel, id=hotel_id)
            return {
                "discount_amount": promo.discount_amount,
            }

        else:
            raise ValidationError("Нужно передать tour_id или hotel_id.") from None
