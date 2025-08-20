from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomLOPagination(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)

        # Если limit и offset не указаны, возвращаем все объекты
        if self.limit is None:
            self.count = queryset.count()
            return list(queryset)

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        # Если пагинация отключена, возвращаем все объекты с метаданными
        if self.limit is None:
            return Response({"count": self.count, "next": None, "previous": None, "results": data})

        return super().get_paginated_response(data)
