from django.urls import path

from rooms.views import RoomPhotoViewSet, RoomViewSet

urlpatterns = [
    path(
        "<int:hotel_id>/rooms/",
        RoomViewSet.as_view({"get": "list", "post": "create"}),
        name="rooms-list",
    ),
    path(
        "<int:hotel_id>/rooms/<int:pk>/",
        RoomViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="rooms-detail",
    ),
    path(
        "rooms/<int:room_id>/photos/",
        RoomPhotoViewSet.as_view({"get": "list", "post": "create"}),
        name="rooms-photos-list",
    ),
    path(
        "rooms/<int:room_id>/photos/<int:pk>/",
        RoomPhotoViewSet.as_view({"delete": "destroy"}),
        name="rooms-photo-detail",
    ),
]
