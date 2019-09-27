# Точки входа API
ENDPOINTS = [
    ('/api/v1/auth/register/', 'register'),
    ('/api/v1/auth/login/', 'login'),
    ('/api/v1/auth/logout/', 'logout'),
    ('/api/v1/user/', 'user_detail'),
    ('/api/v1/user/update/', 'user_update')
]

# Корректный запрос для авторизации
CORRECT_LOGIN_BODY = {
    'email': 'username@example.com',
    'password': '1234567890'
}

# Некорректные запросы для регистрации
INCORRECT_REGISTER_BODY = [
    {'email': 'username_example.com', 'password': '1234567890'},
    {'email': 'username@example.com', 'password': ''},
    {'email': '', 'password': ''},
    {'e_mail': 'username@example.com', 'pa_ssword': '1234567890'},
    'This is string for crash',
    None,
    [],
]

UPDATE_PROFILE_BODY = {
    'biography': 'My biography',
    'birth_date': '1975-01-01',
    'first_name': 'First Name',
    'middle_name': 'Middle Name',
    'last_name': 'Last Name'
}

#
# Заголовки запроса для тестирования загрузки аватара
#
UPLOAD_AVATAR_HEADERS = \
    {
        'HTTP_CONTENT_TYPE': 'image/jpeg',
        'HTTP_CONTENT_DISPOSITION': 'attachment; filename=avatar.jpg'
    }

INCORRECT_UPLOAD_AVATAR_HEADERS = [
    {
        'HTTP_CONTENT_TYPE': 'unsupported-content-type',
        'HTTP_CONTENT_DISPOSITION': 'filename=avatar.png'
    },
    {
        'HTTP_CONTENT_TYPE': '',
        'HTTP_CONTENT_DISPOSITION': 'attachment; file=avatar.jpg'
    },
    {
        'HTTP_CONTENT_TYPE': '',
    },
    {
        'HTTP_CONTENT_DISPOSITION': ''
    },
    {

    }
]
