from flask import Flask, request, render_template
from datetime import date
import json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import requests
from fetch import movie, movie_collection
# from ml import RECOMMEND

df2 = pd.read_csv('./model/tmdb.csv', encoding = 'utf-8')
df2 = df2.reset_index()

count = TfidfVectorizer(stop_words = "english")
count_matrix = count.fit_transform(df2['soup'])


all_titles = [df2['title'][i] for i in range(len(df2['title']))]

def get_recommendation(title):
    cos_sim = cosine_similarity(count_matrix, count_matrix)
    idx = indices[title]
    sim_scores = list(enumerate(cos_sim[idx]))
    sim_scores = sorted(sim_scores, key= lambda x:x[1], reverse = True)
    sim_scores = sim_scores[1:11]
    sim_indics = [i[0] for i in sim_scores]
    tit = df2['title'].iloc[sim_indics]
    dat = df2['release_date'].iloc[sim_indics]

    return_df = pd.DataFrame(columns = ['Title', 'Year']) # 빈프레임 만들기
    return_df['Title'] = tit
    return_df['Year'] = dat

    return return_df

indices = pd.Series(df2.index, index = df2['title'])

app = Flask(__name__)

@app.route('/', methods = ['GET', 'Post'])
def index():
    if request.method == "GET":
        year = date.today().year
        id_year = f'http://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&primary_release_year={year}&sort_by=popularity.desc'
        top_year = movie_collection()
        top_year.results = []
        top_year.fetch(id_year)
        genre = json.loads(requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=da396cb4a1c47c5b912fda20fd3a3336&language=en-US").text)

        top_genre_collection = []
        for genre in genre['genres']:
            # print(genre['id'])
            genre_id = f'https://api.themoviedb.org/3/discover/movie/?api_key=da396cb4a1c47c5b912fda20fd3a3336&with_genre={genre["id"]}&sort_by=popularity.desc'
            top_genre = movie_collection()
            top_genre.results = []
            top_genre.fetch(genre_id)
            top_genre_id = [top_genre.results, genre["name"]]
            top_genre_collection.append(top_genre_id)


        return render_template("home.html", top_year = top_year.results, year = year, top_genre = top_genre_collection )

    # for i in results:
    #         if i["id"] and i["title"] and i["poster_path"] and i["vote_average"] and i["release_date"] and i["overview"] and i["backdrop_path"]:
    #             results.append(movie(i["id"],i["title"],i["poster_path"],i["vote_average"],i["release_date"],i["overview"],i["backdrop_path"]))

    # return "top_year.results"

    elif request.method == 'POST':

        # print(request.form['query'])
        key_word = request.form['query']
        id_url = f"http://api.themoviedb.org/3/search/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&query={key_word}"
        movie_dic = movie_collection()
        movie_dic.results = []
        movie_dic.fetch(id_url)
        print(movie_dic.results)
        return render_template("landing.html", movie = movie_dic.results, key_word = key_word)

@app.route('/details/<id>', methods = ['GET', 'POST'])
def details(id):
    url = f"http://api.themoviedb.org/3/movie/{id}?api_key=da396cb4a1c47c5b912fda20fd3a3336"
    data = json.loads(requests.get(url).text)
    data_json = movie(data["id"],data["title"],data["poster_path"],data["vote_average"],data["release_date"],data["overview"])
    # print(data_json)
    return render_template("details.html", movie = data_json)

@app.route('/recommend', methods = ['GET', 'POST'])
def recommend():
    if request.method == 'GET':
        return render_template('recommend.html')
    elif request.method == 'POST':
        
        print(len(all_titles))
        m_name = request.form['movie_name']
        # print(m_name.title())
        m_name = m_name.title()

        if m_name not in all_titles:
            return render_template('negative.html', name = m_name)
        else:
        
            result_final = recommend.get_recommendation(m_name)
            print(result_final)
            data = []
            for i in range(len(result_final)):
                data.append((result_final.iloc[i][0], result_final.iloc))

            return render_template('positive.html', movie_data = data, search_name = m_name)
    


if __name__ == "__main__":
    app.run(port = 5000, debug = True) ## localhost:5000 / 오류메시지 웹창에 보이게 하는거 