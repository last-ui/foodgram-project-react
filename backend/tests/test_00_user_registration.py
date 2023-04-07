from http import HTTPStatus

import pytest
from django.db.utils import IntegrityError

from tests.utils import (invalid_data_for_user_patch_and_creation,
                         invalid_registration_data_fields)


@pytest.mark.django_db(transaction=True)
class Test00UserRegistration:
    url_signup = '/api/users/'
    url_set_password = '/api/users/set_password/'
    url_token = '/api/auth/token/login/'

    def test_00_nodata_signup(self, client):
        response = client.post(self.url_signup)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос, отправленный на эндпоинт `{self.url_signup}`, '
            'не содержит необходимых данных, должен вернуться ответ со '
            'статусом 400.'
        )
        response_json = response.json()
        empty_fields = ['email', 'username', 'first_name', 'last_name',
                        'password']
        for field in empty_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в POST-запросе к `{self.url_signup}` не переданы '
                'необходимые данные, в ответе должна возвращаться информация '
                'об обязательных для заполнения полях.'
            )

    def test_00_invalid_data_signup(self, client, django_user_model):
        valid_email = 'validemail@foodgram.fake'
        valid_username = 'valid_username'
        valid_firstname = 'valid_firstname'
        valid_last_name = 'last_name'

        invalid_email = 'invalid_email'
        invalid_username = ',$,'
        invalid_firstname = ' '
        invalid_last_name = ' '
        invalid_password = '1234567'

        invalid_data = {
            'email': invalid_email,
            'username': invalid_username,
            'first_name': invalid_firstname,
            'last_name': invalid_last_name,
            'password': invalid_password,
        }
        users_count = django_user_model.objects.count()

        response = client.post(self.url_signup, data=invalid_data)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к эндпоинту `{self.url_signup}` содержит '
            'некорректные данные, должен вернуться ответ со статусом 400.'
        )
        assert users_count == django_user_model.objects.count(), (
            f'Проверьте, что POST-запрос к `{self.url_signup}` с '
            'некорректными данными не создаёт нового пользователя.'
        )

        response_json = response.json()
        invalid_fields = ['email', 'username', 'first_name', 'last_name']
        for field in invalid_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в  POST-запросе к `{self.url_signup}` переданы '
                'некорректные данные, в ответе должна возвращаться информация '
                'о неправильно заполненных полях.'
            )
        invalid_data = {
            'email': valid_email,
            'username': valid_username,
            'first_name': valid_firstname,
            'last_name': valid_last_name,
            'password': invalid_password,
        }
        response = client.post(self.url_signup, data=invalid_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к `{self.url_signup}` не содержит '
            'данных о `password`, должен вернуться ответ со статусом 400.'
        )
        assert users_count == django_user_model.objects.count(), (
            f'Проверьте, что POST-запрос к `{self.url_signup}`, не содержащий '
            'данных о `password`, не создаёт нового пользователя.'
        )

    @pytest.mark.parametrize(
        'data,message', invalid_registration_data_fields
    )
    def test_00_singup_length_and_simbols_validation(self, client,
                                                     data, message,
                                                     django_user_model):
        request_method = 'POST'
        users_count = django_user_model.objects.count()
        response = client.post(self.url_signup, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            message[0].format(
                url=self.url_signup, request_method=request_method
            )
        )
        assert django_user_model.objects.count() == users_count, (
            f'Если в POST-запросе к эндпоинту `{self.url_signup}` '
            'значения полей не соответствуют ограничениям по длине или '
            'содержанию - новый пользователь не должен быть создан.'
        )

    def test_00_valid_data_user_signup(self, client, django_user_model):
        valid_data = {
            'email': 'valid@yamdb.fake',
            'username': 'valid_username',
            'first_name': 'valid_first_name',
            'last_name': 'valid_last_name',
            'password': '2mv-feX9YNCz',
        }
        valid_response = {
            'email': 'valid@yamdb.fake',
            'username': 'valid_username',
            'first_name': 'valid_first_name',
            'last_name': 'valid_last_name',
            'id': 1,
        }

        response = client.post(self.url_signup, data=valid_data)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.CREATED, (
            'POST-запрос с корректными данными, отправленный на эндпоинт '
            f'`{self.url_signup}`, должен вернуть ответ со статусом 201.'
        )
        assert response.json() == valid_response, (
            'POST-запрос с корректными данными, отправленный на эндпоинт '
            f'`{self.url_signup}`, должен вернуть ответ, содержащий '
            'информацию о `id`, `username`, `email`, `first_name` и '
            '`last_name` созданного пользователя.'
        )

        new_user = django_user_model.objects.filter(email=valid_data['email'])
        assert new_user.exists(), (
            'POST-запрос с корректными данными, отправленный на эндпоинт '
            f'`{self.url_signup}`, должен создать нового пользователя.'
        )
        new_user.delete()

    # def test_00_valid_data_set_password(self, client, django_user_model):
    #     valid_data = {
    #         'new_password': 'valid@yamdb.fake',
    #         'current_password': '2mv-feX9YNCz',
    #         'first_name': 'valid_first_name',
    #         'last_name': 'valid_last_name',
    #         'password': '2mv-feX9YNCz',
    #     }
    #
    #     response = client.post(self.url_signup, data=valid_data)
    #
    #     assert response.status_code != HTTPStatus.NOT_FOUND, (
    #         f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
    #         'в *urls.py*.'
    #     )
    #
    #     assert response.status_code == HTTPStatus.CREATED, (
    #         'POST-запрос с корректными данными, отправленный на эндпоинт '
    #         f'`{self.url_signup}`, должен вернуть ответ со статусом 201.'
    #     )
    #     assert response.json() == valid_response, (
    #         'POST-запрос с корректными данными, отправленный на эндпоинт '
    #         f'`{self.url_signup}`, должен вернуть ответ, содержащий '
    #         'информацию о `id`, `username`, `email`, `first_name` и '
    #         '`last_name` созданного пользователя.'
    #     )
    #
    #     new_user = django_user_model.objects.filter(email=valid_data['email'])
    #     assert new_user.exists(), (
    #         'POST-запрос с корректными данными, отправленный на эндпоинт '
    #         f'`{self.url_signup}`, должен создать нового пользователя.'
    #     )
    #     new_user.delete()

    # @pytest.mark.parametrize(
    #     'data,messege', invalid_data_for_user_patch_and_creation
    # )
    # def test_00_admin_create_user_length_and_simbols_validation(
    #         self, admin_client, data, messege, django_user_model
    # ):
    #     request_method = 'POST'
    #     users_count = django_user_model.objects.count()
    #     response = admin_client.post(self.url_admin_create_user, data=data)
    #     assert response.status_code == HTTPStatus.BAD_REQUEST, (
    #         messege[0].format(
    #             url=self.url_admin_create_user, request_method=request_method
    #         )
    #     )
    #     assert django_user_model.objects.count() == users_count, (
    #         'Если значения полей в POST-запросе, отправленном на эндпоинт '
    #         f'`{self.url_admin_create_user}`, не соответствуют ограничениям '
    #         'по длине или содержанию, новый пользователь не должен быть '
    #         'создан.'
    #     )
    #
    # def test_00_obtain_jwt_token_invalid_data(self, client):
    #     response = client.post(self.url_token)
    #     assert response.status_code != HTTPStatus.NOT_FOUND, (
    #         f'Эндпоинт `{self.url_token}` не найдена. Проверьте настройки в '
    #         '*urls.py*.'
    #     )
    #
    #     assert response.status_code == HTTPStatus.BAD_REQUEST, (
    #         'Проверьте, что POST-запрос без данных, отправленный на эндпоинт '
    #         f'`{self.url_token}`, возвращает ответ со статусом 400.'
    #     )
    #
    #     invalid_data = {
    #         'confirmation_code': 12345
    #     }
    #     response = client.post(self.url_token, data=invalid_data)
    #     assert response.status_code == HTTPStatus.BAD_REQUEST, (
    #         'Проверьте, что POST-запрос, отправленный на эндпоинт '
    #         f'`{self.url_token}`и не содержащий информации о `username`, '
    #         'возвращает ответ со статусом 400.'
    #     )
    #
    #     invalid_data = {
    #         'username': 'unexisting_user',
    #         'confirmation_code': 12345
    #     }
    #     response = client.post(self.url_token, data=invalid_data)
    #     assert response.status_code == HTTPStatus.NOT_FOUND, (
    #         'Проверьте, что POST-запрос с несуществующим `username`, '
    #         f'отправленный на эндпоинт `{self.url_token}`, возвращает ответ '
    #         'со статусом 404.'
    #     )
    #
    #     valid_data = {
    #         'email': 'valid@yamdb.fake',
    #         'username': 'valid_username'
    #     }
    #     response = client.post(self.url_signup, data=valid_data)
    #     assert response.status_code == HTTPStatus.OK, (
    #         'Проверьте, что POST-запрос с корректными данными, отправленный '
    #         f'на `{self.url_signup}`, возвращает ответ со статусом 200.'
    #     )
    #
    #     invalid_data = {
    #         'username': valid_data['username'],
    #         'confirmation_code': 12345
    #     }
    #     response = client.post(self.url_token, data=invalid_data)
    #     assert response.status_code == HTTPStatus.BAD_REQUEST, (
    #         'Проверьте, что POST-запрос с корректным `username` и невалидным '
    #         f'`confirmation_code`, отправленный на эндпоинт `{self.url_token}`'
    #         ', возвращает ответ со статусом 400.'
    #     )
    #
    # def test_00_registration_me_username_restricted(self, client):
    #     valid_data = {
    #         'email': 'valid@yamdb.fake',
    #         'username': 'me'
    #     }
    #     response = client.post(self.url_signup, data=valid_data)
    #     assert response.status_code == HTTPStatus.BAD_REQUEST, (
    #         'Если в POST-запросе, отправленном на эндпоинт '
    #         f'`{self.url_signup}`, значением поля `username` указано `me` - '
    #         'должен вернуться ответ со статусом 400.'
    #     )
    #
    # def test_00_registration_same_email_restricted(self, client):
    #     valid_email_1 = 'test_duplicate_1@yamdb.fake'
    #     valid_email_2 = 'test_duplicate_2@yamdb.fake'
    #     valid_username_1 = 'valid_username_1'
    #     valid_username_2 = 'valid_username_2'
    #
    #     valid_data = {
    #         'email': valid_email_1,
    #         'username': valid_username_1
    #     }
    #     response = client.post(self.url_signup, data=valid_data)
    #     assert response.status_code == HTTPStatus.OK, (
    #         f'Проверьте, что POST-запрос к `{self.url_signup}` с корректными '
    #         'возвращает статус-код 200.'
    #     )
    #
    #     duplicate_email_data = {
    #         'email': valid_email_1,
    #         'username': valid_username_2
    #     }
    #     assert_msg = (
    #         f'Если POST-запрос, отправленный на эндпоинт `{self.url_signup}`, '
    #         'содержит `email` зарегистрированного пользователя и незанятый '
    #         '`username` - должен вернуться ответ со статусом 400.'
    #     )
    #     try:
    #         response = client.post(self.url_signup, data=duplicate_email_data)
    #     except IntegrityError:
    #         raise AssertionError(assert_msg)
    #     assert response.status_code == HTTPStatus.BAD_REQUEST, (assert_msg)
    #
    #     duplicate_username_data = {
    #         'email': valid_email_2,
    #         'username': valid_username_1
    #     }
    #     assert_msg = (
    #         f'Если POST-запрос, отправленный на эндпоинт `{self.url_signup}`, '
    #         'содержит `username` зарегистрированного пользователя и '
    #         'несоответствующий ему `email` - должен вернуться ответ со '
    #         'статусом 400.'
    #     )
    #     try:
    #         response = client.post(
    #             self.url_signup, data=duplicate_username_data
    #         )
    #     except IntegrityError:
    #         raise AssertionError(assert_msg)
    #     assert response.status_code == HTTPStatus.BAD_REQUEST, (assert_msg)
    #
    # def test_get_new_confirmation_code_for_existing_user(self, client):
    #     valid_data = {
    #         'email': 'test_email@yamdb.fake',
    #         'username': 'valid_username_1'
    #     }
    #     response = client.post(self.url_signup, data=valid_data)
    #     assert response.status_code == HTTPStatus.OK, (
    #         'Проверьте, что POST-запрос с корректными данными, отправленный '
    #         f'на эндпоинт `{self.url_signup}`, возвращает ответ со статусом '
    #         '200.'
    #     )
    #
    #     response = client.post(self.url_signup, data=valid_data)
    #     assert response.status_code == HTTPStatus.OK, (
    #         f'Проверьте, что повторный POST-запрос к `{self.url_signup}` с '
    #         'данными зарегистрированного пользователя возвращает ответ со '
    #         'статусом 200.'
    #     )
    #
    # def test_get_confirmation_code_for_user_created_by_admin(
    #         self, admin_client, client, django_user_model
    # ):
    #     user_cnt = django_user_model.objects.count()
    #     valid_data = {
    #         'email': 'test_email@yamdb.fake',
    #         'username': 'valid_username_1'
    #     }
    #     admin_client.post(self.url_admin_create_user, data=valid_data)
    #     assert (user_cnt + 1) == django_user_model.objects.count(), (
    #         'Если POST-запрос администратора на эндпоинт '
    #         f'`{self.url_admin_create_user}` содержит корректные данные - '
    #         'должен быть создан новый пользователь.'
    #     )
    #
    #     response = client.post(self.url_signup, data=valid_data)
    #     assert response.status_code == HTTPStatus.OK, (
    #         f'Проверьте, что POST-запрос к {self.url_signup} с данными '
    #         'пользователя, созданного администратором,  возвращает ответ '
    #         'со статусом 200.'
    #     )
