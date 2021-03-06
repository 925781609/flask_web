from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user

from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from ..email import send_mail

@auth.route('/login', methods=['GET', 'POST'])
def login():
    logform = LoginForm()
    regform = RegistrationForm()
    # deal with login form submit
    if logform.submit1.data and logform.validate_on_submit(): #Notice sequence
        user = User.query.filter_by(email=logform.email.data).first()
        if user is not None and user.verify_password(logform.password.data):
            login_user(user, logform.remember_me.data)
            print('reqest.agrs.get(next)',(request.args.get('next' )))
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    # deal with register form submit
    if regform.submit2.data and regform.validate_on_submit(): #Notice sequence
        user = User(email = regform.email.data,
                    username = regform.username.data,
                    password = regform.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email, 'confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A Confirmation email has been sent to you by email.')
        #return redirect(url_for('auth.login')) #seems doesnot need it any more
    return render_template('auth/login.html', logform=logform, regform=regform)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm( )
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.before_app_request
def before_request():
    print('before_request is called ')
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm', methods=['GET', 'PSOT'])
def resend_confirmation():
        token = current_user.generate_confirmation_token()
        send_mail(user.email, 'confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
        return redirect(url_for('main.index'))

