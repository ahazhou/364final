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

def makerequesttoapi(phrase = "stuff"):
    headers = {
        'Api-Key': api_key
    }
    geturl = 'https://api.gettyimages.com/v3/search/images?phrase=' + phrase
    r = requests.get(geturl, headers=headers)
    return r.json()

def imageIDRequest(imageID):
    headers = {
        'Api-Key': api_key
    }
    geturl = 'https://api.gettyimages.com/v3/images/' + str(imageID) + '?fields=id,title,thumb,referral_destinations'
    r = requests.get(geturl, headers=headers)
    return r.json()

def testroute():
    #for all of the function calls below, the term "pandas" can be replaced with any user term
    #access all values from search term
    #print(makerequesttoapi("pandas")["images"][0])
    #print("\n\n\n")
    #get specific title
    #print(makerequesttoapi("pandas")["images"][0]["title"])
    #print("\n\n\n")
    #get specific information about the display for the images to be displayed properly
    #print(makerequesttoapi("pandas")["images"][0]["display_sizes"][0]["uri"])
    print(imageIDRequest(628802586)["images"][0]["referral_destinations"][0]["uri"])



if __name__ == '__main__':
    testroute()

