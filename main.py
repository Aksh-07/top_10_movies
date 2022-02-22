from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

movie_api_key = "ab937b4f36501b4ffc31316e0298d451"
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


# db.create_all()


class EditMovie(FlaskForm):
    rating = StringField("Your rating out of 10. eg: 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AddMovie(FlaskForm):
    name = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/", methods=["get", "post"])
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):

        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route('/edit', methods=["get", "post"])
def edit():
    form = EditMovie()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():

        movie.rating = float(form.rating.data)
        movie.review = form.review.data

        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html", form=form)


@app.route("/delete", methods=["get", "post"])
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add", methods=["get", "post"])
def add_movie():
    form = AddMovie()
    if form.validate_on_submit():

        movie_name = form.name.data
        params = {
            "api_key": movie_api_key,
            "query": movie_name
        }

        movie_url = f"https://api.themoviedb.org/3/search/movie"
        response = requests.get(url=movie_url, params=params)
        movie_list = response.json()["results"]
        return render_template("select.html", movies=movie_list)

    return render_template("add.html", form=form)

@app.route("/add selected movie")
def add_selected():
    selected_movie_id = request.args.get("id")
    if selected_movie_id:
        url = f"https://api.themoviedb.org/3/movie/{selected_movie_id}"
        params = {
            "api_key": movie_api_key
        }
        response = requests.get(url=url, params=params)
        movie_data = response.json()
        new_movie = Movie(
            title=movie_data["title"],
            img_url=f'https://image.tmdb.org/t/p/w500{movie_data["poster_path"]}',
            year=movie_data["release_date"],
            description=movie_data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
