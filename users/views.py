import logging
import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from django.utils.timezone import now
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_field,
    extend_schema_view,
)
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from all_fixture.choices import RoleChoices
from all_fixture.pagination import CustomLOPagination
from all_fixture.views_fixture import (
    AUTH_SETTINGS,
    ENTREPRISE_ID,
    ENTREPRISE_SETTINGS,
    LIMIT,
    OFFSET,
    USER_ID,
    USER_SETTINGS,
)
from config.settings import EMAIL_HOST_USER
from users.models import User
from users.permissions import IsAdminOrOwner
from users.serializers import (
    CheckTokenErrorResponseSerializer,
    CheckTokenSuccessResponseSerializer,
    CompanyUserSerializer,
    DeleteTokenSerializer,
    EmailCodeResponseSerializer,
    EmailLoginSerializer,
    ErrorResponseSerializer,
    LogoutSerializer,
    LogoutSuccessResponseSerializer,
    UserSerializer,
    VerifyCodeResponseSerializer,
    VerifyCodeSerializer,
)
from users.services import check_ban, get_login_state, record_login_attempt

logger = logging.getLogger(__name__)


# Функция-хелпер
def blacklist_user_tokens(user):
    """Аннулирует все токены пользователя перед удалением."""
    try:
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
    except Exception as e:
        logger.warning(f"[User DELETE] Ошибка при аннулировании токенов: {e}")


class RefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class AuthViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ViewSet для аутентификации по email-коду (без ID пользователя)."""

    permission_classes = [AllowAny]
    serializer_class = EmailLoginSerializer

    def get_serializer_class(self):
        """Определяем сериализатор в зависимости от действия."""
        if self.action == "create":
            return EmailLoginSerializer
        elif self.action == "verify":
            return VerifyCodeSerializer
        return self.serializer_class

    @extend_schema(
        summary="Запросить код для входа",
        description="Отправляет 4-значный код на email пользователя для входа в систему.",
        tags=[AUTH_SETTINGS["name"]],
        request={"multipart/form-data": EmailLoginSerializer},
        responses={
            200: OpenApiResponse(
                response=EmailCodeResponseSerializer,
                description="Код успешно отправлен",
            ),
            404: OpenApiResponse(description="Пользователь не найден"),
        },
        examples=[
            OpenApiExample(
                name="Пример запроса",
                value={"email": "user@example.com"},
                request_only=True,
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        is_registered = User.objects.filter(email=email).exists()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден", "register": is_registered},
                status=status.HTTP_404_NOT_FOUND,
            )

        code = random.randint(1000, 9999)
        user.set_password(str(code))
        user.save(update_fields=["password"])

        self.send_email(user.email, code)

        return Response(
            {"message": "Код отправлен на email", "register": is_registered},
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def send_email(email, code):
        """Отправка email с кодом."""
        email_message = EmailMessage(
            subject="Ваш код для входа",
            body=f"""
                <html>
                    <body>
                        <p>Код для входа в сервис <strong>'Куда Угодно'</strong>:
                        <strong style="font-size:18px;color:#007bff;">{code}</strong>.</p>
                        <p><strong>Никому не сообщайте этот код!</strong>
                        Если вы не запрашивали код, просто проигнорируйте это сообщение.</p>
                    </body>
                </html>
            """,
            from_email=EMAIL_HOST_USER,
            to=[email],
        )
        email_message.content_subtype = "html"
        email_message.send()

    @extend_schema(
        summary="Подтвердить код и установить токены",
        description=(
            "Проверка email и кода. В случае успеха — установка JWT токенов (access и refresh) "
            "в cookie. В теле ответа возвращаются только роль и ID пользователя."
        ),
        tags=[AUTH_SETTINGS["name"]],
        request={"multipart/form-data": VerifyCodeSerializer},
        responses={
            200: OpenApiResponse(
                response=VerifyCodeResponseSerializer,
                description="Успешный ответ с ролью и ID пользователя. Токены установлены в cookie.",
            ),
            400: OpenApiResponse(
                description="Неверный код",
                examples=[
                    OpenApiExample(
                        name="Ошибка",
                        value={"error": "Неверный код"},
                        response_only=True,
                    )
                ],
            ),
        },
    )
    @action(detail=False, methods=["post"], url_path="verify", permission_classes=[AllowAny])
    def verify(self, request):
        """
        Проверка email-кода, логирование попытки и выдача JWT-токенов.
        Блокирует пользователя после 5 неудач с нарастающим таймаутом.
        """
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        # ─── 1. Проверяем существование пользователя и активные баны ─────────────
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # деактивирован — возвращаем 403, а не уходим в "неверный код"
        if not user.is_active:
            return Response({"error": "Аккаунт деактивирован"}, status=status.HTTP_403_FORBIDDEN)

        # активная блокировка — сразу 423 + детали
        try:
            check_ban(user)
        except PermissionError:
            state = get_login_state(user)
            return Response(
                {
                    "error": "Слишком много неверных попыток",
                    "remaining_attempts": 0,
                    "blocked_until": state.blocked_until,
                },
                status=status.HTTP_423_LOCKED,
            )
        # ─── 2. Пробуем аутентифицировать по коду ────────────────────────────────
        authenticated_user = authenticate(email=email, password=str(code))
        success = authenticated_user is not None

        # ─── 3. Записываем попытку ───────────────────────────────────────────────
        state = record_login_attempt(user, success, request.META.get("REMOTE_ADDR"))
        if not success:
            return Response(
                {
                    "error": "Неверный код",
                    "remaining_attempts": state.remaining_attempts,
                    "blocked_until": state.blocked_until,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # ─── 4. Всё ок – выдаем токены и куки (оригинальный код без изменений) ───
        refresh = RefreshToken.for_user(authenticated_user)
        response = Response(
            {"role": authenticated_user.role, "id": authenticated_user.id},
            status=status.HTTP_200_OK,
        )

        expires = now() + timedelta(days=30)
        secure = not settings.DEBUG

        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=secure,
            samesite="Lax",
            expires=expires,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=secure,
            samesite="Lax",
            expires=expires,
        )
        return response

    @extend_schema(
        summary="Выход из системы (Logout)",
        description="Аннулирует refresh-токен и завершает сессию пользователя.",
        tags=[AUTH_SETTINGS["name"]],
        request={"multipart/form-data": LogoutSerializer},
        responses={
            205: OpenApiResponse(
                response=LogoutSuccessResponseSerializer,
                description="Вы успешно вышли из системы",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Ошибка при выходе",
                examples=[
                    OpenApiExample(
                        name="Ошибка: токен не передан",
                        value={"error": "Refresh-токен не передан"},
                        response_only=True,
                    ),
                    OpenApiExample(
                        name="Ошибка: некорректный токен",
                        value={"error": "Token is invalid or expired"},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
        permission_classes=[IsAuthenticated],
    )
    def logout(self, request):
        """
        Выход из системы: аннулирование refresh-токена и удаление cookies.
        """

        # Пробуем взять refresh из тела запроса
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        refresh_token = (
            serializer.validated_data.get("refresh") if serializer.is_valid() else request.COOKIES.get("refresh_token")
        )

        if not refresh_token:
            return Response(
                {"error": "Refresh-токен не передан"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"message": "Вы вышли"}, status=status.HTTP_200_OK)
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Проверка активности access-токена",
        description="Проверяет, действителен ли access-токен. Если токен истёк или отсутствует, возвращает 401.",
        tags=[AUTH_SETTINGS["name"]],
        responses={
            200: OpenApiResponse(
                response=CheckTokenSuccessResponseSerializer,
                description="Токен действителен",
            ),
            401: OpenApiResponse(
                response=CheckTokenErrorResponseSerializer,
                description="Токен недействителен или отсутствует",
                examples=[
                    OpenApiExample(
                        name="Ошибка",
                        value={"error": "Недействительный или отсутствующий токен"},
                        response_only=True,
                    )
                ],
            ),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="fetch_me",
        permission_classes=[IsAuthenticated],
    )
    def fetch_me(self, request):
        """Проверяет токен и возвращает текущего пользователя."""
        user = request.user

        if user.role in [RoleChoices.TOUR_OPERATOR, RoleChoices.HOTELIER]:
            serializer = CompanyUserSerializer(user, context={"request": request})
        else:
            serializer = UserSerializer(user, context={"request": request})

        return Response(
            {
                "message": "Токен активен",
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Обновление токенов",
        description="Обновляет access и refresh токены. Возвращает новые токены и обновляет cookies.",
        tags=[AUTH_SETTINGS["name"]],
        request=RefreshRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="Новые токены выданы",
                examples=[
                    OpenApiExample(
                        name="OK",
                        value={"access": "str", "refresh": "str"},
                        response_only=True,
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Невалидный или отозванный токен",
                examples=[
                    OpenApiExample(
                        name="Ошибка",
                        value={"error": "Token is invalid or expired"},
                        response_only=True,
                    )
                ],
            ),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="refresh",
        permission_classes=[AllowAny],
    )
    def refresh(self, request):
        serializer = RefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            access = refresh.access_token

            response = Response(
                {"refresh": str(refresh), "access": str(access)},
                status=status.HTTP_200_OK,
            )

            expires = now() + timedelta(days=30)
            secure = not settings.DEBUG

            response.set_cookie(
                "access_token",
                str(access),
                httponly=True,
                secure=secure,
                samesite="Lax",
                expires=expires,
            )
            response.set_cookie(
                "refresh_token",
                str(refresh),
                httponly=True,
                secure=secure,
                samesite="Lax",
                expires=expires,
            )
            return response

        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema_view(
    list=extend_schema(
        summary="Список пользователей (турист)",
        description="Получение списка всех обычных пользователей",
        tags=[USER_SETTINGS["name"]],
        parameters=[LIMIT, OFFSET],
        responses={200: UserSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Создание пользователя",
        description="Создание нового пользователя с указанием email и пароля",
        tags=[USER_SETTINGS["name"]],
        request={"multipart/form-data": UserSerializer},
        responses={201: UserSerializer},
    ),
    retrieve=extend_schema(
        summary="Детальная информация о пользователе",
        description="Получение полной информации о конкретном пользователе (туристе) по ID",
        tags=[USER_SETTINGS["name"]],
        parameters=[USER_ID],
        responses={
            200: UserSerializer,
            404: OpenApiResponse(description="Пользователь не найден"),
        },
    ),
    update=extend_schema(
        summary="Обновление пользователя",
        description="Полное обновление информации о пользователе (туристе) по ID",
        tags=[USER_SETTINGS["name"]],
        parameters=[USER_ID],
        request={"multipart/form-data": UserSerializer},
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Ошибка валидации"),
            404: OpenApiResponse(description="Пользователь не найден"),
        },
    ),
    destroy=extend_schema(
        summary="Удаление пользователя",
        description=(
            "Удаление обычного пользователя по ID.\n\n"
            "- Пользователь с ролью `USER` может удалить только **себя**.\n"
            "- Админ может удалить **любого пользователя**.\n"
            "- Туроператоры и Отельеры удаляются только через ручку компаний.\n\n"
            "Можно передать `refresh` токен в теле запроса для его аннулирования (необязательно)."
        ),
        tags=[USER_SETTINGS["name"]],
        parameters=[USER_ID],
        request=DeleteTokenSerializer,
        responses={
            204: OpenApiResponse(description="Пользователь удалён"),
            403: OpenApiResponse(description="Удаление запрещено"),
            404: OpenApiResponse(description="Пользователь не найден"),
        },
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для обычных пользователей (туристов)."""

    queryset = User.objects.none()
    serializer_class = UserSerializer
    pagination_class = CustomLOPagination
    parser_classes = (MultiPartParser, FormParser)
    # Админ видит всех, юзер — только себя

    # Исключаем 'patch'
    http_method_names = ["get", "post", "put", "delete", "head", "options", "trace"]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return User.objects.all().order_by("-pk")
        else:
            return User.objects.filter(pk=user.pk)

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminOrOwner]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """Получение детальной информации о пользователе по ID."""
        instance = self.get_object()
        # Проверка объекта
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema_field(serializers.ImageField())
    def get_avatar(self, obj):
        """Отображает URL аватарки, если она загружена."""
        if obj.avatar:
            return obj.avatar.url
        return None

    def update(self, request, *args, **kwargs):
        """Полное обновление информации о пользователе по ID."""
        instance = self.get_object()
        data = request.data.copy()

        # Обработка загрузки файлов
        if request.FILES:
            if "avatar" in request.FILES:
                data["avatar"] = request.FILES["avatar"]

        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if hasattr(instance, "_prefetched_objects_cache"):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if not user.is_superuser:
            if user != instance or instance.role != RoleChoices.USER:
                return Response({"error": "Удаление запрещено"}, status=status.HTTP_403_FORBIDDEN)

        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                logger.warning(f"[User DELETE] Не удалось аннулировать refresh токен: {e}")

        # Аннулируем все оставшиеся токены пользователя
        blacklist_user_tokens(instance)

        self.perform_destroy(instance)
        return Response({"message": "Пользователь удалён"}, status=status.HTTP_204_NO_CONTENT)

    # ───────────────  action-методы для деактивации / активации аккаунта ──────────────────────────
    @extend_schema(
        summary="Деактивация аккаунта",
        description=("Переводит is_active=False и отзывает все JWT-токены пользователя."),
        tags=[USER_SETTINGS["name"]],
        request=None,
        parameters=[USER_ID],
        responses={200: OpenApiResponse(description="Аккаунт деактивирован")},
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        # запрещаю суперпользователю выключать самого себя
        if request.user == user and request.user.is_superuser:
            return Response(
                {"error": "Суперпользователь не может деактивировать себя самого"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.is_active:
            return Response({"message": "Уже деактивирован"}, status=status.HTTP_200_OK)

        user.is_active = False
        user.save(update_fields=["is_active"])
        blacklist_user_tokens(user)
        return Response({"message": "Аккаунт деактивирован"}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Реактивация аккаунта",
        description="Переводит is_active=True (обратное действие).",
        tags=[USER_SETTINGS["name"]],
        parameters=[USER_ID],
        request=None,
        responses={200: OpenApiResponse(description="Аккаунт реактивирован")},
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reactivate(self, request, pk=None):
        user = self.get_object()
        if user.is_active:
            return Response({"message": "Уже активен"}, status=status.HTTP_200_OK)

        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({"message": "Аккаунт реактивирован"}, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary="Список компаний (Туроператоры и Отельеры)",
        description="Получение списка всех компаний (Туроператоры и Отельеры)",
        tags=[ENTREPRISE_SETTINGS["name"]],
        parameters=[LIMIT, OFFSET],
        responses={200: CompanyUserSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Создание компании",
        description="Создание нового Туроператора или Отельера",
        tags=[ENTREPRISE_SETTINGS["name"]],
        request=CompanyUserSerializer,
        responses={201: CompanyUserSerializer},
    ),
    retrieve=extend_schema(
        summary="Детальная информация о компании",
        description="Получение детальной информации о конкретной компании по ID",
        tags=[ENTREPRISE_SETTINGS["name"]],
        parameters=[ENTREPRISE_ID],
        responses={
            200: CompanyUserSerializer,
            404: OpenApiResponse(description="Компания не найдена"),
        },
    ),
    update=extend_schema(
        summary="Обновление компании",
        description="Полное обновление информации о компании по ID",
        tags=[ENTREPRISE_SETTINGS["name"]],
        parameters=[ENTREPRISE_ID],
        request=CompanyUserSerializer,  # 👈 верный сериализатор для обновления
        responses={
            200: CompanyUserSerializer,
            400: OpenApiResponse(description="Ошибка валидации"),
            404: OpenApiResponse(description="Компания не найдена"),
        },
    ),
    destroy=extend_schema(
        summary="Удаление компании",
        description=(
            "Удаление компании (Туроператора или Отельера) по ID.\n\n"
            "- Только администратор может удалять компании.\n"
            "- Туроператор и Отельер **не могут удалить себя самостоятельно**.\n\n"
            "Можно передать `refresh` токен для аннулирования (опционально)."
        ),
        tags=[ENTREPRISE_SETTINGS["name"]],
        parameters=[ENTREPRISE_ID],
        request=DeleteTokenSerializer,  # 👈 универсальный сериализатор
        responses={
            204: OpenApiResponse(description="Компания удалена"),
            403: OpenApiResponse(description="Удаление запрещено"),
            404: OpenApiResponse(description="Компания не найдена"),
        },
    ),
)
class CompanyUserViewSet(viewsets.ModelViewSet):
    """ViewSet для Туроператоров и Отельеров."""

    queryset = User.objects.filter(role__in=[RoleChoices.TOUR_OPERATOR, RoleChoices.HOTELIER]).order_by("-pk")
    serializer_class = CompanyUserSerializer
    pagination_class = CustomLOPagination
    # Исключаем 'patch'
    http_method_names = ["get", "post", "put", "delete", "head", "options", "trace"]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return User.objects.filter(role__in=[RoleChoices.TOUR_OPERATOR, RoleChoices.HOTELIER]).order_by("-pk")
        elif user.role in [RoleChoices.TOUR_OPERATOR, RoleChoices.HOTELIER]:
            return User.objects.filter(pk=user.pk)
        return User.objects.none()

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminOrOwner]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """Получение детальной информации о компании по ID."""
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Полное обновление информации о компании по ID."""
        instance = self.get_object()
        data = request.data.copy()

        # Обработка загрузки файлов
        if request.FILES:
            if "avatar" in request.FILES:
                data["avatar"] = request.FILES["avatar"]
            if "documents" in request.FILES:
                data["documents"] = request.FILES["documents"]

        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if hasattr(instance, "_prefetched_objects_cache"):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        # Только админ может удалять компании
        if not user.is_superuser:
            return Response(
                {"error": "Удаление разрешено только администратору"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Мягкое аннулирование токена
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                logger.warning(f"[Company DELETE] Не удалось аннулировать токен {instance.email}: {e}")

        self.perform_destroy(instance)
        return Response({"message": "Компания удалена"}, status=status.HTTP_204_NO_CONTENT)
