from http import HTTPStatus

import pytest


from tests.utils import invalid_registration_data_fields


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
