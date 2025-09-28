from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
CKEditor(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class PostForm(FlaskForm):
    title = StringField("Add Blog Title", validators=[DataRequired()])
    subtitle = StringField("Add Blog Subtitle", validators=[DataRequired()])
    author = StringField("Blog Author", validators=[DataRequired()])
    img_url = StringField("Add Image URL", validators=[DataRequired()])
    body = CKEditorField("Add Blog Content Here", validators=[DataRequired()])
    submit = SubmitField("Done")



# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = [post for post in db.session.query(BlogPost).all()]
    return render_template("index.html", all_posts=posts)

@app.route('/<int:post_id>')
def show_post(post_id):
    requested_post = db.session.get(BlogPost, post_id)
    print(requested_post)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route("/make-post", methods=["GET", "POST"])
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
        return redirect("/")
    return render_template("make-post.html", form=form)
# TODO: edit_post() to change an existing blog post

# TODO: delete_post() to remove a blog post from the database

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
