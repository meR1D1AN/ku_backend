from django.urls import path

from guests.views import GuestViewSet

urlpatterns = [
    path(
        "<int:user_id>/guests/",
        GuestViewSet.as_view({"get": "list", "post": "create"}),
        name="user-guests-list",
    ),
    path(
        "<int:user_id>/guests/<int:pk>/",
        GuestViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="user-guests-detail",
    ),
]
