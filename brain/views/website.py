from flask import Blueprint, render_template
from brain.util.library import epoch_to_date
from flask_login import login_required, login_user, logout_user
import locale
from .client_api import RoleResource, UserResource, BuyOptionResource, DealResource
from ..util.library import current_timestamp_tz


website = Blueprint('website', __name__)


@website.route('/')
@login_required
def index():
    deals = DealResource().list_all_available()
    return render_template('website/index.html', deals=deals)


@website.app_template_filter()
def epoch2date(value):
    return epoch_to_date(value)


@website.app_template_filter()
def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    return 'R$ ' + locale.currency(value, grouping=True, symbol=False)


@website.app_template_filter()
def date_greater_than_now(value):
    param_date = value.strftime("%Y-%m-%d")
    current_date = current_timestamp_tz().strftime("%Y-%m-%d")
    return param_date > current_date


@website.app_template_filter()
def date_lower_than_now(value):
    param_date = value.strftime("%Y-%m-%d")
    current_date = current_timestamp_tz().strftime("%Y-%m-%d")
    return param_date < current_date
