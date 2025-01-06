from rest_framework.routers import DefaultRouter

from gpt4.views import BookGViewSet

router = DefaultRouter()
router.register(r'book', BookGViewSet, basename='my')

urlpatterns = router.urls
