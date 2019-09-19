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
