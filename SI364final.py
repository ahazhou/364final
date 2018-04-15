import os, requests, json
from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

#Application Configuration Setup
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'SI364FinalHardToGuessSecretKey'

#DB Creation Setup
#createdb -U postgres shelldb_example
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:arnoldzhoumi14@localhost/SI364projectplanahzhou"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Additional Setup
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

#Login configuration Setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager

########################
######## Models ########
########################

#Association Tables
#many photos to man collections prepared by users
user_collection = db.Table('user_collection', db.Column('personalphotocollection_id', db.Integer, db.ForeignKey('personalfolders.id')), db.Column('image_id', db.Integer, db.ForeignKey('images.id')))


#Models
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    userfolders = db.relationship('PersonalFolders', backref='User')
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
## DB load function
## Necessary for behind the scenes login manager that comes with flask_login capabilities! Won't run without this.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class PersonalFolder(db.Model):
    __tablename__ = "personalfolders"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    #one to many relationship with user model
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    #many to many relationship with the images model
    image = db.relationship('Image', secondary=user_collection, backref=db.backref('personalfolders',lazy='dynamic'), lazy='dynamic')

class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    imageURL = db.Column(db.String(256))
    sourceURL = db.Column(db.String(256))
    def __repr__(self):
        return "{%s}" % (self.sourceURL)

#encompasses all search history
class SearchHistory(db.Model):
    __tablename__ = "searchhistory"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    searchterm = db.Column(db.String(255))
    def __repr__(self):
        return "{%s}" % (self.searchterm)

#encompasses all images that have been saved
class ImageSavedHistory(db.Model):
    __tablename__ = "imagessavedhistory"
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer)

########################
######## Forms ########
########################

########################
### Helper functions ###
########################

########################
######## Routes ########
########################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def default():
    return redirect(url_for('index'))

@app.route('/index')
#intro to what this project is as well as some stock images in the background or something
def index():
    pass

@app.route('/register',methods=["GET","POST"])
#register for username
def register()
    pass

@app.route('/login',methods=["GET","POST"])
#login page
def login():
    pass

@app.route('/logout')
@login_required
#logout
def logout():
    pass

@app.route('/liked/<image_id>')
#all users who liked specific image (get request)
def liked():
    pass

@app.route('/createfolder')
#create folder
def createfolder():
    pass

@app.route('/userfolders')
#define all folders for specific user (post request)
def folders():
    pass

@app.route('/imagehistorysaved')
#see all images saved
def savedimages():
    pass

@app.route('/searchedtermhistory')
#all search terms
def searchhistory():
    pass

    
if __name__ == '__main__':
    db.create_all()
    manager.run()