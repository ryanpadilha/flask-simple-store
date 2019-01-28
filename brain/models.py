import json

from flask_login import UserMixin
from .integrations import build_service_unavailable_message_rest
from .util.library import create_date_object


class Credential(object):
    def __init__(self, provider, authorization, expires):
        self.provider = provider
        self.authorization = authorization
        self.expires = expires

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @classmethod
    def from_dict(cls, json_data):
        provider = json_data.get('provider')
        authorization = json_data.get('authorization')
        expires = json_data.get('expires')
        return Credential(provider=provider, authorization=authorization, expires=expires)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class ErrorObject(object):
    def __init__(self, name, message, status_code, timestamp, issues):
        self.name = name
        self.message = message
        self.status_code = status_code
        self.timestamp = timestamp
        self.issues = issues

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @classmethod
    def throw_service_unavailable(cls, url):
        json_data = build_service_unavailable_message_rest(url)
        return ErrorObject.from_dict(json_data)

    @classmethod
    def from_dict(cls, json_data):
        name = json_data.get('name')
        message = json_data.get('message')
        status_code = json_data.get('status_code')
        timestamp = json_data.get('timestamp')
        issues = json_data.get('issues')
        return ErrorObject(name=name, message=message, status_code=status_code, timestamp=timestamp, issues=issues)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class BaseModel(object):
    def __init__(self, credentials):
        self.credentials = credentials

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class AuthenticationObject(BaseModel):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserObject(BaseModel):
    def __init__(self, active, name, phone, document_main, username, user_email, file_name, file_url, company,
                 occupation, password=None, last_password_reset_date=None, roles=None, internal=None, created=None,
                 is_active=True, is_authenticated=True, is_anonymous=False):
        self.internal = internal
        self.created = created
        self.active = active
        self.name = name
        self.phone = phone
        self.document_main = document_main
        self.username = username
        self.password = password
        self.user_email = user_email
        self.last_password_reset_date = last_password_reset_date
        self.file_name = file_name
        self.file_url = file_url
        self.company = company
        self.occupation = occupation
        self.roles = roles or []
        self.is_active = is_active
        self.is_authenticated = is_authenticated
        self.is_anonymous = is_anonymous

    def get_id(self):
        return self.internal

    @classmethod
    def from_dict(cls, json_data):
        internal = json_data.get('internal')
        created = json_data.get('created')
        active = json_data.get('active')
        name = json_data.get('name')
        phone = json_data.get('phone')
        document_main = json_data.get('document_main')
        username = json_data.get('username')
        password = json_data.get('password')
        user_email = json_data.get('user_email')
        last_password_reset_date = json_data.get('last_password_reset_date')
        file_name = json_data.get('file_name')
        file_url = json_data.get('file_url')
        company = json_data.get('company') or ''
        occupation = json_data.get('occupation') or ''
        roles = json_data.get('roles')

        if isinstance(roles, list):
            roles_user = []
            for g in roles:
                roles_user.append(RoleObject.from_dict(g))
        else:
            roles_user = RoleObject.from_dict(roles)

        return UserObject(internal=internal, created=created, active=active, name=name, phone=phone,
                          document_main=document_main, username=username, password=password, user_email=user_email,
                          last_password_reset_date=last_password_reset_date, file_name=file_name, file_url=file_url,
                          company=company, occupation=occupation, roles=roles_user)

    @classmethod
    def to_list_of_object(cls, json_data):
        if isinstance(json_data, list):
            collection = []
            for o in json_data:
                collection.append(UserObject.from_dict(o))
            return collection
        else:
            UserObject.from_dict(json_data)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class RoleObject(BaseModel):
    def __init__(self, name, type, description, internal=None, created=None):
        self.name = name
        self.type = type
        self.description = description
        self.internal = internal
        self.created = created

    @classmethod
    def from_dict(cls, json_data):
        name = json_data.get('name')
        type = json_data.get('type')
        description = json_data.get('description') or ''
        internal = json_data.get('internal')
        created = json_data.get('created')
        return RoleObject(name=name, type=type, description=description, internal=internal, created=created)

    @classmethod
    def to_list_of_object(cls, json_data):
        if isinstance(json_data, list):
            collection = []
            for o in json_data:
                collection.append(RoleObject.from_dict(o))
            return collection
        else:
            RoleObject.from_dict(json_data)


