import pandas as pd
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import pickle
import requests
import re
import itertools


new_movie = []
poster = []


app = Flask(__name__)


app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)



from jedi.plugins import flask
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)



def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


def get_poster(movie_name):
    index = movies[movies['title'] == movie_name].index[0]
    id = movies.iloc[index].movie_id
    return fetch_poster(id)


def popular():
    popular_movies = ["Titanic", "Spectre", "Iron Man", "Avatar", "Batman", "Superman", "Skyfall", "The Notebook"]
    for i in range(8):
        new_movie.append(popular_movies[i])
        poster.append(get_poster(popular_movies[i]))
    return new_movie, poster


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:9]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names,recommended_movie_posters



@app.route('/',  methods=['GET', 'POST'])
def home():
    movie_name = "Spectre"
    new_movie, poster = popular()
    q = request.args.get("q")
    if q:
        for movie in movies:
            if(re.match(q,movie.title)):
                search_movies.append(movie)
    else :
        search_movies = []
    return render_template('index.html', new_movie=new_movie, poster=poster, search_movies=search_movies)



@app.route('/movie',  methods=['GET', 'POST'])
def movie():
    if request.method == 'POST':
        movie_name = request.form.get("movieName")
        if  not movie_name:
            return render_template('error.html')
        new_movie, poster = recommend(movie_name)
        return render_template('movie.html', movie_name=movie_name, new_movie=new_movie, poster=poster)
    else:
        return render_template('index.html')



@app.route('/watchlist',  methods=['GET', 'POST'])
def watchlist():
    posters = []
    if "watchlist" not in session:
        session["watchlist"] = []
    if request.method == "POST" :
        id = request.form.get("id")
        if id:
            session["watchlist"].append(id)
        return redirect('/watchlist')

    movies = session["watchlist"]
    for movie in movies:
        posters.append(get_poster(movie))
    return render_template('watchlist.html', movies_posters=zip(movies,posters))



if __name__ == "__main__":
    app.run(debug=True)
