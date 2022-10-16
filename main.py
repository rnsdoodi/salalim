
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import smtplib
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField, IntegerField, FileField
from wtforms.validators import DataRequired, URL
import csv
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os


OWN_EMAIL = "rnsdoodi9@gmail.com"
OWN_PASSWORD = "mhscrjgbtflymwbz"

all_cvs = []
all_users = []

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "any secret key yes")
####################################################


Bootstrap(app)
###################################################

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(Admin_id):
    return Admins.query.get(int(Admin_id))


#################################################

# CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///candidates.db")
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CREATE USERS TABLE
# PARENT
class User(db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, nullable=False)
    Name = db.Column(db.String(250), nullable=False)
    Contact = db.Column(db.Integer, nullable=False)
    Nid = db.Column(db.Integer, nullable=False)
    Visa = db.Column(db.Integer, nullable=False)
    resume = db.relationship('BioData', backref='resumes')
    resume_id = db.Column(db.Integer, db.ForeignKey('bio_data.id'))


# Child
class BioData(db.Model):
    __tablename__ = "bio_data"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)  # name
    rating = db.Column(db.Integer, nullable=False)  # Age
    review = db.Column(db.String(250), nullable=False)  # type
    img_url = db.Column(db.String(1000), nullable=False)
    resume = db.Column(db.String(1000), nullable=False)
    video = db.Column(db.String(1000), nullable=False)
    selector = relationship('User', backref='bio')


#######################################################################
# New Table :

class Temp(db.Model):
    __tablename__ = "temp"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)  # name
    rating = db.Column(db.Integer, nullable=False)  # Age
    review = db.Column(db.String(250), nullable=False)  # type
    img_url = db.Column(db.String(1000), nullable=False)
    resume = db.Column(db.String(1000), nullable=False)
    video = db.Column(db.String(1000), nullable=False)

#######################################################################


# CREATE TABLE IN DB To save users login Data (Hashed & Salted)
class Admins(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(250))


db.create_all()


# Add Cv Flask Form
class AddCv(FlaskForm):
    title = StringField('worker name اسم العاملة', validators=[DataRequired()])
    rating = IntegerField('worker age العمر', validators=[DataRequired()])
    review = StringField('worker position المهنة', validators=[DataRequired()])
    img_url = StringField('worker image الصورة', validators=[DataRequired()])
    resume = StringField('CV السيرة الذاتية', validators=[DataRequired()])
    video = StringField(' الفيديو', validators=[DataRequired()])
    submit = SubmitField('Add إضافة')


# Edit Cv Flask Form
class EditCv(FlaskForm):
    title = StringField('worker name اسم العاملة', validators=[DataRequired()])
    rating = StringField('worker age العمر', validators=[DataRequired()])
    review = StringField('worker position المهنة', validators=[DataRequired()])
    # img_url = StringField('worker image الصورة', validators=[DataRequired(), URL()])
    submit = SubmitField('تعديل')


# Select Candidate Form (For Users)
class Choice(FlaskForm):
    Name = StringField('ادخل الاسم', validators=[DataRequired()])
    Contact = IntegerField('رقم الجوال', validators=[DataRequired()])
    Nid = IntegerField('رقم الهوية/الإقامة', validators=[DataRequired()])
    Visa = StringField('رقم التأشيرة(الصادر)', validators=[DataRequired()])
    author_id = IntegerField('Worker ID الرجاء إدخال رقم تعريف العاملة المطلوبة ', validators=[DataRequired()])
    submit = SubmitField('اختيار')


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/select")
def select():
    return render_template("cards.html")


@app.route("/philippines")
def philippines():
    all_cvs = Temp.query.all()
    return render_template("philippines.html", cvs=all_cvs)


@app.route("/kenya")
def kenya():
    return render_template("kenya.html", cvs=all_cvs)


