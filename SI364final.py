import os, requests, json
from api_key import api_key
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
    password_hash = db.Column(db.String)
    userfolders = db.relationship('PersonalFolder', backref='User')
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

#database of all saved images
class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    imageID = db.Column(db.String(12))
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

#encompasses all images that have been saved (added whenever added to a folder)
class ImageSavedHistory(db.Model):
    __tablename__ = "imagessavedhistory"
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer)

########################
######## Forms #########
########################
class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[Required()])
    password = StringField("Password:", validators=[Required()])
    loggedin = BooleanField("Keep me logged in")
    submit = SubmitField("Login")

class SearchForm(FlaskForm):
    searchterm = StringField("Search:", validators=[Required()])
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    email = StringField("Email:", validators=[Required()])
    username = StringField("Username:", validators=[Required()])
    password = StringField("Password:", validators=[Required()])
    confirm = StringField("Confirm Password:", validators=[Required()])
    submit = SubmitField('Register')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username taken')

class FavoriteImageSubmit(FlaskForm):
    submit = SubmitField("Add to Favorites")

class CreateNewFolder(FlaskForm):
    foldername = StringField("Folder name:", validators=[Required()])
    submit = SubmitField("Create")


########################
### Helper functions ###
########################
def gettyAPICall(phrase = "", imageID = ""):
    headers = {
        'Api-Key': api_key
    }
    if phrase != "":
        geturl = 'https://api.gettyimages.com/v3/search/images?fields=id,title,thumb,referral_destinations&sort_order=best&phrase=' + phrase
        r = requests.get(geturl, headers=headers)
        return r.json()
    if imageID != "":
        geturl = 'https://api.gettyimages.com/v3/images/' + str(imageID) + '?fields=id,title,thumb,referral_destinations'
        r = requests.get(geturl, headers=headers)
        return r.json()
    return None

def get_or_create_image(imageID):
    image = Image.query.filter_by(imageID = imageID).first()
    if image == None:
        image_information = gettyAPICall(imageID=imageID)
        image = Image(imageID=imageID, imageURL=image_information["images"][0]["display_sizes"][0]["uri"], sourceURL=image_information["images"][0]["referral_destinations"][0]["uri"])
        db.session.add(image)
        db.session.commit()
    return image

def get_or_create_folder_collection(imageID, foldername):
    current_user_id = User.query.filter_by(username=current_user).first()
    current_user_folder = PersonalFolder.query.filter_by(name=foldername, user_id=current_user_id)
    current_image = get_or_create_image(imageID)
    if current_user_folder == None:#we have to create the folder so we directly add the image in
        newfolder = PersonalFolder(name=foldername, user_id=current_user_id, image=current_image)
        db.session.add(newfolder)
        db.session.commit()
        return newfolder
    #otherwise if the folder already exists
    current_user_folder.image.append(current_image)
    db.session.add(current_user_folder)
    db.session.commit()
    return current_user_folder

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
    form = SearchForm()
    if request.method == 'GET' and request.args.get("searchterm") != None:
        return redirect(url_for('foundimages', searchterm=request.args.get("searchterm")))
    return render_template("index.html", form=form)

@app.route('/foundimages')
#show all of the images from the search result based in the index and be able to add image
def foundimages():
    searchterm = ""
    if request.args.get("searchterm") != None:
        searchterm = request.args.get("searchterm")
    foundimages = gettyAPICall(phrase=searchterm)
    return render_template("foundimages.html", searchterm=searchterm, foundimages=foundimages, form=FavoriteImageSubmit())

@app.route('/addtofavorites/<imageID>/<searchterm>', defaults={'foldername': None})
@app.route('/addtofavorites/<imageID>/<searchterm>/<foldername>',methods=["GET","POST"])
#select and add to favorites folder
def addtofavorites(imageID, searchterm, foldername):
    form=FavoriteImageSubmit()
    create_folder_form=CreateNewFolder()
    if form.validate_on_submit():#post request if folder already exists
        get_or_create_folder_collection(imageID, foldername)
    if create_folder_form.validate_on_submit():#post request if folder doesn't exist
        get_or_create_folder_collection(imageID, create_folder_form.foldername)
    if imageID != None and searchterm != None:#when first land on this page
        user_id = User.query.filter_by(username=current_user).first().id
        if user_id == None:
            redirect(url_for("login"))#if you're not logged in, redirect
        user_folders = PersonalFolder.query.filter_by(user_id=user_id).all()#get all the folder names
        ##################TODO (TESTING)
        return render_template("addtofavorites.html", imageID=imageID, user_folders=user_folders, form=form, create_folder_form=create_folder_form, searchterm=searchterm)
    return redirect(url_for('foundimages', searchterm=searchterm))

@app.route('/register',methods=["GET","POST"])
#register for username
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route('/login',methods=["GET","POST"])
#login page
def login():
    form = LoginForm()
    if form.validate_on_submit():
        current_user = User.query.filter_by(username=form.username.data).first()
        if current_user == None:
            flash("No user found.")
        elif current_user.verify_password(form.password.data):
            login_user(current_user, form.loggedin.data)
            return redirect(url_for("index"))
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
#logout
def logout():
    logout_user()
    return redirect(url_for('index'))

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