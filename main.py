from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password= PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")

class PostForm(FlaskForm):
    title = StringField("Add Blog Title", validators=[DataRequired()])
    subtitle = StringField("Add Blog Subtitle", validators=[DataRequired()])
    author = StringField("Blog Author", validators=[DataRequired()])
    img_url = StringField("Add Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Add Blog Content Here", validators=[DataRequired()])
    submit = SubmitField("Done")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

with app.app_context():
    db.create_all()




@app.route('/')
@login_required
def get_all_posts():
    posts = [post for post in db.session.query(BlogPost).all()]
    return render_template("index.html", all_posts=posts)



@app.route('/<int:post_id>')
def show_post(post_id):
    requested_post = db.session.get(BlogPost, post_id)
    print(requested_post)
    return render_template("post.html", post=requested_post)


@app.route("/make-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        author = form.author.data
        img_url = form.img_url.data
        body = form.body.data
        today = date.today().strftime("%B %#d, %Y")
        try:
            new_post = BlogPost(title=title, subtitle=subtitle, author=author, img_url=img_url, body=body, date=today)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return redirect("/")
    return render_template("make-post.html", form=form)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = db.session.get(BlogPost, id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        try:
            post.title = form.title.data
            post.subtitle = form.subtitle.data
            post.author = form.author.data
            post.img_url = form.img_url.data
            post.body = form.body.data
            db.session.commit()
            return redirect("/")
        except SQLAlchemyError as e:
            print(e)
            return redirect("/")
    return render_template("edit.html", form=form)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    try:
        post = db.session.get(BlogPost, id)
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        return redirect(url_for("get_all_posts"))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")
        else:
            flash(message="Username of password is incorrect", )
            return redirect("/login")
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = generate_password_hash(form.password.data, "pbkdf2:sha256", 8)
        name = form.name.data
        try:
            new_user = User(email=email, password=password, name=name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect("/")
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback()
            return redirect("/register")

    return render_template("register.html", form=form)

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
