
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, TechTalkEditForm, TechTalkForm
from models import ROLE_USER, ROLE_ADMIN, User, TechTalk
from config import TABLEROWS_PER_PAGE
from datetime import datetime


#  We need to provide a user_load function for Flask-Login module.
# basically we telling it what is our unique column.
@lm.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        db.session.add(g.user)
        db.session.commit()


@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    techtalks = TechTalk.query.paginate(page, TABLEROWS_PER_PAGE, False)
    #paginated_techtalks = TechTalk.paginate(page, TABLEROWS_PER_PAGE, False)

    return render_template(
        'index.html',
        title='Home',
        user=current_user,
        techtalks=techtalks
    )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(
        url_for('index')
    )


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template(
        'login.html',
        title='Sign In',
        form=form,
        providers=app.config['OPENID_PROVIDERS']
    )


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    techtalks = user.techtalks.paginate(page, TABLEROWS_PER_PAGE, False)
    return render_template(
        'user.html',
        user=user,
        techtalks=techtalks)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    elif request.method != "POST":
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
        form=form)


@app.route('/techtalks/')
@app.route('/techtalks/upcoming')
def schedule_index():
    return 'techtalks placeholder.  show upcoming techtalks from now() onwards'


@app.route('/techtalks/previous')
def schedule_previous():
    return 'techtalk placeholder.  show all previous techtalks.'


@app.route('/techtalks/add')
def schedule_previous():
    return 'Add new techtalk placeholder '


@app.route('/techtalks/edit')
def schedule_previous():
    return 'Edit a techtalk placeholder '


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
