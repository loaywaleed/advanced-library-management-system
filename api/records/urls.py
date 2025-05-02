from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BorrowingRecordViewSet

router = SimpleRouter()

router.register(r"borrowings", BorrowingRecordViewSet, basename="borrowing-records")


urlpatterns = [
    path("", include(router.urls)),
]
