from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

import secrets
from functools import wraps



app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisismysecretkey'



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

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    token = db.Column(db.String(200), unique=True, nullable=True)
    log_counter = db.Column(db.Integer, default = 0)

    def __repr__(self):
        return '<User: %r>' % self.email


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
        # if CURRENT_USER is None:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['POST', 'GET'])
def index():

    error_message = None
    
    if 'user' in session:
        u = User.query.filter_by(email=session['user']).first()
        return redirect(url_for('profile', cur_user_id=u.id))

    if request.method == 'POST':
        email = request.form['email']
        if not User.query.filter_by(email=email).first():
            token = secrets.token_urlsafe()
            
            user = User(email=email, token=token)
            db.session.add(user)
            db.session.commit()

            login_link = str(request.base_url+'_login_request/user_{}/token_{}'.format(user.email, token))

            mail_message = Message('Hi, this is your link to log in', 
                                    sender=app.config['MAIL_USERNAME'],
                                    recipients=[email])
            mail_message.body = 'Copy and past this link to your browser or click on it: {}'.format(login_link)
            mail.send(mail_message)
            print('message sended to email: {}'.format(email))
            
            return render_template('confirm.html')
        
        error_message = 'This email already register! Use another one!'
        
    return render_template('index.html', error_message=error_message)

@login_required
@app.route('/_login_request/user_<email>/token_<token>')
def login_request(email, token):
    cur_user = User.query.filter_by(email=email, token=token).first()
    if cur_user:
        cur_user.log_counter = cur_user.log_counter + 1
        db.session.commit()

        session['user'] = cur_user.email
        
        return redirect(url_for('profile', cur_user_id=cur_user.id))

    return 'loaded, but not sign in...'

@app.route('/logout')
def logout():

    session.pop('user', None)
    
    return redirect(url_for('index'))




@app.route('/profile/<cur_user_id>')
@login_required
def profile(cur_user_id):
    user = User.query.filter_by(id=cur_user_id, email=session['user']).first()
    if user:
        log_count = user.log_counter
        return render_template('profile.html', cur_user = user.email, log_count=log_count)
    return redirect(url_for('index'))



@app.route('/delete_users/')
def delete_users():
    users = User.query.all()
    for user in users:
        db.session.delete(user)
        db.session.commit()
    return 'users deleted'




