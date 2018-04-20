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
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:arnoldzhoumi14@localhost/SI364finalahzhou"
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
    name = db.Column(db.String(15))
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
    user_id = db.Column(db.Integer)
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
            flash('Email already registered')
            raise ValidationError('Email already registered')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            flash('Username taken')
            raise ValidationError('Username taken')
        if field.data == "Anonymous":
            flash("Cannot use name: Anonymous")
            raise ValidationError('Cannot use name: Anonymous')

class FavoriteImageSubmit(FlaskForm):
    submit = SubmitField("Add to Favorites")

class CreateNewFolder(FlaskForm):
    foldername = StringField("Folder name:", validators=[Required()])
    submit = SubmitField("Create")
    update = SubmitField("Update")
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if len(self.foldername.data) > 15:
            flash("Invalid name: " + self.foldername.data)
            flash("Name can be at most 15 characters.")
            return False

        if self.foldername.data.find('#') != -1:
            flash("Invalid name: " + self.foldername.data)
            flash("Name cannot contain character '#'.")
            return False
        if self.foldername.data.find(' ') != -1:
            flash("Invalid name: " + self.foldername.data)
            flash("Name cannot contain spaces.")
            return False
        return True

class DeleteObject(FlaskForm):
    delete = SubmitField("Delete")

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

def get_or_create_searchterm(searchterm, username):
    if username == None or not current_user.is_authenticated:
        username = "Anonymous"
    user_id = User.query.filter_by(username=username).first()
    if user_id != None:
        user_id = user_id.id
    else:#what if there's no anonymous entry in the database?
        #we create it
        db.session.add(User(username="Anonymous", email="Anonymous", password="Anonymous"))
        db.session.commit()
        user_id = User.query.filter_by(username="Anonymous").first()

    search = SearchHistory.query.filter_by(user_id=user_id, searchterm=searchterm).first()
    if search == None:
        search = SearchHistory(user_id=user_id, searchterm=searchterm)
        db.session.add(search)
        db.session.commit()
    return search

def get_or_create_image(imageID, search=False):
    image = Image.query.filter_by(imageID = imageID).first()
    if image == None and search == False:
        image_information = gettyAPICall(imageID=imageID)
        image = Image(imageID=imageID, imageURL=image_information["images"][0]["display_sizes"][0]["uri"], sourceURL=image_information["images"][0]["referral_destinations"][0]["uri"])
        db.session.add(image)
        db.session.commit()
    return image

def get_or_create_folder_collection(foldername, imageID=-1):
    current_user_id = User.query.filter_by(username=current_user.username).first().id
    current_user_folder = PersonalFolder.query.filter_by(name=foldername, user_id=current_user_id).first()
    if current_user_folder == None:#we have to create the folder and we don't want to add the image directly because it's annoying
        current_user_folder = PersonalFolder(name=foldername, user_id=current_user_id)
        db.session.add(current_user_folder)
        db.session.commit()
        return current_user_folder
    #otherwise if the folder already exists
    if imageID == -1:#if not given, we return the current_folder
        return current_user_folder
    current_image = get_or_create_image(imageID)
    #add image to current folder
    current_user_folder.image.append(current_image)
    db.session.add(current_user_folder)
    #add to search history
    imageSavedHistory = ImageSavedHistory(image_id=imageID)
    db.session.add(imageSavedHistory)
    db.session.commit()
    return current_user_folder

def folder_exists(foldername):
    current_user_id = User.query.filter_by(username=current_user.username).first().id
    current_user_folder = PersonalFolder.query.filter_by(name=foldername, user_id=current_user_id).first()
    if current_user_folder == None:
        return False
    return True

def image_exists_in_folder(foldername, imageID):
    current_user_id = User.query.filter_by(username=current_user.username).first().id
    current_user_folder = PersonalFolder.query.filter_by(name=foldername, user_id=current_user_id).first()
    current_image = get_or_create_image(imageID, search=True)
    if current_user_folder == None or current_image == None:
        return False
    if current_user_folder.image.filter_by(id = current_image.id).first() == None:
        return False
    return True

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

    if current_user.is_authenticated:
        current_userID = User.query.filter_by(username=current_user.username).first().id
    else:
        current_userID = None
    if current_userID == None:
        current_userID = User.query.filter_by(username="Anonymous").first()
        if current_userID != None:
            current_userID = current_userID.id
            user_search_history = SearchHistory.query.filter_by(user_id=current_userID).all()
            recent_saved_images_id = ImageSavedHistory.query.all()
            recent_saved_images = []
            for index in recent_saved_images_id:
                recent_saved_images.append(Image.query.filter_by(imageID=str(index.image_id)).first())
            #goes to this if everything's all good
            return render_template("index.html", form=form, user_search_history=user_search_history, recent_saved_images=recent_saved_images)
    return render_template("index.html", form=form)

@app.route('/foundimages')
#show all of the images from the search result based in the index and be able to add image
def foundimages():
    searchterm = ""
    if request.args.get("searchterm") != None:
        if current_user.is_authenticated:
            current_username = current_user.username
        else:
            current_username = "Anonymous"
        get_or_create_searchterm(request.args.get("searchterm"), current_username)
        searchterm = request.args.get("searchterm")
        foundimages = gettyAPICall(phrase=searchterm)
        return render_template("foundimages.html", searchterm=searchterm, foundimages=foundimages, form=FavoriteImageSubmit())
    return redirect(url_for('index'))

