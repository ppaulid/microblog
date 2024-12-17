from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone
from typing import Optional
from hashlib import md5
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import login
from app import db
import platform
import random
import uuid

def generate_uuid():
    return str(uuid.uuid4())

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
   
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)


if platform.system() != "Windows":
    import adafruit_dht
    import board

class DHT11Sensor:
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin
        self.is_windows = platform.system() == "Windows"  #Check if running on Windows

        if not self.is_windows:
            # Initialize the DHT sensor (DHT11 in this case) for the specified pin
            # Convert the GPIO pin number to the appropriate board pin
            self.sensor = adafruit_dht.DHT11(getattr(board, f'D{gpio_pin}'))
    
    def get_readings(self):
        if self.is_windows:
            # Simulate data if on Windows
            return {
                'temperature': round(random.uniform(20.0, 30.0), 2),
                'humidity': round(random.uniform(30.0, 70.0), 2)
            }
        else:
            try:
                # Read actual sensor data on Raspberry Pi
                temperature = self.sensor.temperature
                humidity = self.sensor.humidity

                # Ensure valid readings
                if humidity is not None and temperature is not None:
                    return {'temperature': temperature, 'humidity': humidity}
                else:
                    return {'error': 'Failed to retrieve data from the sensor'}

            except RuntimeError as error:
                # Handle sensor reading errors (which occur occasionally)
                return {'error': str(error)}

class Temperature(db.Model):
    id = db.Column(db.String(64), primary_key=True, default=generate_uuid)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    value = db.Column(db.Float)

class Humidity(db.Model):
    id = db.Column(db.String(64), primary_key=True, default=generate_uuid)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    value = db.Column(db.Float)
