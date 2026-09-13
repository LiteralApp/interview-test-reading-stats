from rest_framework.routers import DefaultRouter

from .views import BookViewSet, StudentViewSet

router = DefaultRouter()
router.register("books", BookViewSet, basename="book")
router.register("students", StudentViewSet, basename="student")

urlpatterns = router.urls
