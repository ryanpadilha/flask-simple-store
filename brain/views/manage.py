import json

from slugify import slugify
from flask import Blueprint, abort, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from ..util.enums import FlashMessagesCategory
from .client_api import RoleResource, UserResource, BuyOptionResource, DealResource, PurchaseResource
from ..models import RoleObject, ErrorObject, UserObject, BuyOptionObject, DealObject, PurchaseObject
from ..forms import RoleForm, UserForm, UserEditForm, UserChangePasswordForm, BuyOptionForm, DealForm
from ..util.library import json_default, convert_to_currency


manage = Blueprint('manage', __name__, url_prefix='/manage')


@manage.route('/buy-option', methods=['GET'])
@login_required
def list_options():
    options = BuyOptionResource().list()
    return render_template('store/list-buy-option.html', options=options)


@manage.route('/buy-option/form', methods=['GET', 'POST'])
@login_required
def form_option():
    form = BuyOptionForm()

    if form.validate_on_submit():
        option = BuyOptionObject(title=form.title.data,
                                 normal_price=convert_to_currency(form.normal_price.data),
                                 sale_price=convert_to_currency(form.sale_price.data),
                                 percentage_discount=convert_to_currency(form.percentage_discount.data),
                                 quantity_cupom=form.quantity_cupom.data,
                                 start_date=form.start_date.data,
                                 end_date=form.end_date.data)

        json_option = json.dumps(option, default=json_default)

        try:
            obj = BuyOptionResource().persist(data=json_option)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('store/form-buy-option.html', form=form)

            return redirect(url_for('manage.list_options'))
        except Exception as e:
            abort(500, e)

    return render_template('store/form-buy-option.html', form=form)


@manage.route('/buy-option/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_option(id):
    form = BuyOptionForm()

    if request.method == 'GET':
        option = BuyOptionResource().get_by_id(id=id)
        if not isinstance(option, ErrorObject):
            form.process(obj=option)

    if form.validate_on_submit():
        option = BuyOptionObject(id=id,
                                 title=form.title.data,
                                 normal_price=convert_to_currency(form.normal_price.data),
                                 sale_price=convert_to_currency(form.sale_price.data),
                                 percentage_discount=convert_to_currency(form.percentage_discount.data),
                                 quantity_cupom=form.quantity_cupom.data,
                                 start_date=form.start_date.data,
                                 end_date=form.end_date.data)

        json_option = json.dumps(option, default=json_default)

        try:
            obj = BuyOptionResource().update(id=id, data=json_option)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('store/form-buy-option.html', form=form)

            return redirect(url_for('manage.list_options'))
        except Exception as e:
            abort(500, e)

    return render_template('store/form-buy-option.html', form=form)


@manage.route('/buy-option/delete', methods=['POST'])
@login_required
def delete_option():
    try:
        obj = BuyOptionResource().delete_entity(id=request.form['recordId'])
        if isinstance(obj, ErrorObject):
            flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
        else:
            flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)

        return redirect(url_for('manage.list_options'))
    except Exception as e:
        abort(500, e)


@manage.route('/deal', methods=['GET'])
@login_required
def list_deals():
    deals = DealResource().list()
    return render_template('store/list-deal.html', deals=deals)


@manage.route('/deal/form', methods=['GET', 'POST'])
@login_required
def form_deal():
    form = DealForm()
    collection = BuyOptionResource().all_available_without_relation()
    form.options.choices = [(o.id, o.title) for o in collection]

    if form.validate_on_submit():
        deal = DealObject(title=form.title.data,
                          text=form.text.data,
                          publish_date=form.publish_date.data,
                          end_date=form.end_date.data,
                          url=slugify(form.title.data.lower()),
                          total_sold=0,
                          type=form.type.data,
                          options=form.options.data)

        json_deal = json.dumps(deal, default=json_default)

        try:
            obj = DealResource().persist(data=json_deal)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('store/form-deal.html', form=form)

            return redirect(url_for('manage.list_deals'))
        except Exception as e:
            abort(500, e)

    return render_template('store/form-deal.html', form=form)


@manage.route('/deal/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_deal(id):
    form = DealForm()
    current_collection = []

    option_item_list = []
    deal = DealResource().get_by_id(id=id)
    for o in deal.options:
        option_item_list.append(o.id)
        current_collection.append(BuyOptionResource().get_by_id(o.id))

    # only without relation
    collection = BuyOptionResource().all_available_without_relation() + current_collection
    form.options.choices = [(o.id, o.title) for o in collection]

    if request.method == 'GET':
        if not isinstance(deal, ErrorObject):
            form.process(obj=deal, type=deal.type, h_total_sold=deal.total_sold, h_url=deal.url)

            form.options.default = option_item_list
            form.options.process(None)

    if form.validate_on_submit():
        deal = DealObject(id=id,
                          title=form.title.data,
                          text=form.text.data,
                          publish_date=form.publish_date.data,
                          end_date=form.end_date.data,
                          url=form.h_url.data,
                          total_sold=form.h_total_sold.data,
                          type=form.type.data,
                          options=form.options.data)

        json_deal = json.dumps(deal, default=json_default)

        try:
            obj = DealResource().update(id=id, data=json_deal)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('store/form-deal.html', form=form)

            return redirect(url_for('manage.list_deals'))
        except Exception as e:
            abort(500, e)

    return render_template('store/form-deal.html', form=form)


@manage.route('/deal/delete', methods=['POST'])
@login_required
def delete_deal():
    try:
        obj = DealResource().delete_entity(id=request.form['recordId'])
        if isinstance(obj, ErrorObject):
            flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
        else:
            flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)

        return redirect(url_for('manage.list_deals'))
    except Exception as e:
        abort(500, e)


@manage.route('/o/<url>', methods=['GET'])
@login_required
def view_deal_details(url):
    deal = DealResource().get_by_url(url=url)
    return render_template('store/view-deal.html', deal=deal)


@manage.route('/o/buy/<deal>/<option>', methods=['POST'])
@login_required
def buy_option(deal, option):
    deal_id = deal
    option_id = option

    deal = DealResource().get_by_id(id=deal_id)

    purchase = PurchaseObject(deal_id=deal_id,
                              buy_option_id=option_id,
                              quantity=1)

    json_purchase = json.dumps(purchase, default=json_default)

    try:
        obj = PurchaseResource().persist(data=json_purchase)
        if isinstance(obj, ErrorObject):
            flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
            return render_template('store/view-deal.html', deal=deal)

        flash(u'Compra de oferta realizada com sucesso.', category=FlashMessagesCategory.INFO.value)
        return redirect(url_for('website.index'))
    except Exception as e:
        abort(500, e)


@manage.route('/role')
@login_required
def list_roles():
    roles = RoleResource().list()
    return render_template('manage/list-role.html', roles=roles)


@manage.route('/role/form', methods=['GET', 'POST'])
@login_required
def form_role():
    form = RoleForm()

    if form.validate_on_submit():
        role = RoleObject(name=form.name.data,
                          type=form.type.data.upper(),
                          description=form.description.data).to_json()

        try:
            obj = RoleResource().persist(data=role)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-role.html', form=form)

            return redirect(url_for('manage.list_roles'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-role.html', form=form)


@manage.route('/role/<uuid:internal>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(internal):
    form = RoleForm()

    if request.method == 'GET':
        role = RoleResource().get_by_internal(internal=internal)
        if not isinstance(role, ErrorObject):
            form.process(obj=role)

    if form.validate_on_submit():
        role = RoleObject(name=form.name.data,
                          type=form.type.data.upper(),
                          description=form.description.data).to_json()

        try:
            obj = RoleResource().update(internal=internal, data=role)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-role.html', form=form)

            return redirect(url_for('manage.list_roles'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-role.html', form=form)


@manage.route('/role/delete', methods=['POST'])
@login_required
def delete_role():
    try:
        obj = RoleResource().delete_entity(internal=request.form['recordId'])
        if isinstance(obj, ErrorObject):
            flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
        else:
            flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)

        return redirect(url_for('manage.list_roles'))
    except Exception as e:
        abort(500, e)


@manage.route('/user', methods=['GET'])
@login_required
def list_users():
    users = UserResource().list()
    return render_template('manage/list-user.html', users=users)


@manage.route('/user/form', methods=['GET', 'POST'])
@login_required
def form_user():
    form = UserForm()

    if form.validate_on_submit():
        user = UserObject(active=form.active.data,
                          name=form.name.data,
                          username=form.user_email.data.lower(),
                          user_email=form.user_email.data.lower(),
                          password=form.user_password.data,
                          file_name=None,
                          file_url=None,
                          company=form.company.data,
                          occupation=form.occupation.data,
                          phone=form.phone.data.replace('(', '').replace(') ', '').replace('-', ''),
                          document_main=form.document_main.data)

        user.roles.clear()
        for role in form.roles.data:
            user.roles.append(role)

        try:
            obj = UserResource().persist(data=user.to_json())
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-user.html', form=form)

            return redirect(url_for('manage.list_users'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-user.html', form=form)


@manage.route('/user/<uuid:internal>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(internal):
    form = UserEditForm()

    if request.method == 'GET':
        user = UserResource().get_by_internal(internal=internal)
        if not isinstance(user, ErrorObject):
            form.process(obj=user)

            role_list = []
            for r in user.roles:
                role_list.append(r.type)
            form.roles.default = role_list
            form.roles.process(request.form)

    if form.validate_on_submit():
        user = UserObject(active=form.active.data,
                          name=form.name.data,
                          username=form.user_email.data.lower(),
                          user_email=form.user_email.data.lower(),
                          file_name=None,
                          file_url=None,
                          company=form.company.data,
                          occupation=form.occupation.data,
                          phone=form.phone.data.replace('(', '').replace(') ', '').replace('-', ''),
                          document_main=form.document_main.data)

        user.roles.clear()
        for role in form.roles.data:
            user.roles.append(role)

        try:
            obj = UserResource().update(internal=internal, data=user.to_json())
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-user.html', form=form)

            return redirect(url_for('manage.list_users'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-user.html', form=form, file_name='', file_url='')


@manage.route('/user/delete', methods=['POST'])
@login_required
def delete_user():
    try:
        obj = UserResource().delete_entity(internal=request.form['recordId'])
        if isinstance(obj, ErrorObject):
            flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
        else:
            flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)

        return redirect(url_for('manage.list_users'))
    except Exception as e:
        abort(500, e)


@manage.route('/user/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    form = UserChangePasswordForm()

    if form.validate_on_submit():
        user = UserResource().get_by_internal(current_user.internal)
        if isinstance(user, ErrorObject):
            flash(user.issues, category=FlashMessagesCategory.ERROR.value)
            return render_template('manage/view-profile.html', form=form)

        # verificando se senha atual confere
        # if not user.verify_password(form.current_password.data):
        #     flash(u'Senha atual informada está incorreta.', category=FlashMessagesCategory.ERROR.value)
        #     return render_template('manage/view-profile.html', form=form)

        user.password = form.user_password.data

        try:
            obj = UserResource().update(internal=user.internal, data=user.to_json())
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
            else:
                flash(u'Alteração de senha realizada com sucesso. A alteração ocorre apenas uma vez por sessão.',
                      category=FlashMessagesCategory.INFO.value)

            return redirect(url_for('manage.view_profile'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/view-profile.html', form=form)