@app.route("/contact", methods=["GET", "POST"])
def get_data():
    if request.method == "POST":
        name = request.form["full-name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        send_email(name, email, phone, message)

        return render_template("index.html", msg_sent=True)
    return render_template("index.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message.encode("UTF-8"))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddCv()

    if form.validate_on_submit():
        new_resume = Temp(
            title=form.title.data,
            rating=form.rating.data,
            review=form.review.data,
            img_url=form.img_url.data,
            resume=form.resume.data,
            video=form.video.data
        )

        new_cv = BioData(
            title=form.title.data,
            rating=form.rating.data,
            review=form.review.data,
            img_url=form.img_url.data,
            resume=form.resume.data,
            video=form.video.data
        )

        with open("cvs-data.csv", mode="a", encoding="utf8") as csv_file:
            csv_file.write(f"\n{form.title.data},"
                           f"{form.rating.data},"
                           f"{form.review.data},"
                           f"{form.img_url.data},"
                           f"{form.resume.data},"
                           f"{form.video.data}"
                           )

        # file = form.img_url.data
        # file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
        #                        secure_filename(file.filename)))

        db.session.add(new_cv)
        db.session.add(new_resume)
        db.session.commit()
        all_cvs.append(new_cv)
        all_cvs.append(new_resume)
        flash("✔!! تم إضافة العاملة بنجاح ")
        return redirect(url_for('add'))

    return render_template("add.html", form=form, cv=cvs)


#######################################################################################################################

# @app.route("/downloads/tos/")
# def tos():
#     workingdir = os.path.abspath(os.getcwd())
#     filepath = workingdir + '/static/uploads/'
#     return send_from_directory(filepath, 'tos.pdf')


########################################################################################################################
@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditCv()
    cv_id = request.args.get("id")
    updated_cv = BioData.query.get(cv_id)
    if form.validate_on_submit():
        updated_cv.title = form.title.data
        updated_cv.rating = form.rating.data
        updated_cv.review = form.review.data
        # updated_cv.img_url = form.img_url.data
        db.session.commit()
        flash("✔ تم تعديل بيانات العاملة بنجاح")
        return redirect(url_for('Dh_list'))
    return render_template("edit.html", form=form, cv=updated_cv)


@app.route("/delete")
def delete():
    cv_id = request.args.get("id")
    cv_to_delete = BioData.query.get(cv_id)
    db.session.delete(cv_to_delete)
    db.session.commit()
    flash("✔ تم حذف العاملة بنجاح")
    return redirect(url_for('Dh_list'))


@app.route("/choice/<int:cvs_id>", methods=["GET", "POST"])
def choice(cvs_id):
    form = Choice()
    cv_id = request.args.get("id")
    cv_to_select = Temp.query.get(cv_id)
    selector = cvs_id
    if form.validate_on_submit():
        new_user = User(
            Name=form.Name.data,
            Contact=form.Contact.data,
            Nid=form.Nid.data,
            Visa=form.Visa.data,
            author_id=form.author_id.data,
            resume_id=selector
        )

        if form.author_id.data == cvs_id:
            cv_to_select = db.session.query(Temp).get(cvs_id)
            db.session.delete(cv_to_select)
            db.session.commit()
            flash(" ✔ !!! تم الاختيار بنجاح  ")
        else:
            flash("لقد قمت بإدخال رقم تعريف خاطئ , الرجاء التأكد من رقم التعريف والمحاولة مرة أخرى ")
            new_user = User(
                Name='N/A',
                Contact='0',
                Nid='0',
                Visa='0',
                author_id='0',
                resume_id='0'

            )

        db.session.add(new_user)
        db.session.commit()
        all_users.append(new_user)

        return redirect(url_for('philippines'))
    return render_template("choice.html", form=form, users=all_users, select=cv_to_select, cvs=all_cvs, cv=cvs_id)


@app.route("/cvs")
def cvs():
    with open('cvs-data.csv', newline='', encoding="utf8") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
        return render_template('cvs.html', cvs=list_of_rows)


@app.route("/list")
def Dh_list():
    added_cvs = BioData.query.all()
    return render_template("list.html", cvs=added_cvs)


@app.route("/selections")
def selections():
    new_user = User.query.all()
    return render_template("selections.html", users=new_user, cvs=all_cvs)


@app.route("/reject/<int:users_id>", methods=["GET", "POST"])
def reject(users_id):
    user_to_delete = db.session.query(User).get(users_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(" ✔ تم رفض الطلب  ")

    return redirect(url_for('selections'))


@app.route("/policy")
def policy():
    return render_template("policy.html")


########################################################################################################################
# Authentication Part for (Admins) :-


# @app.route("/")
# def landing():
#     return render_template("admin.html")

@app.route('/admins')
def sign():
    return render_template("main.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if Admins.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_admin = Admins(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_admin)
        db.session.commit()
        login_user(new_admin)
        flash("تم التسجيل بنجاح, رجاءا قم بالعودة الى صفحة الدخول")
        return redirect(url_for("register"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        admin = Admins.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not admin:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(admin.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(admin)
            return redirect(url_for('admin'))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sign'))


@app.route('/add')
@login_required
def admin():
    print(current_user.name)
    all_cvs = cvs.query.all()
    return render_template("add.html", cvs=all_cvs, logged_in=True, name=current_user.name)


########################################################################################################################
if __name__ == "__main__":
    app.run(debug=True)