@app.route('/addtofavorites/<imageID>/<searchterm>', defaults={'foldername': None},methods=["GET","POST"])
@app.route('/addtofavorites/<imageID>/<searchterm>/<foldername>',methods=["GET","POST"])
#select and add to favorites folder (but only if it's a new folder)
def addtofavorites(imageID, searchterm, foldername):
    form=FavoriteImageSubmit()
    create_folder_form=CreateNewFolder()
    if create_folder_form.validate_on_submit() and create_folder_form.foldername.data != None:#post request if folder doesn't exist
        get_or_create_folder_collection(create_folder_form.foldername.data)
    if imageID != None and searchterm != None:#when first land on this page
        if not current_user.is_authenticated:
            flash("Please log in.")
            return redirect(url_for("login"))
        user_id = User.query.filter_by(username=current_user.username).first().id
        if user_id == None:
            return redirect(url_for("register"))
        user_folders = PersonalFolder.query.filter_by(user_id=user_id).all()#get all the folder names
        return render_template("addtofavorites.html", imageID=imageID, user_folders=user_folders, form=form, create_folder_form=create_folder_form, searchterm=searchterm)
    return redirect(url_for('foundimages', searchterm=searchterm))

@app.route('/api/addimgfolder',methods=["GET","POST"])
#Add img to folder
def add_img_to_folder():###TODO
    if request.method == 'GET' and request.args.get("imageID") != None and request.args.get("foldername") != None:
        cur_imageID = request.args.get("imageID")
        cur_foldername = request.args.get("foldername")
        if not image_exists_in_folder(cur_foldername, cur_imageID):
            get_or_create_folder_collection(cur_foldername, cur_imageID)
            return "success"
        return "exists"
    return ('', 500)

@app.route('/register',methods=["GET","POST"])
#register for username
def register():
    if current_user.is_authenticated:
        return ('', 204)
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm.data:
            flash("Passwords don't match up.")
            return render_template("register.html", form=form)
        #CREATE ANONYMOUS USER
        if User.query.filter_by(username="Anonymous").first() == None:
            db.session.add(User(username="Anonymous", email="Anonymous", password="Anonymous"))
            db.session.commit()
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
        user = User.query.filter_by(username=form.username.data).first()
        if user == None:
            flash("No user found.")
        elif user.verify_password(form.password.data):
            login_user(user, form.loggedin.data)
            return redirect(url_for("index"))
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
#logout
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/userfolders', defaults={'foldername': None},methods=["GET","POST"])
@app.route('/userfolders/<foldername>',methods=["GET","POST"])
#define all folders for specific user (post request)
def folders(foldername):
    update = CreateNewFolder()
    if update.validate_on_submit():
        if update.foldername.data != foldername:
            if folder_exists(update.foldername.data):
                flash("Foldername exists.")
            else:
                current_folder = get_or_create_folder_collection(foldername)
                current_folder.name = update.foldername.data
                db.session.commit()
    if not current_user.is_authenticated:
        return ('', 204)
    user_id = User.query.filter_by(username=current_user.username).first().id
    if user_id == None:
        return redirect(url_for("register"))
    user_folders = PersonalFolder.query.filter_by(user_id=user_id).all()#get all the folder names
    return render_template("userfolders.html", user_folders=user_folders, form=DeleteObject(), update=update)

@app.route('/folder',methods=["GET","POST"])
#all search terms
def open_folder():
    if request.method == 'GET' and request.args.get("foldername") != None:
        form = DeleteObject()
        current_userID = User.query.filter_by(username=current_user.username).first().id
        if current_userID == None:
            current_userID = User.query.filter_by(username="Anonymous").first().id
        folderImages = PersonalFolder.query.filter_by(name=request.args.get("foldername"), user_id=current_userID).first().image.all()
        return render_template("folderImages.html", foldername=request.args.get("foldername"), folderImages=folderImages, form=form)
    return ('', 204)

@app.route('/delete/<objecttype>/<objectname>/<albumname>',methods=["GET","POST"])
#delete either photo from album or delete album
def delete_object(objecttype,objectname,albumname):
    if objecttype != None and objectname != None and albumname != None:
        current_userID = User.query.filter_by(username=current_user.username).first().id
        if current_userID == None:
            current_userID = User.query.filter_by(username="Anonymous").first().id

        if objecttype == "folder":#delete entire folder
            chosen_folder = PersonalFolder.query.filter_by(name=objectname, user_id=current_userID).first()
            db.session.delete(chosen_folder)
            db.session.commit()
            return redirect(url_for('folders'))
        elif objecttype == "image":#delete image from folder
            user_images = PersonalFolder.query.filter_by(name=albumname, user_id=current_userID).first().image
            current_image = user_images.filter_by(id=objectname).first()
            db.session.delete(current_image)
            db.session.commit()
            return redirect(url_for('folders'))
    return ('', 204)
    
if __name__ == '__main__':
    db.create_all()
    manager.run()