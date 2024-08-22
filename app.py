import streamlit as st

if not hasattr(st, 'already_started_server'):
    # Hack the fact that Python modules (like st) only load once to
    # keep track of whether this file already ran.
    st.already_started_server = True

    st.write('''
        The first time this script executes it will run forever because it's
        running a Flask server.

        Just refresh the page.
    ''')

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

    app.run(port=8888)


# We'll never reach this part of the code the first time this file executes!

# Your normal Streamlit app goes here:
import streamlit as st
import requests

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://mir-s3-cdn-cf.behance.net/project_modules/1400/3734378226309.5cd1a5d2e5711.jpg");
        background-size: cover;
        width: 100%;
        height: 100vh;
        animation: fadeIn 1s ease-in-out;
        background-color: gray;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .header {
        background: linear-gradient(135deg, #FF5733, #FFC300); /* Gradient colors */
        padding: 20px; /* Padding inside the box */
        border-radius: 10px; /* Rounded corners */
        color: white; /* Text color */
        text-align: center; /* Center align text */
        font-size: 2.5em; /* Larger font size */
        font-weight: bold; /* Make text bold */
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); /* Shadow effect */
    }
    .gradient-box {
        background: linear-gradient(135deg, #FF5733, #FFC300); /* Gradient colors */
        padding: 20px; /* Padding inside the box */
        border-radius: 10px; /* Rounded corners */
        color: white; /* Text color */
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); /* Shadow effect */
    }
    </style>
    <div class="header">
        Popcorn Picks
    </div>
    """,
    unsafe_allow_html=True
)

st.write("""

## Discover Your Next Favorite Flick!


""")

# URLs of the Flask APIs
titles_url = 'http://127.0.0.1:5000/get_titles'
recommendation_url = 'http://127.0.0.1:5000/recommend'
posters_url = 'http://127.0.0.1:5000/fetch_posters'

# Fetch data for the dropdown from the API
try:
    response = requests.get(titles_url)
    if response.status_code == 200:
        options = response.json()
    else:
        st.error('Failed to retrieve data from API.')
        options = []
except Exception as e:
    st.error(f'Error: {e}')
    options = []

# Add some spacing before the dropdown
st.markdown("<br><br>", unsafe_allow_html=True)

# Create a dropdown list in Streamlit
selected_movie = st.selectbox('Choose a movie:', options)

if st.button('Recommend'):
    # Fetch the recommended movie titles based on the selected movie
    response_titles = requests.post(recommendation_url, data={'title': selected_movie})
    if response_titles.status_code == 200:
        titles = response_titles.json()  # Expecting a list of movie titles
    else:
        titles = []
        st.error('Failed to retrieve recommendations.')

    # Fetch the poster URLs and movie details
    response = requests.post(posters_url, data={'title': selected_movie})
    if response.status_code == 200:
        data = response.json()
        posters = data.get('posters', [])  # List of poster URLs
        movie_details = data.get('movie_details', {})  # Dictionary of movie details
    else:
        posters = []
        movie_details = {}
        st.error('Failed to retrieve posters and movie details.')

    # Create a dictionary combining the movie titles and their poster URLs
    movies_dict = dict(zip(titles, posters))

    st.write("## Details of Selected Movie")

    # Define a gradient box using CSS
    st.markdown(
        f"""
        <style>
        .gradient-box {{
            background: linear-gradient(to right, #ff7e5f, #feb47b); /* Gradient colors */
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
            color: white;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }}
        .gradient-box img {{
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .gradient-box .details {{
            display: flex;
            justify-content: space-between;
            width: 100%;
        }}
        .gradient-box .details div {{
            flex: 1;
            margin: 0 10px;
        }}
        </style>
        <div class="gradient-box">
            <img src="https://image.tmdb.org/t/p/w500{movie_details.get('path', 'N/A')}" width="300" />
            <div class="details">
                <div>
                    <p><strong>Tagline:</strong> <span style="font-weight: bold; color: yellow;">{movie_details.get('Tagline', 'N/A')}</p>
                    <p><strong>Release Date:</strong> <span style="font-weight: bold; color: yellow;">{movie_details.get('Release Date', 'N/A')}</p>
                    <p><strong>Runtime:</strong> <span style="font-weight: bold; color: yellow;">{movie_details.get('Runtime', 'N/A')}</p>
                    <p><strong>Genres:</strong> <span style="font-weight: bold; color: yellow;">{movie_details.get('Genres', 'N/A')}</p>
                </div>
                <div>
                    <p><strong>Overview:</strong> <span style="font-weight: bold; color: yellow;">{movie_details.get('Overview', 'N/A')}</p>
                    <p><strong>Vote Average:</strong> <span style="font-weight: bold; color: yellow;">{movie_details.get('Vote Average', 'N/A')}</p>
                    <p><strong>Vote Count:</strong> <span style="font-weight: bold; color: yellow;">{movie_details.get('Vote Count', 'N/A')}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("## You May Like")



    # Display the recommended movies with their posters horizontally
    cols = st.columns(len(movies_dict))  # Create a column for each movie

    for idx, (title, poster_url) in enumerate(movies_dict.items()):
        with cols[idx]:
            st.write(f"**{title}**")  # Display the movie title in bold
            if poster_url:
                st.image(poster_url, width=150)  # Display the movie poster with a smaller width
            else:
                st.write("Poster not available.")
