
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    refresh.set_exp(from_time=datetime.now(), lifetime=timedelta(minutes=1200))
    refresh.access_token.set_exp(from_time=datetime.now(), lifetime=timedelta(minutes=600))

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }