# ignored .svg files for git, may want to check/update static files

from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app=Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
app.secret_key="super-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/cu'
db=SQLAlchemy(app)

message = 'Your vaccine is pending. \nContact : '
phone = "8146080631"
name = 'Vaccicare'


class Login(db.Model):
    cid=db.Column(db.Integer, primary_key=True)
    pemail=db.Column(db.String(50),unique=True, nullable=False)
    ppass=db.Column(db.String(50),unique=True,nullable=False)


class Child(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(50),nullable=False)
    pname = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(12), nullable=False)
    weight = db.Column(db.Integer,nullable=False)
    phone = db.Column(db.Integer,nullable=False)
    gender = db.Column(db.String(12),nullable=False)


class Vaccs(db.Model):
    vid = db.Column(db.Integer, primary_key=True)
    vname = db.Column(db.String(100),nullable=False)
    age = db.Column(db.String(50),nullable=False)
    dose = db.Column(db.String(50),nullable=False)


class Vcc(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer, nullable=False)
    vid = db.Column(db.Integer, nullable=False)
    vname = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(50), nullable=False)
    dose = db.Column(db.String(50), nullable=False)


@app.route('/', methods=['GET','POST'])
def home():
    return redirect('/index')


@app.route('/index', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        cid = request.form.get('cid')
        name = request.form.get('email')
        pwd = request.form.get('pass')

        if Login.query.filter_by(pemail=name).first():
            if Login.query.filter_by(ppass=pwd).first():
                session['cid'] = cid
                session['user'] = name
                posts = Vcc.query.filter_by(cid=session['cid']).all()
                return render_template('logmain.html', cname=session['user'], posts=posts)

        i = "invalid id/ password"
        return render_template('login.html', i=i)
    return render_template('login.html')


@app.route('/logmain')
def logmain():
    posts = Vcc.query.filter_by(cid=session['cid']).all()
    return render_template('logmain.html', cname=session['user'] ,posts=posts)



@app.route('/regmain', methods=['GET','POST'])
def regmain():
    if request.method=='POST':
        cname = request.form.get('first_name')
        pname = request.form.get('father_name')
        dob = request.form.get('dob')
        weight = request.form.get('weight')
        pwd = request.form.get('pwd')
        email = request.form.get('email')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        entry2 = Child(cname=cname, pname=pname, phone=phone, dob=dob, weight=weight, gender=gender)
        db.session.add(entry2)
        db.session.commit()
        last_item = Child.query.order_by(Child.id.desc()).first()
        entry1 = Login(cid=last_item.cid ,pemail=email, ppass=pwd)
        db.session.add(entry1)
        db.session.commit()
    return render_template('regmain.html')


@app.route('/vaccines')
def vaccines():
    posts = Vaccs.query.all()
    return render_template('admin.html', posts=posts)


@app.route('/cvac', methods=['GET','POST'])
def cvac():
    posts = Vaccs.query.all()
    if request.method == 'POST':
        cid = session['cid']
        vid = request.form.get('vid')
        vname = request.form.get('vname')
        age = request.form.get('age')
        dose = request.form.get('dose')
        entry = Vcc(cid=session['cid'], vid=vid, vname=vname, age=age, dose=dose)
        db.session.add(entry)
        db.session.commit()
        #print(check)
    return render_template('cvac.html', posts=posts)



@app.route('/notify', methods=['GET','POST'])
def notify():
    if request.method == 'POST':
        email = request.form.get('email')
        mail.send_message('New message from ' + name,
                          sender= email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone
                          )
        return redirect('/')
    return render_template('notify.html')


@app.route("/logout")
def logout():
    session.pop('user')
    session.pop('cid')
    return redirect("/")


app.run(debug=True)