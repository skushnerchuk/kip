from kip_api.models.user import User, Profile


def test_user_str_method(correct_login):
    user = User.objects.first()
    assert user.__str__() == correct_login['email']


def test_profile_str_method(correct_login):
    user = User.objects.first()
    profile = Profile.objects.get(user_id=user.id)
    assert profile.__str__() == f'Профиль: {correct_login["email"]}'
