from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

img_url = "https://image.tmdb.org/t/p/original"
url = "https://api.themoviedb.org/3/search/movie"
api = "c927f429a633a0ae99413d60f6a9ac03"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Add(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

class EditForm(FlaskForm):
    rating = StringField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your Review')
    submit = SubmitField('Done')

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String, nullable=False)




with app.app_context():
    db.create_all()
    all_movies = db.session.query(Movie).all()

@app.route("/")
def home():
    # all_movies = db.session.query(Movie).all()
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route('/add', methods=["GET","POST"])
def add():
    form = Add()
    if form.validate_on_submit():
        movie_title = form.title.data
        responce = requests.get(url, params={"api_key": api, "query": movie_title})
        data = responce.json()["results"]
        return render_template("select.html", option=data)
    return render_template("add.html", form=form)

@app.route('/select')
def selector():
    movie_id = request.args.get('id')
    if movie_id:
        new_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        responce = requests.get(new_url, params={"api_key": api, "language": 'en-US'})
        data = responce.json()
        print(data)
        new_movie = Movie(
            title=data["title"],
            year=int(data["release_date"].split("-")[0]),
            img_url=f'{img_url}{data["poster_path"]}',
            description=data["overview"],
            ranking=1,
            review=data['title'],
            rating=1
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))

@app.route('/edit', methods=["GET","POST"])
def edit():
    form = EditForm()
    id = request.args.get('id')
    movie = Movie.query.get(id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect("/")
    return render_template("edit.html", name=movie.title, form=form)

@app.route('/delete')
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
