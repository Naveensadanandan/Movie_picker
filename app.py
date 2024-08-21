from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import util


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes



@app.route('/fetch_posters', methods=['POST'])
def fetch_posters():
    title = request.form.get('title')
    urls = util.fetch_poster_urls(title)
    return jsonify(urls)

# Route to get movie titles
@app.route('/get_titles', methods=['GET'])
def get_titles():
    titles = util.load_movie_titles()
    return jsonify(titles)


@app.route('/recommend', methods=['POST'])
def get_recommendations():
    title = request.form['title']

    response = jsonify(util.recommend_movies(title))
    return response


if __name__ == "__main__":
    print("starting python flask server for movie prediction")
    util.load_artifacts()
    app.run()
