from datetime import datetime
import platform
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, jsonify
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import app
from app import db
from app.forms import LoginForm, RegistrationForm
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