import streamlit as st
import pandas as pd
import pickle
import requests
from dotenv import load_dotenv
import os

# Injecting custom CSS.
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .main {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        flex-direction: column;
    }
    h1 {
        font-family: 'Arial Black', sans-serif;
        color: #E50914;
        text-shadow: 2px 2px 5px black;
        font-size: 50px;
    }
    p {
        font-family: 'Courier New', monospace;
        color: lightgray;
        font-size: 20px;
        text-shadow: 1px 1px 3px black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main content
st.markdown('<h1>Welcome to OTT World</h1>', unsafe_allow_html=True)
st.markdown('<p>Beautiful and Thrilling Streaming Awaits...</p>', unsafe_allow_html=True)

# Function to fetch poster using API key
def fetch_poster(movie_title):
    load_dotenv()
    api_key = os.getenv('API_KEY')  # Replace with your API key
    url = "http://www.omdbapi.com/"

    params = {
        "apikey": api_key,
        "t": movie_title,  # Movie title
    }
    # Make the API request
    response = requests.get(url, params=params)
    response = requests.get(url)
    data = response.json()
    return data.get('Poster')

# Function to recommend movies
def recommend(movie_name, movies_x, similarity_y):
    index = movies_x[movies_x['title'] == movie_name].index[0]
    distance = similarity_y[index]
    movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    movie_recommended = []
    poster_urls = []

    for i in movie_list:
        movie_recommended.append(movies_x.iloc[i[0]].title)
        poster_urls.append(fetch_poster(movies_x.iloc[i[0]].title))

    return movie_recommended, poster_urls

# Load data
movies_list = pickle.load(open('movie_list_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# User input
option = st.selectbox('Enter the name of the movie', movies['title'].values)

if st.button('Recommend'):
    name, posters = recommend(option, movies, similarity)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(name[0])
        st.image(posters[0])
    with col2:
        st.text(name[1])
        st.image(posters[1])
    with col3:
        st.text(name[2])
        st.image(posters[2])
    with col4:
        st.text(name[3])
        st.image(posters[3])
    with col5:
        st.text(name[4])
        st.image(posters[4])
