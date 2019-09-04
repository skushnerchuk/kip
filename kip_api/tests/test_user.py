import pytest
from kip_api.models.user import User


@pytest.mark.django_db
def test_my_user():
    with pytest.raises(User.DoesNotExist):
        User.objects.get(email='dr_coyote@mail.ru')
