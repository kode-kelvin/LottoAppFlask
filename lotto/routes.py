# import all dependables
import threading
from flask import  render_template, url_for, flash, redirect, request, session
from lotto import app, db, bcrypt, mail
from flask_mail import Message
from lotto.models import User, Bet, Account
from lotto.forms import RegistrationForm, LoginForm, UpdateProfileForm
from flask_login import login_user, current_user, logout_user, login_required
import random
import datetime
import time
import random
import threading
from datetime import timedelta
import sqlite3
import stripe

stripe_keys = {
  'secret_key': 'sk_test_51IMienLuVHLuqvTJnrvsHIShICYXVz49215ak3Bik8V7pVnahjdh0G1Xdq4hS15ocmn7jQOcOEiZqVs7HiWzmqfG00wfX13p99',
  'publishable_key': 'pk_test_51IMienLuVHLuqvTJ8jH8EOcWbSVyDjClLD76EJiqqUv8seev2beSzhMg13GVCJBsxash8S9NUc2zKpGSH8OmHuh000tfCKULQm'
}

stripe.api_key = stripe_keys['secret_key']


# methods
action = ['GET', 'POST']

# auto check win
def get_random_number(sleeptime=10):
    while sleeptime >0:
        time.sleep(sleeptime)
        numb = random.randint(10000000,99999999)
        with open('/Users/mac/Desktop/FLaskPROJECT/megawin/lotto/winnum.txt', 'w') as f:
            f.write(str(numb))
            f.close()


        # add -- more history
        with open('/Users/mac/Desktop/FLaskPROJECT/megawin/lotto/winhistory.txt', 'at') as f:
           f.write(f" \n {str(numb)}")
           f.close()

        # paying
threading.Thread(target=get_random_number).start()



# home view - ----- -- ------
@app.route('/')
def home():
    user = current_user
    print(user)
    return render_template('index.html')

# register - ----- -- ------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, role=form.role.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # create account automatically
        # send welcome email
        subject = 'Comfirmation'
        msg = Message(subject, sender='noreply@demo.com', recipients=[form.email.data])
        msg.body = 'Welcome to 10Xbet. you have 10 credits'
        mail.send(msg)
        flash('Your account has been successfully created. You can now login')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


# login - ----- -- ------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login failed, check password and email')
    return render_template('signin.html', form=form)



# logout - ----- -- ------
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


# result ---


@app.route('/result', methods=['GET', 'POST'])
def result():
    user = current_user.id
    def check_result(sleeptime=10):
        while sleeptime >0:
            time.sleep(sleeptime)
            with open('/Users/mac/Desktop/FLaskPROJECT/megawin/lotto/the.txt', 'r') as f:
                lines = f.read()
                lines = int(lines)
                rand_num = lines
              
                count = Bet.query.filter_by(bet=rand_num, user_id=user).count()
                if count:
                    win = 4000
                    
                    account_balance = Account.query.filter_by(id=user).all()
                    cash =  (sum([fund.my_money for fund in account_balance]))
                    # new balance
                    new_money = cash + win
                    #get the amount and add to the new
                    con = sqlite3.connect('/Users/mac/Desktop/FLaskPROJECT/megawin/lotto/lotto.db')
                    cur = con.cursor()
                    # update with the new amount
                    sql_update_query = """Update Account set my_money = ? where user_id = ?"""
                    data = (new_money, user)
                    cur.execute(sql_update_query, data)
                    con.commit()
                    print('we got a winner')
                else:
                    print('did not win')
    threading.Thread(target=check_result).start()
    return render_template('result.html', user=user)


# profile page - ----- -- ------
@login_required
@app.route('/profile', methods=action)
def profile():
    form = UpdateProfileForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            if form.password.data:
                current_user.password = bcrypt.generate_password_hash(form.password.data)
            else:
                pass
            db.session.commit()
            flash('your account has been updated')
            return redirect(url_for('profile'))
    else:
        all_bet = Bet.query.filter_by(author=current_user).all()
        account_balance = Account.query.filter_by(author=current_user).all()
        cash =  (sum([fund.my_money for fund in account_balance]))
        form.username.data = current_user.username
        form.email.data = current_user.email
        return render_template('profile.html', form=form, title='profile', me=current_user.password, data=all_bet, cash=cash)

# bet - ----- -- ------
@login_required
@app.route('/bet', methods=action)
def placebet():
    user = current_user.id
    account_balance = Account.query.filter_by(id=user).all()
    cash =  (sum([fund.my_money for fund in account_balance]))
    bet_amount = 300
    if request.method == 'POST':
        entry_bet = request.form['bet']
        check = str(entry_bet)
        if not entry_bet:
            flash('You have to enter a number', 'error')
        elif len(check) != 8:
            flash('Your number is less than 8 digits', 'error')
        elif cash < bet_amount:
            flash('Your account is too low ! Please top up')
        else:
            new_bet = Bet(bet=entry_bet, author=current_user)
            db.session.add(new_bet)
            db.session.commit()
            flash('Bet successfully placed.. Wish you luck', 'info')
            # taking money off after bet
          
            # new balance -- adding money
            new_money = cash - bet_amount
            #get the amount and add to the new
            con = sqlite3.connect('/Users/mac/Desktop/FLaskPROJECT/megawin/lotto/lotto.db')
            cur = con.cursor()
            # update with the new amount
            sql_update_query = """Update Account set my_money = ? where user_id = ?"""
            data = (new_money, user)
            cur.execute(sql_update_query, data)
            con.commit()
            print('money added')
        return render_template('bet.html', cash=cash)
    else:
        account_balance = Account.query.filter_by(author=current_user).all()
        cash =  (sum([fund.my_money for fund in account_balance]))
    return render_template('bet.html', cash=cash)
    

# top-up ---- ----- --- ---
@app.route('/topup')
def topaccount():
    return render_template('topup.html', key=stripe_keys['publishable_key'])


# topping up - ----- -- ------
@login_required
@app.route('/charge', methods=['POST'])
def charge():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        email = request.form['email']
        full_name = request.form['name']

        if amount == 500:
            pay = 5000 + 1000
        elif amount == 700:
            pay = 8000 + 1200
        elif amount == 1000:
            pay = 11000 + 1400
        else:
            pass

        # check if account exist
        user = current_user.id
        check_account = Account.query.filter_by(id=user).all()
        if check_account:
            # get the main amount
            account_balance = Account.query.filter_by(author=current_user).all()
            cash =  (sum([fund.my_money for fund in account_balance]))
            # new balance
            new_money = cash + pay
            #get the amount and add to the new
            con = sqlite3.connect('/Users/mac/Desktop/FLaskPROJECT/megawin/lotto/lotto.db')
            cur = con.cursor()
            # update with the new amount
            sql_update_query = """Update Account set my_money = ? where user_id = ?"""
            data = (new_money, user)
            cur.execute(sql_update_query, data)
            con.commit()
            print('account was UPDATED successfully')
        else:
            # CREATE ACCOUNT FOR USER IF THEY DON'T
            add_account = Account(my_money=pay, author=current_user)
            db.session.add(add_account)
            db.session.commit()
            print('account was CREATED successfully and money added')

        
    # Amount in cents
    amount = amount
    email = email
    nickname = full_name

    customer = stripe.Customer.create(
        name=nickname,
        email=email,
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        # customer=customer.id,
        customer=customer,
        amount=amount * 100,
        currency='usd',
        description='Subscription'
    )

    return render_template('charge.html', amount=amount, email=email)


# quick cash  - ----- -- ------  - ----- -- ------ - ----- -- ------ - ----- -- ------
@app.route('/quickcash', methods=action)
def quickgame():
    account_balance = Account.query.filter_by(author=current_user).all()
    cash =  (sum([fund.my_money for fund in account_balance]))
    if request.method == "POST":
        wager = request.form.get("wager")
        guess = request.form.get("guess")
        test = request.form.get("test")

        print(wager, guess, test)

        # adding pay or minus
         # check if account exist
        user = current_user.id
        check_account = Account.query.filter_by(id=user).all()
        if check_account:
            # get the main amount
            account_balance = Account.query.filter_by(author=current_user).all()
            cash =  (sum([fund.my_money for fund in account_balance]))
            # new balance
            if guess == test:
                new_money = cash + int(wager *2)
                #get the amount and add to the new
                con = sqlite3.connect('/Users/mac/Desktop/FLaskPROJECT/megawin/lotto/lotto.db')
                cur = con.cursor()
                # update with the new amount
                sql_update_query = """Update Account set my_money = ? where user_id = ?"""
                data = (new_money, user)
                cur.execute(sql_update_query, data)
                con.commit()
                print('money added')
            else:
                new_money = cash - int(wager)
                #get the amount and add to the new
                con = sqlite3.connect('/Users/mac/Desktop/FLaskPROJECT/megawin/lotto/lotto.db')
                cur = con.cursor()
                # update with the new amount
                sql_update_query = """Update Account set my_money = ? where user_id = ?"""
                data = (new_money, user)
                cur.execute(sql_update_query, data)
                con.commit()
                print('you lost money')

        else:
            pass
    return render_template('quickcash.html', cash=cash)