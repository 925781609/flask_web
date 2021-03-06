from flask import (render_template, flash, redirect,
                   url_for, request, send_from_directory,
                   current_app, make_response, abort)
from . import main
from ..decorators import admin_required, permission_required
from ..models import Permission, User, Role, Post, Comment
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
import os
from PIL import Image
from werkzeug import secure_filename
import re
# use to report weather
import urllib.request
from threading import Thread
from random import randint


INFO = "你好，请先登录"
FIRST_TIME = 1


def get_weather(ApiUrl):
    print('get_weather was called!')
    global status
    with urllib.request.urlopen(ApiUrl) as html:
        # 读取并解码
        data=html.read().decode("utf-8")
        # print(data)
        line = re.split('\n', data)
        # print(line)
        for item in line:
            weather = re.findall("var hour3data.*?n00,(.*?),0.*", item)
            if len(weather) != 0:
                global INFO
                INFO = "上海天气: " + weather[0]
    print('get_weather end called')


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page,
                                                                per_page=current_app.config['FLASKY_POSTS_PER_PAGE'] or 20,
                                                                error_out=False)
    posts = pagination.items
    ApiUrl= "http://www.weather.com.cn/weather1d/101020100.shtml"
    global FIRST_TIME
    if FIRST_TIME == 1:
        FIRST_TIME = 0
        thr = Thread(target=get_weather, args=[ApiUrl])
        thr.start()
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination, info=INFO)


@main.route('/admin')
@login_required
@admin_required
def for_admin():
    return "For administrator"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderator():
    return "For moderator"


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/user/signin')
def sign_in():
    print('current user is {}'.format(current_user.username))
    user = User.query.filter_by(username=current_user.username).first()
    if user.signin_num is None:
        user.signin_num = 1
    else:
        user.signin_num +=1
    if user.gold_coin is None:
        user.gold_coin =randint(1, 4)
    else:
        user.gold_coin += randint(1, 4)
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/user/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


AVATAR_FOLDER=r'C:\Users\keithliu\CODE\blog\app\static\avatar'
ALLOWED_EXTENSIONS=set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and re.split('\.', filename)[1] in ALLOWED_EXTENSIONS


@main.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        size = (40, 40)
        im = Image.open(file)
        im.thumbnail(size)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(AVATAR_FOLDER)
            im.save(os.path.join(AVATAR_FOLDER, filename))
            current_user.new_avatar_file = url_for('static', filename='%s/%s' % ('avatar', filename))
            current_user.is_avatar_default = False
            flash(u'头像修改成功')
            return redirect(url_for('.user', username=current_user.username))
        else:
            flash(u'update avatar not successfully')
    return render_template('upload_file.html')


@main.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(AVATAR_FOLDER, filename)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page=request.args.get('page', 1, type=int)
    if page== -1:
        page= (post.comments.count() - 1) / (current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page,
                                                                          per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
                                                                          error_out=False)
    comments = pagination.items

    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You are already following this user')
        return redirect(url_for('main.user', username=username))

    current_user.follow(user)
    flash('Now you are following %s' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page,
                                         per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)

    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]

    return render_template('followers.html', user=user, title='Followers of',
                           endpoint='main.followers', pagination=pagination, follows=follows)


@main.route('/followed/<username>')
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page,
                                        per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                        error_out=False)

    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    print("item.timestamp")
    for item in pagination.items:
        print(item.timestamp)

    return render_template('followers.html', user=user, title='Followed by',
                           endpoint='main.followed', pagination=pagination, follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp
