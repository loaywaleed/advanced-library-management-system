from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    BookViewSet,
    AuthorViewSet,
    # CategoryViewSet,
    LibraryViewSet,
)

router = SimpleRouter()

router.register(r"libraries", LibraryViewSet, basename="library")
router.register(r"books", BookViewSet, basename="book")
router.register(r"authors", AuthorViewSet, basename="author")


urlpatterns = [
    path("", include(router.urls)),
]
