from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms.validators import InputRequired, Email, Length
from forms import *
from io import BytesIO
import os
# Connecting to the database and ORM as known sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from database import *

import PyPDF2


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

##################################
# Database Connection
engine = create_engine('sqlite:///Shopmart.db')
Base.metadata.bind = engine

# Creates the session
session = scoped_session(sessionmaker(bind=engine))


@app.teardown_request
def remove_session(ex=None):
    session.remove()


###############################

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
######################################


@login_manager.user_loader
def load_user(user_id):
    user = session.query(Users).filter_by(ID = int(user_id)).first()
    return user


# Log out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Password Reset
@app.route('/reset_password')
def reset_password():
    return 'password reset page'


# Registration System
@app.route('/register',  methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    signup_form = SignUpForm()
    if signup_form.validate_on_submit():
        hashed_password = generate_password_hash(signup_form.Password.data, method='sha256')
        newUser = Users(FullName=signup_form.FullName.data, PhoneNumber=signup_form.PhoneNumber.data, UserType = signup_form.UserType.data, EmailAddress=signup_form.EmailAddress.data, Password=hashed_password)
        session.add(newUser)
        session.commit()

        return redirect(url_for('login'))
    else: print('validation failed')

    return render_template('signup.html', signup_form = signup_form)


# Login System
@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    email_subscribe_form = EmailSubscribeForm()

    login_form = LoginForm()

    if login_form.validate_on_submit():
        tempUser = login_form.EmailAddress.data
        user = session.query(Users).filter_by(EmailAddress=tempUser).first()
        if user:
            if check_password_hash(user.Password, login_form.Password.data):
                login_user(user, remember=login_form.Remember.data)
                return redirect(url_for('dashboard'))
            else:
                flash("Password not correct")
                return redirect(url_for('login'))

    return render_template('login.html', login_form = login_form, email_subscribe_form = email_subscribe_form)


# Define User dashboard
@app.route('/dashboard')
@login_required
def dashboard():

    email_subscribe_form = EmailSubscribeForm()

    if current_user.UserType == 'buyer':
        return render_template('buyer_dashboard.html')

    elif current_user.UserType == 'seller':
        return render_template('seller_dashboard.html')
        
    elif current_user.UserType == 'Caarer':
        return render_template('caarer_dashboard.html')
        
    elif current_user.UserType == 'admin':
        return render_template('admin_dashboard.html')
    else:
        flash('Access Denied')
        return url_for('home')


##########################################
#Social Networking system

##################################
# ABOUT US PAGE
@app.route('/about')
def about():
    return render_template('about.html')


# CONTACT US PAGE
@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/')
def home():
    return render_template('index.html')




##################################

# Main Function
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
