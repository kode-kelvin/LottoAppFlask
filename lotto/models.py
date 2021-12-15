from datetime import datetime

from flask_login.mixins import UserMixin
from lotto import db, login_manager
from flask_login import UserMixin



# user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), unique=False, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    money = db.relationship('Account', backref='author', lazy=True)
    bets = db.relationship('Bet', backref='author', lazy=True)
    
    

    
    def __repr__(self):
        return f"User('{self.username}','{self.email}', '{self.role}')"


# their bet

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bet = db.Column(db.String(20), nullable=False)
    bet_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Bet('{self.bet}', '{self.bet_date}')"


# their account
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    my_money = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'Money("{self.my_money}")'


