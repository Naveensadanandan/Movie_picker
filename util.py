import pickle
import pandas as pd
import requests
from flask import jsonify
import gzip

__movie_names = None
__similarity = None
__movies_dict = None


def fetch_poster_urls(title):
    load_artifacts()
    recommendations = recommend_movies(title)
    df = pd.DataFrame(__movies_dict)
    recommendations_urls = []

    try:
        movie_id = df[df["title"] == title]["id"].values[0]
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmMjE5ZmViNjFjYjRlYzg0YWYyMWY3NzEyZGE4MDQwMCIsIm5iZiI6MTcyMTk4MDUyMy4yOTY3NzQsInN1YiI6IjY1NDNkZWY1Mjg2NmZhMDBjNDIyYTY1OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.f-z1m4xf39qzTndBDpeDm5LjsdHzGeI273Ma-38Kk2c"
        }

        response = requests.get(url, headers=headers)
        movie_data = response.json()
        details = {
            "Title": movie_data.get("title"),
            "Tagline": movie_data.get("tagline"),
            "Release Date": movie_data.get("release_date"),
            "Runtime": f"{movie_data.get('runtime')} minutes",
            "Genres": ", ".join([genre["name"] for genre in movie_data.get("genres", [])]),
            "Overview": movie_data.get("overview"),
            "Vote Average": movie_data.get("vote_average"),
            "Vote Count": movie_data.get("vote_count"),
            "path" : movie_data.get("poster_path")
        }

        for movie in recommendations:
            id = df[df["title"] == movie]["id"].values[0]
            url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"
            response = requests.get(url, headers=headers)
            movie_data = response.json()
            poster_url = movie_data.get("poster_path")

            recommendations_urls.append(f"https://image.tmdb.org/t/p/w500{poster_url}")

        data = {
        "posters": recommendations_urls,
        "movie_details": details}

        return data
    except IndexError:
        return ["Movie not found."]
    except Exception as e:
        return [f"An error occurred: {str(e)}"]


def recommend_movies(movie):
    # Ensure the artifacts are loaded
    if __similarity is None or __movies_dict is None:
        load_artifacts()

    lst = []
    movies_df = pd.DataFrame(__movies_dict)

    try:
        movie_index = movies_df[movies_df['title'] == movie].index[0]
        distances = __similarity[movie_index]
        movies_list = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]
        for i in movies_list:
            lst.append(movies_df.iloc[i[0], 1])
    except IndexError:
        lst = ["Movie not found."]
    return lst


def load_movie_titles():
    with open(r'movies_dict.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
    titles = list(movies_dict['title'].values())
    return titles


def load_artifacts():
    print("loading required artifacts")
    global __movie_names
    global __similarity
    global __movies_dict

    __movie_names = load_movie_titles()

    with gzip.open(r"similarity_new.pkl.gz", 'rb') as f:
        __similarity = pickle.load(f)

    with open(r'movies_dict.pkl', 'rb') as f:
        __movies_dict = pickle.load(f)

    print("loaded saved artifacts")


if __name__ == "__main__":
    load_artifacts()
    # print(load_movie_titles())
    print(recommend_movies("Batman"))
    print(fetch_poster_urls("Batman"))


