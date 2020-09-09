from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

import secrets
from functools import wraps
import hashlib



app = Flask(__name__)

# set secret key for using session
app.config['SECRET_KEY'] = 'thisismysecretkey'


# set config values for flask-mail
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'fortestonlyflask@gmail.com',
    MAIL_PASSWORD = 'passwordFortest',
))
mail = Mail(app)

# set database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# create user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    hash_email = db.Column(db.String(300), unique=True, nullable=True)
    token = db.Column(db.String(200), unique=True, nullable=True)
    log_counter = db.Column(db.Integer, default = 0)

    def __repr__(self):
        return '<User: %r>' % self.email

# create decorator for prevent unauthorized access
# it`s check that cyrrent user are authorized or not
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# index route
@app.route('/', methods=['POST', 'GET'])
def index():

    error_message = None
    
    # check if user already log in
    if 'user' in session:
        u = User.query.filter_by(email=session['user']).first()
        return redirect(url_for('profile', cur_user_id=u.id))

    # when someone type in input and press send button
    if request.method == 'POST':
        email = request.form['email']

        # check if this email already was registerd  
        if not User.query.filter_by(email=email).first():
            # generate token and hash email
            token = secrets.token_urlsafe()
            hash_obj = hashlib.md5(email.encode())
            md5_hash = hash_obj.hexdigest()
            
            # create user
            user = User(email=email, token=token, hash_email=md5_hash)
            db.session.add(user)
            db.session.commit()

            # generate magic link
            login_link = str(request.base_url+'_login_request/{}_and_{}'.format(user.hash_email, token))

            # setup, generate and send mail to inputed email
            mail_message = Message('Hi, this is your link to log in', 
                                    sender=app.config['MAIL_USERNAME'],
                                    recipients=[email])
            mail_message.body = 'Copy and past this link to your browser or click on it: {}'.format(login_link)
            mail.send(mail_message)
            print('message sended to email: {}'.format(email))
            
            return render_template('confirm.html')
        # if inputed email already used user see this error
        error_message = 'This email already register! Use another one!'
        
    return render_template('index.html', error_message=error_message)


# route for magic link, when user go via sended for him magic link
# in this part we verify link, increase counter, that count ho much times user log in and than redirect to profile
@login_required
@app.route('/_login_request/<hash_email>_and_<token>')
def login_request(hash_email, token):
    cur_user = User.query.filter_by(hash_email=hash_email, token=token).first()
    if cur_user:
        # increace counter
        cur_user.log_counter = cur_user.log_counter + 1
        db.session.commit()
        # setup current session user
        session['user'] = cur_user.email
        # redirect to profile
        return redirect(url_for('profile', cur_user_id=cur_user.id))
    # return error if link not verify
    return 'loaded with some error, not sign in...'

# logout route
@app.route('/logout')
def logout():

    # clear current session
    session.pop('user', None)
    
    return redirect(url_for('index'))


# user profile route. this page visible only after user tap on magic link.
@app.route('/profile/<cur_user_id>')
@login_required
def profile(cur_user_id):
    user = User.query.filter_by(id=cur_user_id, email=session['user']).first()
    if user:
        log_count = user.log_counter
        return render_template('profile.html', cur_user = user.email, log_count=log_count)
    return redirect(url_for('index'))




# this part - route for quick delete all users, drop database and create again

@app.route('/del/delete_users/')
def delete_users():
    users = User.query.all()
    for user in users:
        db.session.delete(user)
        db.session.commit()
        db.drop_all()
        db.session.commit()
        db.create_all()
        db.session.commit()
    return 'users deleted'




