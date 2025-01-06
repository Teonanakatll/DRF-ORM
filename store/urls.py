from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, UserBookRelationView

router = SimpleRouter()

router.register(r'book', BookViewSet, basename='che')
router.register(r'book_relation', UserBookRelationView, basename='she')

urlpatterns = router.urls
