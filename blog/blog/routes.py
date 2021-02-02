import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, request, redirect
from flask_login import current_user, login_required, login_user, logout_user
from blog import app, bcrypt, login_manager, db
from blog.forms import LoginForm, RegisterForm, UpdateAccountForm
from blog.models import User


@app.route('/account/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def account_update(id):
    user = User.query.filter_by(id=id).first()

    if not current_user == user and not user is None:
        flash('You must be authenticated as this user to update his info!', 'danger')
        return redirect(url_for('account', id=id))

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account', id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pictures/' + user.image_file)
    return render_template('account_edit.html', form=form, image_file=image_file, title='Update Account')

@app.route('/account/<int:id>')
@login_required
def account(id):
    user = User.query.filter_by(id=id).first()
    image_file = url_for('static', filename='profile_pictures/' + user.image_file)
    return render_template('account_info.html', user=user, image_file=image_file, title='Account Information')

@app.route('/accounts')
@login_required
def accounts():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id.desc()).paginate(page=page, per_page=3)
    # users.remove(current_user)
    return render_template('accounts.html', users=users, title='Accounts')

@app.route('/')
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account', id=current_user.id))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account', id=current_user.id))
        else:
            flash('Username or password incorrect!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pictures',picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
