from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from hashlib import md5
from sqlalchemy.dialects.postgresql import ARRAY, INET


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(12), index=True, unique=True)
    access = db.Column(db.Integer, default=1)
    alerts = db.Column(db.String(3))
    newsletter = db.Column(db.String(3))
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(500), index=True)
    address = db.Column(db.String(500), index=True)
    city = db.Column(db.String(50), index=True)
    state = db.Column(db.String(2), index=True)
    zip_code = db.Column(db.String(14), index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    tortilla_desc = db.Column(db.String(1000))
    tortilla_score = db.Column(db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None))
    potato_desc = db.Column(db.String(1000))
    potato_score = db.Column(db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None))
    texture_desc = db.Column(db.String(1000))
    texture_score = db.Column(db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None))
    flavor_desc = db.Column(db.String(1000))
    flavor_score = db.Column(db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None))
    general_desc = db.Column(db.String(1000))
    general_score = db.Column(db.Integer)
    overall_score = db.Column(db.Integer, index=True)
    smother = db.Column(db.String(3))
    smother_score = db.Column(db.String(3))
    overview = db.Column(db.String(1000))
    published = db.Column(db.String(3))



class Access(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    ip = db.Column(INET)
    path = db.Column(db.String(100))
    time = db.Column(db.DateTime, default=datetime.utcnow)

class Dict_Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class DictYN(db.Model):
    type = db.Column(db.String(3), primary_key=True)

class DictScore(db.Model):
    type = db.Column(db.String(3), primary_key=True)

class BurritoBanter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(500), index=True)
    banter = db.Column(db.String(1000))

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    subject = db.Column(db.String(50))
    message = db.Column(db.String(1000))