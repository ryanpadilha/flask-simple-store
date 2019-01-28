import weakref

from flask import flash
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectMultipleField, \
    BooleanField, HiddenField, SelectField, FileField, FieldList, DateField, TextAreaField

from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed
from .views.client_api import RoleResource
from wtforms.fields.html5 import EmailField, IntegerField, URLField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired, NumberRange, Optional
from enum import Enum
from .util.library import convert_to_currency, current_timestamp_tz
from .views.client_api import RoleResource, UserResource, BuyOptionResource, DealResource


def my_strip_filter(value):
    if value is not None and hasattr(value, 'strip'):
        return value.strip()
    return value


class BaseForm(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            # We don't set default filters for query-based fields as it breaks them if no query_factory is set
            # while the Form is instantiated. Also, it's quite pointless for those fields...
            # FieldList simply doesn't support filters.
            no_filter_fields = FieldList  # QuerySelectField
            filters = [my_strip_filter] if not issubclass(unbound_field.field_class, no_filter_fields) else []
            filters += unbound_field.kwargs.get('filters', [])
            bound = unbound_field.bind(form=form, filters=filters, **options)
            bound.get_form = weakref.ref(form)  # GC won't collect the form if we don't use a weakref
            return bound


class LoginForm(FlaskForm):
    email = StringField(u'Email ou telefone', validators=[DataRequired(u'Informe o e-mail ou telefone')])
    password = PasswordField(u'Senha', validators=[DataRequired(u'Informe a senha')])
    remember_me = BooleanField(u'Permanecer logado')


class BuyOptionForm(BaseForm):
    id = HiddenField()
    title = StringField(u'Título *', validators=[DataRequired(u'Informe o título')])
    normal_price = StringField('Preço de Venda Normal *', validators=[Optional()], default='0')
    sale_price = StringField('Preço de Venda Final *', validators=[Optional()], default='0')
    percentage_discount = StringField('Percentual de Desconto *', validators=[Optional()], default='0')
    quantity_cupom = IntegerField('Quantidade de Cupons *', validators=[NumberRange(min=1, max=99999, message='Quantidade de cupom deve ser no mínimo 1'), InputRequired('Informe um número válido')], default=1)
    start_date = DateField(u'Data de Publicação *', format='%d/%m/%Y', validators=[DataRequired(u'Informe uma data de publicação')])
    end_date = DateField(u'Data de Expiração *', format='%d/%m/%Y', validators=[DataRequired(u'Informe uma data de expiração')])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        valid = True

        if self.quantity_cupom.data and int(self.quantity_cupom.data) <= 0:
            self.quantity_cupom.errors.append('Quantidade de cupom deve ser maior que 0')
            valid = False

        if self.normal_price.data and convert_to_currency(self.normal_price.data) <= 0:
            self.normal_price.errors.append('Preço de venda normal deve ser maior que 0')
            valid = False

        if self.sale_price.data and convert_to_currency(self.sale_price.data) <= 0:
            self.sale_price.errors.append('Preço de venda final deve ser maior que 0')
            valid = False

        if self.percentage_discount.data and convert_to_currency(self.percentage_discount.data) > 100:
            self.percentage_discount.errors.append('Percentual de desconto não deve ser maior que 100')
            valid = False

        if self.percentage_discount.data and convert_to_currency(self.percentage_discount.data) < 0:
            self.percentage_discount.errors.append('Percentual de desconto deve ser maior que 0')
            valid = False

        if convert_to_currency(self.sale_price.data) > convert_to_currency(self.normal_price.data):
            self.sale_price.errors.append('Preço de venda deve ser menor ou igual que preço de venda')
            valid = False

        if self.start_date.data < current_timestamp_tz().date():
            self.start_date.errors.append('Data de publicação deve ser maior que data atual')
            valid = False

        if self.end_date.data and self.start_date.data:
            if self.end_date.data <= self.start_date.data:
                self.end_date.errors.append('Data de expiração deve ser maior que data de publicação')
                valid = False

        return valid


class FlashMessagesCategory(Enum):
    MESSAGE = 'message'
    ERROR = 'error'
    INFO = 'info'
    WARNING = 'warning'


class StatusType(Enum):
    LOCAL = ('LOCAL', 'Oferta Local')
    PRODUCT = ('PRODUCT', 'Oferta de Produto')
    TRAVEL = ('TRAVEL', 'Oferta de Viagem')

    @staticmethod
    def list():
        return list(map(lambda c: c.value, StatusType))


class DealForm(BaseForm):
    id = HiddenField()
    h_total_sold = HiddenField()
    h_url = HiddenField()
    title = StringField(u'Título *', validators=[DataRequired(u'Informe o título')])
    url = StringField(u'URL *')
    total_sold = IntegerField('Total Vendido *', default=0)
    text = TextAreaField(u'Descritivo Principal *', validators=[DataRequired(u'Informe um descritivo principal')])
    publish_date = DateField(u'Data de Publicação *', format='%d/%m/%Y', validators=[DataRequired(u'Informe uma data de publicação')])
    end_date = DateField(u'Data de Expiração *', format='%d/%m/%Y', validators=[DataRequired(u'Informe uma data de expiração')])
    type = SelectField(u'Tipo *', coerce=str, default='LOCAL')
    options = SelectMultipleField(u'Opções de Compra', coerce=str)

    def __init__(self, **kwargs):
        super(DealForm, self).__init__(**kwargs)
        self.type.choices = StatusType.list()

        collection = BuyOptionResource().list_all_available()
        self.options.choices = [(o.id, o.title) for o in collection]

    def validate(self):
        rv = FlaskForm.validate(self)
        self.url.data = self.h_url.data

        if not rv:
            return False

        valid = True

        if self.publish_date.data < current_timestamp_tz().date():
            self.publish_date.errors.append('Data de publicação deve ser maior que data atual')
            valid = False

        if self.end_date.data and self.publish_date.data:
            if self.end_date.data <= self.publish_date.data:
                self.end_date.errors.append('Data de expiração deve ser maior que data de publicação')
                valid = False

        return valid


class RoleForm(BaseForm):
    internal = HiddenField()
    name = StringField(u'Nome *', validators=[DataRequired(u'Informe o nome')])
    type = StringField(u'Sigla (25 caracteres) *', validators=[DataRequired(u'Informe a sigla'),
                                                              Length(min=1, max=25, message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres')])
    description = StringField(u'Descrição')


class UserEditForm(FlaskForm):
    internal = HiddenField()
    active = SelectField(u'Situação *', coerce=int, default=1)
    name = StringField(u'Nome Completo *', validators=[DataRequired(u'Informe o nome completo')])
    user_email = StringField(u'E-mail *',
                             validators=[DataRequired(u'Informe o e-mail'), Email(u'Endereço de e-mail inválido')])
    photo = FileField(u'Foto do Perfil') # validators=[FileAllowed(f_images, 'Selecione apenas imagens')]
    company = StringField(u'Empresa')
    occupation = StringField(u'Cargo')
    phone = StringField(u'Telefone Celular *', validators=[DataRequired(u'Informe o telefone')])
    document_main = StringField(u'CPF')
    roles = SelectMultipleField(u'Papeis *', coerce=str,
                                validators=[DataRequired(u'Selecione pelo menos um papel')])

    def __init__(self, **kwargs):
        super(UserEditForm, self).__init__(**kwargs)
        self.roles.choices = [(g.type, g.name) for g in RoleResource().list()]
        self.active.choices = [(1, u'Ativo'),(0, u'Inativo')]


class UserForm(UserEditForm):
    user_password = PasswordField(u'Senha *', validators=[DataRequired(u'Informe uma senha'),
                                                          Length(min=6, max=20,
                                                                 message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres')])

    confirm_password = PasswordField(u'Confirmar Senha *', validators=[DataRequired(u'Informe um confirmar senha'),
                                                                       Length(min=6, max=20,
                                                                              message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres'),
                                                                       EqualTo('user_password',
                                                                               u'A confirmação de senha não confere')])


class UserChangePasswordForm(FlaskForm):
    current_password = PasswordField(u'Senha Atual *', validators=[DataRequired(u'Informe a senha atual'),
                                                                   Length(min=6, max=20,
                                                                          message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres')])

    user_password = PasswordField(u'Nova Senha *', validators=[DataRequired(u'Informe a nova senha'),
                                                               Length(min=6, max=20,
                                                                      message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres')])

    confirm_password = PasswordField(u'Confirmar Nova Senha *', validators=[DataRequired(u'Informe um confirmar senha'),
                                                                            Length(min=6, max=20,
                                                                                   message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres'),
                                                                            EqualTo('user_password',
                                                                               u'A confirmação de senha não confere')])
