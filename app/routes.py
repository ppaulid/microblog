from datetime import datetime, timezone
import platform
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, jsonify
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import app
from app import db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from app.models import DHT11Sensor

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
         {
            'author': {'username': 'JoJo'},
            'body': 'Beautiful day in Morioh-city!'
        },
        {
            'author': {'username': 'SusieQ'},
            'body': 'The Feidarras movie was so cool!'
        },
        {
            'author': {'username': 'Koniordos Michalis'},
            'body': 'to vathos tou ouranou den tha einai pia kokkino'
        }
    ]
    return render_template("index.html", title='Home Page', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username of password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/api/time', methods=['GET'])
def get_current_time():
    now = datetime.utcnow()
    time_data = {
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'name':'Petros'
        
    }
    return jsonify(time_data)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)












sensor = DHT11Sensor(gpio_pin=4)
@app.route('/api/dht11', methods=['GET'])
def temphum():
    data = sensor.get_readings()
    if 'error' not in data:
        return render_template('dht11.html', temperature=data['temperature'], humidity=data['humidity'])
    else:
        return "Failed to retrieve data from the sensor"
        
@app.route('/api/dht11/data', methods=['GET'])
def api_data():
    data = sensor.get_readings()
    if 'error' not in data:
        return jsonify(data)
    else:
        return jsonify(data), 500