from flask import Blueprint, render_template, flash, redirect, url_for, request, session, json
from flask_login import login_required, login_user, logout_user
from ..forms import LoginForm
from ..application import login_manager
from ..util.library import jwt_decode
from ..util.enums import FlashMessagesCategory
from .client_api import LoginResource, UserResource
from ..models import AuthenticationObject, ErrorObject, UserObject
from ..util.authentication import AuthHeader
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from flask import current_app as app

auth = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(internal):
    user = None
    token = None

    try:
        if session['atlas_jwt_user']:
            user = UserObject.from_dict(session['atlas_jwt_user'])
        if session['atlas_jwt_token']:
            token = session['atlas_jwt_token']
    except Exception as e:
        return None

    app.logger.info('load_user: user {} / token {}'.format(user, token))
    if user and token:
        try:
            claims = jwt_decode(token)
        except (JWTError, ExpiredSignatureError, JWTClaimsError) as e:
            app.logger.error('Authentication Exception for user: {}'.format(e))
            session.pop('atlas_jwt_user', None)
            session.pop('atlas_jwt_token', None)
            return None
    return user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next_url = request.args.get('next')

    if form.validate_on_submit():
        next_url = request.form['next']
        user_json = UserObject(username=form.email.data, password=form.password.data, internal='393020202',
                               active=True, name='Ryan Padilha', phone='19981009370', document_main='41',
                               user_email='ryan.padilha@peixeurbano.com', file_name=None, file_url=None,
                               company='Peixe Urbano', occupation='Software Eng.')
        # AuthenticationObject(username=form.email.data, password=form.password.data).to_json()
        transaction = {'transaction': '8fpEQzmkXzxRfbAtiXQLMus6BhNS9gWocrNxM2ggCnw'}
        # LoginResource().authentication(data=user_json)

        if isinstance(transaction, ErrorObject):
            flash(u'O email ou o número de telefone inserido não corresponde a nenhuma conta',
                  category=FlashMessagesCategory.ERROR.value)
        else:
            AuthHeader.set_credentials(access_token=transaction.get('access_token'),
                                       expires=transaction.get('expires_in'))

            user_internal = UserObject(username='ryan.padilha@peixeurbano.com', password='p31xE', internal='393020202',
                                       active=True, name='Ryan Padilha', phone='19981009370', document_main='41',
                                       user_email='ryan.padilha@peixeurbano.com', file_name=None, file_url=None,
                                       company='Peixe Urbano', occupation='Software Eng.')

            # UserResource().find_by_username(username=form.email.data)
            if user_json.password == user_internal.password:
                user = user_internal
            else:
                user = user_json

            if user:
                if not user.active:
                    flash(u'Usuário não encontra-se ativo', category=FlashMessagesCategory.INFO.value)
                else:
                    login_user(user, remember=form.remember_me.data)
                    session.permanent = True
                    session['atlas_jwt_user'] = json.loads(user.to_json())
                    session['atlas_jwt_token'] = transaction.get('access_token')

                    return redirect(next_url or url_for('website.index'))
            else:
                flash(u'Problema desconhecido ao recuperar usuário', category=FlashMessagesCategory.ERROR.value)

    return render_template('auth/login.html', form=form, next=next_url)


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    session.pop('atlas_jwt_user', None)
    session.pop('atlas_jwt_token', None)

    logout_user()
    return redirect(url_for('auth.login'))

