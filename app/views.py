from flask import jsonify,render_template,redirect,flash,url_for,request,g
from models import *
from app import app,db,auth,mail
from datetime import datetime
import json
from datetime import datetime
from token import generate_confirmation_token,confirm_token
import json


#only index here move ahead
@app.route("/")
@app.route("/index",methods=["GET"])
def index():
    return jsonify({"msg":"kamehameha"})


#helper function to verify password
@auth.verify_password
def verify_password(token):
    user=None
    if request.json.has_key("token"):
        user=Guser.verify_auth_token(request.json["token"])
    if not user:
        return False
    else:
        g.user=user
        return True


#user logs in
@app.route("/login",methods=["GET","POST"])
def login():
    if request.json.has_key("token"):
        return after_request(jsonify({"msg":"looks like the user is already logged in"}))
    data=request.json
    username_or_email=data["username"]
    if username.__contains__("@a"):
        guser=Guser.query.filter(Guser.emailid==username_or_email)
        if guser.count()==0:
            return jsonify({"err":"No such user exists"})
        elif guser[0] and guser[0].has_key("password") and guser[0].check_password(data["password"]):
            return jsonify({"token":guser[0].generate_auth_token()})
        else:
            return jsonify({"err":"wrong credentials"})
    else:
        guser=Guser.query.filter(Guser.username==username_or_email)
        if guser.count()==0:
            return jsonify({"msg":"No such user exists"})
        elif guser[0] and guser[0].has_key("password") and guser[0].check_password(data["password"]):
            return jsonify({"token":guser[0].generate_auth_token()})
        else:
            return jsonify({"err":"wrong credentials"})

@app.route("/logout",methods=["GET","POST"])
@auth.login_required
def logout():
    return jsonify({"msg":"Successfully logged out"})

#new user enters
@app.route("/adduser",methods=["POST"])
def adduser():
    data=request.json
    if data.has_key("token"):
        return jsonify({"err":"The user already has a token associated with himself.Cannot accept this request"})
    #now the real auth starts here.Note first let's check for req fields.
    username=data["username"]
    msg=helper_functions.satisfy_username(username)
    if not msg=='':
        return jsonify({"data":request.json,"field_responsible":username,"msg":msg})
    emailid=data["emailid"]
    msg=helper_functions.satisfy_emailid(emailid)
    if not msg=='':
        return jsonify({"data":request.json,"field_responsible":email_id,"msg":msg})

    # if I have reached till here then the basic auth has been completed.Now let's roll the user in.
    user=Guser(username=username,emailid=emailid)
    user.confirmed=False
    user.member_since=datetime.utcnow()
    db.session.add(user)
    db.session.commit()

    #Now that the user has been added to the database let's send him a confirmation token and generate the auth token
    email_token=generate_confirmation_token(user.email)
    confirm_url=url_for("confirm_email",token=token,_external=True)
    html=render_template("activate.html",confirm_url=confirm_url)
    subject="Please confirm your email"
    send_email(user.email,subject,html)
    token=user.generate_auth_token()
    return jsonfiy({"token":token,"msg":"Email confirmation sent"})



#confirm email function
@app.route("/confirm/<token",methods=["GET"])
@auth.login_required
def confirm_email(token):
    try:
        email=confirm_token(token)
    except:
        return jsonify({"err":"The confirmation link is invalid or has expired","danger"})
    user=Guser.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        return jsonfiy({"err":"User Already confirmed"})
    else:
        user.confirmed=True
        user.confirmed_on=datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        return after_request(jsonify({"msg":"user successfully added"}))


#send email function
def send_email(to,subject,template):
    msg=Message(subject,recipients=[to],html=template,sender=app.config['MAIL_DEFAULT_SENDER'])
    mail.send(msg)



#view profile edit it upload stuff edit informations and many more
@app.route("/viewprofile",methods=["POST"])
@auth.login_required
def viewprofile():
    data=request.json
    user=g.user
    return user.full_serialize()

@app.route("/resend",methods=["POST"])
@auth.login_required
def resend_confirmation():
    user=g.user
    email_token=generate_confirmation_token(user.emailid)
    confirm_url=url_for("confirm_email",token=email_token,_external=True)
    html=render_template("activate.html",confirm_url=confirm_url)
    subject="Please confirm your email"
    send_email(user.emailid,subject,html)
    return after_request(jsonify({"msg":"email confirmation sent successfully"}))

@app.route("/add_education",methods=["POST"])
@auth.login_required
def add_education():
    data=request.json
    name=data["name"]
    country=data["country"]
    state=data["country"]
    typ=data["type"]
    current_status=data["current_status"]
    percentage=float(data["percentage"])
    if helper_functions.check_edu_presence():
        return after_request(jsonify{"err":"looks like edu already present"})
    edu=Education(name=name)
    edu.country=country
    edu.state=state
    db.session.add(edu)
    db.session.commit()
    user=g.user
    user.educations.append(edu,typ=typ,current_status=current_status,percentage=percentage)
    db.session.add(user)
    db.session.commit()
    return after_request(jsonify({"msg":"successfully added"}))

