import os
import base64
import pytz
import datetime
import time

from flask import request
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask_login import current_user
from dateutil.tz import tzlocal
from jose import jwt
from ..default_settings import JWT_SECRET
from decimal import Decimal
from re import sub

def jwt_decode(token, secret_key=JWT_SECRET, algorithms='HS512'):
    options = {
        'verify_signature': False
    }

    decode_value = jwt.decode(token=token, key=secret_key, algorithms=algorithms,
                              options=options, audience='web', issuer='atlas-auth-server')
    return decode_value


def user_logged_in():
    return current_user.name if current_user is not None else 'REST-API'


def current_timestamp_tz():
    now = datetime.datetime.now().replace(tzinfo=tzlocal())
    return now.astimezone(pytz.timezone('America/Sao_Paulo'))


def current_request_ip():
    if 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'

    return remote_addr


def epoch_to_date(value):
    if value:
        date = datetime.datetime.fromtimestamp(value).strftime('%d/%m/%Y %H:%M:%S')
        return date
    return None


def generate_secret_key():
    """
        Return a random URL-safe text string, in Base64 encoding.
        The string has *nbytes* random bytes.

    :return: secret key
    """
    token = os.urandom(32)
    key = base64.urlsafe_b64encode(token).rstrip(b'=').decode('ascii')
    return key


def json_default(value):
    if isinstance(value, datetime.date) or isinstance(value, Decimal):
        return value.__str__()
    else:
        return value.__dict__


def convert_to_currency(money):
    try:
        money = money.replace('.', '')
        money = money.replace(',', '.')
        return Decimal(sub(r'[^\d\-.]', '', money))
    except Exception as e:
        return 0


def create_date_object(str_date, str_format='%d-%m-%Y'):
    time_stamp = time.mktime(time.strptime(str_date, str_format))
    return datetime.datetime.fromtimestamp(time_stamp)

