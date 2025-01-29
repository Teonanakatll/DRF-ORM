import json

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.test.utils import CaptureQueriesContext

from gpt4.models import BookG
from gpt4.serializers import UserSerializer, BookGSerializer
from gpt4.utils import cons


class UserApiTestCase(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='User_1', first_name='Kri')
        self.user_2 = User.objects.create(username='User_2', first_name='Fox')
        self.admin = User.objects.create(username='Boss', first_name='Teon', last_name='Ko', is_staff=True)

        self.book_1 = BookG.objects.create(title='Book_1', pages=444, owner=self.user_1, content='Book_1 content')
        self.book_2 = BookG.objects.create(title='Book_2', pages=555, owner=self.user_1, content='Book_2 content')

        self.base_url = 'http://testserver'

    # получение данных юзера с правами администратора
    def test_detail_staff(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        context = {'request': response.wsgi_request}
        serializer_data = UserSerializer(self.user_1, context=context).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertIn('my_books', response.data)
        self.assertIn('read_list', response.data)

    # получение несуществующего пользователя
    def test_detail_wrong_user(self):
        url = reverse('user-detail', args=(100,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # получение данных юиера без прав администратора
    def test_get_detail_not_staff(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        context = {'request': response.wsgi_request}
        serializer_data = UserSerializer(self.user_1, context=context).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение данных юиера неавторизованным пользователем
    def test_get_detail_without_login(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        response = self.client.get(url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # получение списка юзеров с правами администратора
    def test_get_list(self):
        url = reverse('user-list')
        self.client.force_login(self.admin)

        # чтобы проверить сколько запросов происходит во время запроса, запустим response в контексте
        # CaptureQueriesContext — инструмент Django для мониторинга SQL-запросов, а connection — это
        # объект подключения к базе данных, будет логировать все SQL-зарпоссы во время его работы
        with CaptureQueriesContext(connection) as queries:
            # client это тестовый клиент для имитации http запросов к приложению в тестах, get - get запрос
            response = self.client.get(url)
            self.assertEqual(5, len(queries))

        context = {'request': response.wsgi_request}
        serializer_data = UserSerializer(User.objects.all(), context=context, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertIn('my_books', response.data[0])
        self.assertIn('read_list', response.data[0])

    # получение списка юзеров без прав админа
    def test_get_list_not_staff(self):
        url = reverse('user-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        context = {'request': response.wsgi_request}
        serializer_data = UserSerializer(User.objects.all(), context=context, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertIn('my_books', response.data[0])
        self.assertIn('read_list', response.data[0])

    # получение списка юзеров неавторизованым пользователем
    def test_get_list_without_login(self):
        url = reverse('user-list')

        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # PUT запрос, админом
    def test_put_admin(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('Fox', response.data['username'])
        self.assertEqual(2, len(response.data['my_books']))
        self.assertEqual([], response.data['read_list'])

    # PUT запрос, админом для изменения несуществующего пользователя
    def test_put_admin_wrong_id(self):
        url = reverse('user-detail', args=(100,))
        self.client.force_login(self.admin)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # PUT запрос, админом некорректными данными
    def test_put_admin_wrong_field(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        data = {
            'username': False
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        user = User.objects.get(id=self.user_1.id)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('User_1', user.username)

    # PUT запрос, изменение своих данных
    def test_put_own_user(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('Fox', response.data['username'])
        self.assertEqual(2, len(response.data['my_books']))
        self.assertEqual([], response.data['read_list'])

    # PUT запрос, изменение чужих данных
    def test_put_not_own_user(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.user_2)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        user = User.objects.get(id=self.user_1.id)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('User_1', user.username)

    # PUT запрос, изменение несуществующего пользователя, авторизованным пользователем
    def test_put_not_wrong_user(self):
        url = reverse('user-detail', args=(100,))
        self.client.force_login(self.user_1)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # PUT запрос, не авторизованным пользователем
    def test_put_without_login(self):
        url = reverse('user-detail', args=(self.user_1.id,))

        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # PUT запрос, админом
    def test_patch_admin(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('Fox', response.data['username'])
        self.assertEqual(2, len(response.data['my_books']))
        self.assertEqual([], response.data['read_list'])

    # PUT запрос, админом для изменения несуществующего пользователя
    def test_patch_admin_wrong_id(self):
        url = reverse('user-detail', args=(100,))
        self.client.force_login(self.admin)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # PUT запрос, админом некорректными данными
    def test_patch_admin_wrong_field(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        data = {
            'username': False
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        user = User.objects.get(id=self.user_1.id)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('User_1', user.username)

    # PUT запрос, изменение своих данных
    def test_patch_own_user(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('Fox', response.data['username'])
        self.assertEqual(2, len(response.data['my_books']))
        self.assertEqual([], response.data['read_list'])

    # PUT запрос, изменение чужих данных
    def test_patch_not_own_user(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.user_2)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        user = User.objects.get(id=self.user_1.id)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('User_1', user.username)

    # PUT запрос, изменение несуществующего пользователя, авторизованным пользователем
    def test_patch_not_wrong_user(self):
        url = reverse('user-detail', args=(100,))
        self.client.force_login(self.user_1)
        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # PUT запрос, не авторизованным пользователем
    def test_patch_without_login(self):
        url = reverse('user-detail', args=(self.user_1.id,))

        data = {
            'username': 'Fox'
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    ########################################### неразрешённые методы ################################333

    # неразрешённый POST запрос админом
    def test_post_not_allowed_admin(self):
        url = reverse('user-list')
        self.client.force_login(self.admin)
        data = {
            'username': 'Fox'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    # неразрешённый POST запрос авторизованным пользователем без прав
    def test_post_not_allowed_user(self):
        url = reverse('user-list')
        self.client.force_login(self.user_1)
        data = {
            'username': 'Fox'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual('method_not_allowed', response.data['detail'].code)

    # неразрешённый POST запрос не авторизованным пользователем
    def test_post_not_allowed_without_login(self):
        url = reverse('user-list')
        data = {
            'username': 'Fox'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # неразрешённый DELETE запрос, админом
    def test_delete_not_allowed(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual('method_not_allowed', response.data['detail'].code)

    # неразрешённый DELETE запрос, авторизованным пользователем без прав
    def test_delete_not_user(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual('method_not_allowed', response.data['detail'].code)

    # неразрешённый DELETE запрос, не авторизованным пользователем
    def test_delete_not_allowed_without_login(self):
        url = reverse('user-detail', args=(self.user_1.id,))

        response = self.client.delete(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)


#     ###################################### ТЕСТЫ ЭКШЕНА book ######################################
#
#
    # получение списка связанных книг экшена books хозяином
    def test_get_action_owner(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        serializer_data = BookGSerializer(BookG.objects.filter(owner_id=self.user_1.id), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение списка связанных книг экшена books не хозяином
    def test_get_action_owner_bad_id(self):
        url = reverse('user-list-books', args=(100,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('permission_denied', response.data['detail'].code)

    # получение списка чужих связанных книг экшена books не хозяином
    def test_get_action_not_owner(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_2)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('permission_denied', response.data['detail'].code)

    # получение списка чужих связанных книг экшена books неавторизованным пользователем
    def test_get_action_without_login(self):
        url = reverse('user-list-books', args=(self.user_1.id,))

        response = self.client.get(url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # получение списка связанных книг экшена books админом
    def test_get_action_staff(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        serializer_data = BookGSerializer(BookG.objects.filter(owner_id=self.user_1.id), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение списка связанных книг  несущуствующего пользователя экшена books админом
    def test_get_action_staff_wrong_id(self):
        url = reverse('user-list-books', args=(100,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        # cons(response.data)
        serializer_data = BookGSerializer(BookG.objects.filter(owner_id=self.user_1.id), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([], response.data)

    # ПРОВЕРКИ НЕДОПУСТИМЫХ МЕТОДОВ ЭКШЕНА book

    # неразрешённый POST запрос экшена books админом
    def test_post_action_not_allowed_admin(self):
        url = reverse('user-list-books', args=(1,))
        self.client.force_login(self.admin)
        data = {
            'username': 'Fox'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    # неразрешённый POST запрос экшена books авторизованным пользователем без прав
    def test_post_action_not_allowed_user(self):
        url = reverse('user-list-books', args=(1,))
        self.client.force_login(self.user_1)
        data = {
            'username': 'Fox'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('permission_denied', response.data['detail'].code)

    # неразрешённый POST запрос экшена books не авторизованным пользователем
    def test_post_action_not_allowed_without_login(self):
        url = reverse('user-list-books', args=(1,))
        data = {
            'username': 'Fox'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # неразрешённый PATCH запрос экшена books, админом
    def test_patch_action_not_allowed(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.patch(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual('method_not_allowed', response.data['detail'].code)

    # неразрешённый PATCH запрос экшена books, авторизованным пользователем без прав
    def test_patch_action_not_allowed_user(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.patch(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual('method_not_allowed', response.data['detail'].code)

    # неразрешённый PATCH запрос экшена books, не авторизованным пользователем
    def test_patch_action_not_allowed_without_login(self):
        url = reverse('user-list-books', args=(self.user_1.id,))

        response = self.client.patch(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # неразрешённый PUT запрос экшена books, админом
    def test_put_action_not_allowed(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.put(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    # неразрешённый PUT запрос экшена books, авторизованным пользователем без прав
    def test_put_action_not_allowed_user(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.put(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual('method_not_allowed', response.data['detail'].code)

    # неразрешённый PUT запрос экшена books, не авторизованным пользователем
    def test_put_action_not_allowed_without_login(self):
        url = reverse('user-list-books', args=(self.user_1.id,))

        response = self.client.put(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # неразрешённый DELETE запрос экшена books, админом
    def test_delete_action_not_allowed(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    # неразрешённый DELETE запрос экшена books, авторизованным пользователем без прав
    def test_delete_action_not_allowed_user(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual('method_not_allowed', response.data['detail'].code)

    # неразрешённый DELETE запрос экшена books, не авторизованным пользователем
    def test_delete_action_not_allowed_without_login(self):
        url = reverse('user-list-books', args=(self.user_1.id,))

        response = self.client.delete(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)