class PurchaseObject(BaseModel):
    def __init__(self, deal_id, buy_option_id, quantity, id=None):
        self.deal_id = deal_id
        self.buy_option_id = buy_option_id
        self.quantity = quantity
        self.id = id

    @classmethod
    def from_dict(cls, json_data):
        deal_id = json_data.get('deal_id')
        buy_option_id = json_data.get('buy_option_id')
        quantity = json_data.get('quantity')
        id = json_data.get('id')
        return PurchaseObject(deal_id=deal_id, buy_option_id=buy_option_id, quantity=quantity, id=id)

    @classmethod
    def to_list_of_object(cls, json_data):
        if isinstance(json_data, list):
            collection = []
            for o in json_data:
                collection.append(PurchaseObject.from_dict(o))
            return collection
        else:
            PurchaseObject.from_dict(json_data)


class BuyOptionObject(BaseModel):
    def __init__(self, title, normal_price, sale_price, percentage_discount, quantity_cupom,
                 start_date, end_date, id=None, create_date=None):
        self.title = title
        self.normal_price = normal_price
        self.sale_price = sale_price
        self.percentage_discount = percentage_discount
        self.quantity_cupom = quantity_cupom
        self.start_date = start_date
        self.end_date = end_date
        self.id = id
        self.create_date = create_date

    @classmethod
    def from_dict(cls, json_data):
        title = json_data.get('title')
        normal_price = json_data.get('normal_price')
        sale_price = json_data.get('sale_price')
        percentage_discount = json_data.get('percentage_discount')
        quantity_cupom = json_data.get('quantity_cupom')
        start_date = create_date_object(json_data.get('start_date'), '%Y-%m-%d')
        end_date = create_date_object(json_data.get('end_date'), '%Y-%m-%d')
        create_date = json_data.get('create_date')
        id = json_data.get('id')
        return BuyOptionObject(title=title, normal_price=normal_price, sale_price=sale_price,
                               percentage_discount=percentage_discount, quantity_cupom=quantity_cupom,
                               start_date=start_date, end_date=end_date, id=id, create_date=create_date)

    @classmethod
    def to_list_of_object(cls, json_data):
        if isinstance(json_data, list):
            collection = []
            for o in json_data:
                collection.append(BuyOptionObject.from_dict(o))
            return collection
        else:
            BuyOptionObject.from_dict(json_data)


class DealObject(BaseModel):
    def __init__(self, title, text, publish_date, end_date, url, total_sold, type, options=None,
                 id=None, create_date=None):
        self.title = title
        self.text = text
        self.publish_date = publish_date
        self.end_date = end_date
        self.url = url
        self.total_sold = total_sold
        self.type = type
        self.options = options
        self.id = id
        self.create_date = create_date

    @classmethod
    def from_dict(cls, json_data):
        title = json_data.get('title')
        text = json_data.get('text')
        publish_date = create_date_object(json_data.get('publish_date'), '%Y-%m-%d')
        end_date = create_date_object(json_data.get('end_date'), '%Y-%m-%d')
        url = json_data.get('url')
        total_sold = json_data.get('total_sold')
        type = json_data.get('type')
        create_date = json_data.get('create_date')
        id = json_data.get('id')
        options = BuyOptionObject.to_list_of_object(json_data.get('buy_options') or [])
        return DealObject(title=title, text=text, publish_date=publish_date, end_date=end_date,
                          url=url, total_sold=total_sold, type=type, options=options, id=id, create_date=create_date)

    @classmethod
    def to_list_of_object(cls, json_data):
        if isinstance(json_data, list):
            collection = []
            for o in json_data:
                collection.append(DealObject.from_dict(o))
            return collection
        else:
            DealObject.from_dict(json_data)
