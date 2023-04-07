invalid_registration_data_fields = [
    (
        {
            'email': ('a' * 244) + '@foodgram.fake',
            'username': 'valid-username',
            'first_name': 'valid-firstname',
            'last_name': 'valid-lastname',
            'password': 'cK>SJDGccsc19'
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'проверяется длина поля `email`: его содержимое не должно быть '
            'длиннее 254 символа.'
        ),)
    ),
    (
        {
            'email': 'valid-email@foodgram.fake',
            'username': ('a' * 151),
            'first_name': 'valid-firstname',
            'last_name': 'valid-lastname',
            'password': 'cK>SJDGccsc19'
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'проверяется длина поля `username`: его содержимое не должно быть '
            'длиннее 150 символов.'
        ),)
    ),
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': '|-|aTa|_|_|a',
            'first_name': 'valid-firstname',
            'last_name': 'valid-lastname',
            'password': 'cK>SJDGccsc19'
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'содержание поля `username` проверяется на соответствие '
            'паттерну, указанному в спецификации: ^[\\w.@+-]+\\z'
        ),)
    ),
    (
        {
            'email': 'valid-email@foodgram.fake',
            'username': 'valid-username',
            'first_name': ('a' * 151),
            'last_name': 'valid-lastname',
            'password': 'cK>SJDGccsc19'
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'проверяется длина поля `first_name`: его содержимое не должно '
            'быть длиннее 150 символов.'
        ),)
    ),
    (
        {
            'email': 'valid-email@foodgram.fake',
            'username': 'valid-username',
            'first_name': 'valid-firstname',
            'last_name': ('a' * 151),
            'password': 'cK>SJDGccsc19'
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'проверяется длина поля `last_name`: его содержимое не должно '
            'быть длиннее 150 символов.'
        ),)
    ),
    (
        {
            'email': 'valid-email@foodgram.fake',
            'username': 'valid-username',
            'first_name': 'valid-firstname',
            'last_name': 'valid-lastname',
            'password': ('cK>SJDGc195' * 15)
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'проверяется длина поля `password`: его содержимое не должно '
            'быть длиннее 150 символов.'
        ),)
    )
]
