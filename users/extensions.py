from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CookieJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    """
    DRF Spectacular-расширение для поддержки JWT-аутентификации через cookie.
    Обеспечивает корректное отображение схемы аутентификации в документации OpenAPI,
    указывая, что токен передаётся не в заголовке, а в cookie `access_token`.
    """

    # Путь к кастомному классу аутентификации
    target_class = "users.authentication.CookieJWTAuthentication"
    # Имя стратегии в OpenAPI-схеме
    name = "CookieJWTAuth"

    def get_security_definition(self, auto_schema):
        """
        Возвращает описание схемы безопасности для OpenAPI.
        Указывает, что токен передаётся в cookie `access_token`.
        """
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
        }
