from flask import Flask, render_template, flash, url_for, request
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

from forms import RegistrationForm, LoginForm

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY


class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), index=True, unique=True)
  email = db.Column(db.String(150), unique=True, index=True)
  password_hash = db.Column(db.String(150))
  joined_at = db.Column(db.DateTime(), default=datetime.utcnow, index=True)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
  return User.get(user_id)


#routes


@app.route('/')
def home():
  return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data)
    user.set_password(form.password1.data)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('login'))
  return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user is not None and user.check_password(form.password.data):
      login_user(user)
      next = request.args.get("next")
      return redirect(next or url_for('home'))
    flash('Invalid email address or Password.')
  return render_template('login.html', form=form)


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
