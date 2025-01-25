"""
URL configuration for books project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from gpt4.views import BookGViewSet, UserBookGRelationVew, UserView, GenreViewSet, AuthorViewSet
from store.views import auth, logout_github_view

from store.views import BookViewSet, UserBookRelationView

# слушай мне авторизации даются очень не легко, давай я подведу итоги того что понял на данный момент а ты если что
# поправишь. авторизация\регистрация\логаут через джанго auth и django_social происходит с помощю сессий и цсрф, только
# сам вход в систему\регистрация\логаут в случае с django auth происходит через формы самого джанго или эндпоинтов
# предоставляемых дрф, в случае с django_social django настроен на то чтобы делегировать регистрацию и авторизацию
# внешним довененным проверенным времени ресурсам а сам при получении подтверждения на вход в доверенный ресурс создаёт
# аккаунт или активирует если такой пользователь уже есть и выдаёт ключи сессии и цсрф, в ручную необходимо прописать
# ендпоинт для выхода из системы, я правильно понимаю?
# X-CSRFToken - token из постмена, Cookie  -  sessionid=... из браузера

router = SimpleRouter()
# Book !!!!!!!!!!!!!
router.register(r'book', BookViewSet)
router.register(r'book_relation', UserBookRelationView)
router.register(r'api/bookg', BookGViewSet, basename='bookg')
router.register(r'api/bookg/relations', UserBookGRelationVew, basename='bookg-relation')
router.register(r'api/genre', GenreViewSet, basename='genre')
router.register(r'api/author', AuthorViewSet, basename='author')
router.register(r'api/users', UserView, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),

    # авторизация djoser и таблицами drf
    # path('auth/', include('djoser.urls')),  # Базовые маршруты Djoser
    # path('auth/', include('djoser.urls.authtoken')),  # Маршруты для токенов

    #
    # стандартные моршруты дрф для входа (форма) и выхода, через post запроссы только браузер дрф
    # path('session_auth/', include('rest_framework.urls')),

    # # пути django-social
    # path('social_django/', include('social_django.urls', namespace='social')),
    # # шаблон авторизации
    # path('auth_temp/', auth),
    # path('logout/github/', logout_github_view, name='logout_github'),  # кастомный маршрут выхода

    # path('my/', include('gpt4.urls')),
    # path('che/', include('store.urls'))
]

urlpatterns += router.urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
