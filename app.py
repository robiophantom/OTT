import streamlit as st
import pandas as pd
import pickle
import asyncio
import aiohttp
import time
from pathlib import Path
from dotenv import load_dotenv
import os
import platform

# Injecting custom CSS
st.markdown(
    """
    <style>
    /* Background color with gradient */
    body {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* Centering the main content */
    .main {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        flex-direction: column;
    }

    /* Style for the text */
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

# Get user-specific directory for cache
def get_cache_dir():
    system = platform.system().lower()
    if system == 'windows':
        # For windows
        cache_dir = Path(os.getenv('APPDATA')) / 'MyAppCache'
    elif system == 'darwin':
        # For macOS
        cache_dir = Path(os.path.expanduser('~')) /'Library'/'Application Support'/'MyAppCache'
    else:
        cache_dir = Path(os.path.expanduser('~')) / '.cache' / 'MyAppCache'

    # Creating a directory if it does not exist
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir

# Path to store the cache file
cache_file = get_cache_dir() / 'poster_cache.pkl'

# Initialize poster_cache
if cache_file.exists():
    # Load the cache file
    with open(cache_file, 'rb') as file:
        poster_cache = pickle.load(file)
else:
    # Cache file does not exist, initialize an empty cache
    poster_cache = {}

# Function to fetch poster using API key
async def fetch_poster_async(movie_id, session):

    if movie_id in poster_cache:
        return poster_cache[movie_id]
    
    load_dotenv()
    api_key = os.getenv('API_KEY')
    async with session.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}') as response:
        data = await response.json()
        poster_url = 'https://image.tmdb.org/t/p/w185/' + data['poster_path']
        poster_cache[movie_id] = poster_url
        return poster_url

# Save cache
def save_cache():
    with open(cache_file, 'wb') as f:
        pickle.dump(poster_cache, f)

save_cache()

# Recommend movie and fetch poster parallely
async def recommend_async(movie_name, movies_x, similarity_y):
    index = movies_x[movies_x['title'] == movie_name].index[0]
    distance = similarity_y[index]
    movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    movie_recommended = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in movie_list:
            movie_id = movies_x.iloc[i[0]].movie_id
            movie_recommended.append(movies_x.iloc[i[0]].title)
            #fetch Posters
            task = fetch_poster_async(movie_id, session)
            tasks.append(task)
        poster_urls = await asyncio.gather(*tasks)

    return movie_recommended, poster_urls

movies_list = pickle.load(open('movie_list_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))
option = st.selectbox('Enter the name of the of the movie',movies['title'].values)

if st.button('Recommend'):
    start_time = time.time()
    name, posters = asyncio.run(recommend_async(option, movies, similarity))
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

    print(f'Recommended loaded in time {time.time() - start_time:.2f} seconds')