@app.route("/update_education",methods=["POST"])
@auth.login_required
def update_education():
    edu_id=request.json["id"]
    education=Education.query.filter_by(id=edu_id).first()
    typ=request.json["type"]
    current_status=request.json["current_status"]
    if helper_functions.check_edu_and_user(education,g.user,typ):
        return after_request(jsonify({"msg":"looks like user already has this edu"}))
    g.user.education.append(education,typ=typ,current_status=current_status,percentage=percentage)
    db.session.add(g.user)
    db.session.commit()
    return after_request(jsonify({"msg":"Successfully Updated"}))

@app.route("/get_all_educations")
def get_all_educations():
    edus=Education.query.all()
    l=[]
    for edu in edus:
        l.append(edu.full_serialize())
    return after_request(jsonify({"educations":l})


@app.route("/get_all_user_educations")
def get_all_user_educations():
	return after_request(jsonify({"educations":g.user.educations_serialize()}))


@app.route("add_mobileno",methods=["POST"])
@auth.login_required
def add_mobileno():
    user=g.user
    user.mobileno=request.json["mobileno"]
    db.session.add(user)
    db.session.commit()
    return after_request(jsonify({"msg":"mobile no successfully added"}))

@app.route("user_first_name",methods=["POST"])
@auth.login_required
def user_first_name():
    user=g.user
    user.first_name=request.json["first_name"]
    db.session.add(user)
    db.session.commit()
    return after_request(jsonify({"msg":"First Name updated Successfully"}))

@app.route("/user_last_name",methods=["POST"])
@auth.login_required
def user_last_name():
    user=g.user
    user.last_name=request.json["last_name"]
    db.session.add(user)
    db.session.commit()
    return after_request(jsonify({"msg":"Last Name Updated Successfully"}))

@app.route("/update_user_skill",methods=["POST"])
@auth.login_required
def update_user_skill():
	user=g.user
	skill_id=int(request.json["id"])
	for ski in user.skills:
		if ski.id==skill_id:
			return after_request(jsonify({"msg":"User already has this skill"}))
	try:
		skill=Skill.query.filter(Skill.id==skill_id)[0]
	except:
		return after_request(jsonify({"err":"no such skill found"}))
	user.skills.append(skill,level=request.json["level"])
	return after_request(jsonify{"msg":"successfully added skill to skill set"})

@app.route("/get_user_skills",methods=["POST"])
@auth.login_required
def get_user_skills():
	return after_request(jsonify({"skills":g.user.skills_serialize()}))

@app.route("/get_all_skills",methods=["POST"])
@auth.login_required
def get_all_skills():
	l=[]
	skills=Skill.query.all()
	for skill in skills:
		l.append(skill.full_serialize())
	return after_request(jsonify({"skills":l}))

@app.route("/update_user_availability",methods=["POST"])
@auth.login_required
def update_user_availability():
	user=g.user
	availability_id=int(request.json["availability_id"])
	for avai in user.availabilities:
		if avai.id==availability_id:
			return after_request(jsonify({"msg":"User already has this availability."}))
	try:
		availability=Availability.query.filter(Availability.id==availability_id)[0]
	except:
		return after_request(jsonify({"msg":"no such availability found"}))
	description=''
	if request.json.has_key("description"):
		description=request.json["description"]
	user.availabilities.append(availability,description=description)
	return after_request(jsonify{"msg":"successfully updated user availability"})

@app.route("/get_all_availabilities",methods=["POST"])
@auth.login_required
def get_all_availabilities():
	availabilities=Availability.query.all()
	l=[]
	for avai in availabilities:
		l.append(avai.full_serialize())
	return after_request(jsonify({"availabilities":l}))

@app.route("/get_all_user_availabilities",methods=["POST"])
@auth.login_required
def get_all_user_availabilities():
	return after_request(jsonify({"availabilities":g.user.avalabilities_serialize()}))

@app.route("/update_user_preferences",methods=["POST"])
@auth.login_required
def update_user_preferences():
	preference_id=int(request.json["preference_id"])
	user=g.user
	for pre in user.preferences:
		if pre.id==preference_id:
			return after_request(jsonify{"err":"Looks like user already has that preference"})
	try:
		preference=Preference.query.filter(Preference.id==preference_id)[0]
	except:
		return jsonify({"err":"No such preference exists"})
	user.preferences.append(preference)
	return after_request(jsonify({"msg":"preference added successfully."}))

@app.route("/show_all_preferences",methods=["POST"])
@auth.login_required
def show_all_preferences():
	l=[]
	preferences=Preference.query.all()
	for preference in preferences:
		l.append(preference.full_serialize())
	return after_request(jsonify({"preferences":l}))

@app.route("/show_all_user_preferences",methods=["POST"])
@auth.login_required
def show_all_user_preferences():
	return after_request(jsonify({"user_preferences":g.user.preferences_serialize()}))