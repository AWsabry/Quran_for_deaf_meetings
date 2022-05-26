import time
import random
import string
from typing import Tuple

from django.conf import settings
from django.utils.text import slugify

from agora_token_builder import RtcTokenBuilder


def generate_random_str(length: int = 12) -> str:
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for _ in range(length))


def random_str_shuffle(s: str, length: int = 20) -> str:
    lst = list(s)
    random.shuffle(lst)
    final_string = slugify(''.join(lst))
    return final_string[:length]


def generate_agora_token(channel_name: str, expiration_time: float = None) -> Tuple[str, int]:
    uid = random.randint(1, 230)
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE
    default_expiration_time = settings.AGORA_EXPIRATION_TIME
    increase_time = settings.AGORA_INCREASE_TIME
    expiration_time = (expiration_time or int(time.time()) + default_expiration_time) + increase_time
    role = 1
    token = RtcTokenBuilder.buildTokenWithUid(app_id, app_certificate, channel_name, uid, role, expiration_time)
    return token, uid
