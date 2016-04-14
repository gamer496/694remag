from app import db,app
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy_utils import ScalarListType,force_auto_coercion
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,BadSignature,SignatureExpired)
from datetime import datetime
from sqlalchemy_utils import ChoiceType,ScalarListType

force_auto_coercion()


guserseducations=db.Table('guserseducations',
        db.Column('education_id',db.Integer,db.ForeignKey('education.id')),
        db.Column('guser_id',db.Integer,db.ForeignKey('guser.id')),
        db.Column('typ',db.String(100)),
        db.Column('current_status',db.String(100)),
        db.Column('percentage',db.Float)
        )

gusersskills=db.Table('gusersskills',
        db.Column('skill_id',db.Integer,db.ForeignKey('skill.id')),
        db.Column('guser_id',db.Integer,db.ForeignKey('guser.id')),
        db.Column('level',db.String(50))
        )

gusersavailabilities=db.Table('gusersavailabilities',
        db.Column('availability_id',db.Integer,db.ForeignKey('availability.id')),
        db.Column('guser_id',db.Integer,db.ForeignKey('guser.id')),
        db.Column('letter',db.Text)
        )

guserspreferences=db.Table('guserspreferences',
        db.Column('preference_id',db.Integer,db.ForeignKey('preference.id')),
        db.Column('guser_id',db.Integer,db.ForeignKey('guser.id'))
        )


class Preference(db.Model):
    __tablename__="preference"
    id                  =db.Column          (db.Integer,primary_key=True)
    state_country_name  =db.Column          (db.String(250),index=True)

class Skill(db.Model):
    __tablename__="skill"
    id              =db.Column          (db.Integer,primary_key=True)
    name            =db.Column          (db.String(250),index=True)

class Education(db.Model):
    __tablename__="Education"
    id              =db.Column          (db.Integer,primary_key=True)
    name            =db.Column          (db.String(250),index=True)
    state           =db.Column          (db.String(200))
    country         =db.Column          (db.String(200))

    def __init__(self,name):
        self.name=name

class Availability(db.Model):
    __tablename__="availability"
    id              =db.Column          (db.Integer,primary_key=True)
    name            =db.Column          (db.String(250),index=True)

class Guser(db.Model):

    __tablename__="guser"
    id              =db.Column          (db.Integer,primary_key=True)
    username        =db.Column          (db.String(100),unique=True,index=True)
    first_name      =db.Column          (db.String(100))
    last_name       =db.Column          (db.String(100))
    emailid         =db.Column          (db.String(100),unique=True)
    password        =db.Column          (db.String(200))
    member_since    =db.Column          (db.DateTime)
    confirmed       =db.Column          (db.Boolean)
    confirmed_on    =db.Column          (db.DateTime)
    mobileno        =db.Column          (db.String(20))
    hometown        =db.Column          (db.String(100))
    links           =db.Column          (ScalarListType())
    educations      =db.relationship    ('Education',secondary='guserseducations',backref=db.backref("gusers",lazy="dynamic"))
    skills          =db.relationship    ('Skill',secondary="gusersskills",backref=db.backref("gusers",lazy="dynamic"))
    availabilities  =db.relationship    ('Availability',secondary="gusersavailabilities",backref=db.backref("gusers",lazy="dynamic"))
    preferences     =db.relationship    ('Preference',secondary="guserspreferences",backref=db.backref("gusers",lazy="dynamic"))


    def __init__(self,username,password,emailid):
        self.username=username
        self.emailid=emailid
        self.set_password(password)
        self.member_since=datetime.utcnow()

    def set_password(self,password):
        self.password=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)

    def generate_auth_token(self):
        s=Serializer(app.config['SECRET_KEY'])
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except BadSignature:
            return None
        user=Guser.query.get(data['id'])
        return user

    def half_serialize(self):


    def __repr__(self):
        return "<User: %s>"%(self.username)

class Gemployer(db.Model):
    __tablename__="gemployer"
    id                  =db.Column      (db.Integer,primary_key=True)
    organization_name   =db.Column      (db.String(250),unique=True,index=True)
    password            =db.Column      (db.String(200))
    first_name          =db.Column      (db.String(150))
    last_name           =db.Column      (db.String(150))
    mobile_no           =db.Column      (db.String(20))

    def __init__(self,organization_name):
        self.organization_name=organization_name
        self.set_password(password)


    def set_password(self,password):
        self.password=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)

    def generate_auth_token(self):
        s=Serializer(app.config['SECRET_KEY'])
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except BadSignature:
            return None
        user=Guser.query.get(data['id'])
        return user

    def __repr__(self):
        return "Organization Name : %s"%(self.organization_name)
