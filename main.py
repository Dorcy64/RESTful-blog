from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    most_posts = db.session.query(BlogPost).order_by("id").all()
    posts = []
    for post in reversed(most_posts):
        posts.append(post)
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    posts = db.session.query(BlogPost).order_by("id").all()
    for blog_post in reversed(posts):
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["POST", "GET"])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        make_post = BlogPost(
            title=request.values.get("title"),
            subtitle=request.values.get("subtitle"),
            date=datetime.now().strftime("%B %-d, %Y"),
            body=request.values.get("body"),
            author=request.values.get("author"),
            img_url=request.values.get("img_url")
        )

        db.session.add(make_post)
        db.session.commit()

        return redirect("/")

    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    object_to_edit = BlogPost.query.get(post_id)
    form = CreatePostForm(obj=object_to_edit)
    if form.validate_on_submit():
        object_to_edit.title = request.values.get("title")
        object_to_edit.subtitle = request.values.get("subtitle")
        object_to_edit.author = request.values.get("author")
        object_to_edit.img_url = request.values.get("img_url")
        object_to_edit.body = request.values.get("body")
        db.session.commit()
        return redirect("/")

    return render_template("/make-post.html", form=form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    object_to_delete = BlogPost.query.get(post_id)
    db.session.delete(object_to_delete)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
