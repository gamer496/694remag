import os
from information import *


#main config
SQLALCHEMY_DATABASE_URI="mysql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_HOST+"/"+DB_NAME
SQLALCHEMY_TRACK_MODIFICATIONS=True
SECRET_KEY="reality is broken"
SECURITY_PASSWORD_SALT="email salt"
DEBUG=True

#mail config
MAIL_SERVER='smtp.googlemail.com'
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True

#gmail auth
MAIL_USERNAME=MAIL_USERNAME_INFO
MAIL_PASSWORD=MAIL_PASSWORD_INFO
MAIL_DEFAULT_SENDER=MAIL_DEFAULT_SENDER_INFO