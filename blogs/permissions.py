from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdmin(BasePermission):
    """
    Доступ к объекту:

    • **SAFE-методы** (GET, HEAD, OPTIONS) — разрешены всем.

    • **Изменение / удаление** — разрешено, если
        ─ пользователь -– staff или superuser; **или**
        ─ он является автором объекта
          (`author` *или* `user` поле) **или**
        ─ у объекта есть метод ``can_edit(user)``,
          который вернёт ``True``.
    """

    def has_object_permission(self, request, view, obj):
        # 1) Чтение доступно всегда
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user.is_authenticated:
            return False

        # 2) Админы / staff — полный доступ
        if user.is_staff or user.is_superuser:
            return True

        # 3) Универсальная проверка «я автор»
        for attr in ("author", "user"):
            author = getattr(obj, attr, None)
            if author and author == user:
                return True

        # 4) Объект сам знает, можно ли редактировать
        can_edit = getattr(obj, "can_edit", None)
        if callable(can_edit):
            return can_edit(user)

        return False
