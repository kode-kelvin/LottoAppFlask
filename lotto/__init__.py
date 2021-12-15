# import all dependables
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message
from decouple import config

# admin
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import  url_for,redirect, session


import stripe

stripe_keys = {
  'secret_key': 'sk_test_51IMienLuVHLuqvTJnrvsHIShICYXVz49215ak3Bik8V7pVnahjdh0G1Xdq4hS15ocmn7jQOcOEiZqVs7HiWzmqfG00wfX13p99',
  'publishable_key': 'pk_test_51IMienLuVHLuqvTJ8jH8EOcWbSVyDjClLD76EJiqqUv8seev2beSzhMg13GVCJBsxash8S9NUc2zKpGSH8OmHuh000tfCKULQm'
}

stripe.api_key = stripe_keys['secret_key']



# initiate the app
app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY'] = '730ec8ee4d95f7c0011a59877f2a5119b92095c89db9c5ll30'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lotto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# registration  and admin page related
bcrypt = Bcrypt(app)
# login_manager = LoginManager(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from lotto.models import User, Bet, Account #import model User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# the admin ---------------
class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.role == 'Admin':
            return True
        else:
            False      
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))


class MyAdminIndexView(AdminIndexView):
     def is_accessible(self):
        if current_user.is_authenticated and current_user.role == 'Admin':
            return True
        else:
            False   
        

# admin view
admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Bet, db.session))
admin.add_view(MyModelView(Account, db.session))





# sending an email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kodediego@gmail.com'
app.config['MAIL_PASSWORD'] = config['PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# the routes
from lotto import  routes
