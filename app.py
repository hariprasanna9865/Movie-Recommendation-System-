import flask
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random


app = flask.Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
            
    if flask.request.method == 'POST':
        language=flask.request.form['movie_language']
        if language=="Tamil":
           df2 = pd.read_csv('./model/Tamil_movies_dataset.csv')
           all_titles = [df2['MovieName'][i] for i in range(len(df2['MovieName']))]
           attribute='MovieName'
           m_name = " ".join(flask.request.form['movie_name'].title().split())
           user_movie=m_name
           df2['soup'] = df2[['MovieName', 'Genre', 'Rating', 'Director', 'Actor', 'PeopleVote', 'Year', 'Hero_Rating', 'movie_rating', 'content_rating']].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
        if language=="English":
            df2 = pd.read_csv('./model/tmdb.csv')
            all_titles = [df2['title'][i] for i in range(len(df2['title']))]
            attribute='title'
            m_name = " ".join(flask.request.form['movie_name'].title().split())
            user_movie=m_name
        tfidf = TfidfVectorizer(stop_words='english',analyzer='word')

        #Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(df2['soup'])
        print(tfidf_matrix.shape)

        #construct cosine similarity matrix
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        print(cosine_sim.shape)

        df2 = df2.reset_index()
        indices = pd.Series(df2.index, index=df2[attribute]).drop_duplicates()
        # create array with all movie titles
        all_titles = [df2[attribute][i] for i in range(len(df2[attribute]))]
        
        
        def get_tamil_recommendations(title,attribute):
            # Get the index of the movie that matches the title
            idx = indices[title]
            # Get the pairwise similarity scores of all movies with that movie
            sim_scores = list(enumerate(cosine_sim[idx]))
            # Sort the movies based on the similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            # Get the scores of the 10 most similar movies
            sim_scores = sim_scores[1:11]
            # print similarity scores
            print("\n movieId      score")
            for i in sim_scores:
                print(i)

            # Get the movie indices
            movie_indices = [i[0] for i in sim_scores]

            # return list of similar movies
            return_df = pd.DataFrame(columns=['Title','Homepage'])
            return_df['Title'] = df2[attribute].iloc[movie_indices]
            return_df['Homepage'] = df2['MovieName'].iloc[movie_indices]
            return_df['ReleaseDate'] = df2['Year'].iloc[movie_indices]
            return return_df
        def get_english_recommendations(title,attribute):
            # Get the index of the movie that matches the title
            idx = indices[title]
            # Get the pairwise similarity scores of all movies with that movie
            sim_scores = list(enumerate(cosine_sim[idx]))
            # Sort the movies based on the similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            # Get the scores of the 10 most similar movies
            sim_scores = sim_scores[1:11]
            # print similarity scores
            print("\n movieId      score")
            for i in sim_scores:
                print(i)

            # Get the movie indices
            movie_indices = [i[0] for i in sim_scores]

            # return list of similar movies
            return_df = pd.DataFrame(columns=['Title','Homepage'])
            return_df['Title'] = df2[attribute].iloc[movie_indices]
            return_df['Homepage'] = df2['homepage'].iloc[movie_indices]
            return_df['ReleaseDate'] = df2['release_date'].iloc[movie_indices]
            return return_df
        if m_name not in all_titles:
            length=len(df2[attribute])
            random_number=random.randint(0,length)
            m_name=df2[attribute][random_number]
            if language=='Tamil':
                result_final = get_tamil_recommendations(m_name,attribute)
            if language=='English':
                result_final = get_english_recommendations(m_name,attribute)
            names = []
            homepage = []
            releaseDate = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                releaseDate.append(result_final.iloc[i][2])
                if len(str(result_final.iloc[i][1])) > 3:
                    homepage.append(result_final.iloc[i][1])
                else:
                    homepage.append("#")

            return flask.render_template('random_movie.html', movie_names=names, movie_homepage=homepage, search_name=user_movie, movie_releaseDate=releaseDate)
        else:
            
            if language=='Tamil':
                result_final = get_tamil_recommendations(m_name,attribute)
            else:
                result_final = get_english_recommendations(m_name,attribute)
            names = []
            homepage = []
            releaseDate = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                releaseDate.append(result_final.iloc[i][2])
                if(len(str(result_final.iloc[i][1]))>3):
                    homepage.append(result_final.iloc[i][1])
                else:
                    homepage.append("#")
                

            return flask.render_template('found.html',movie_names=names,movie_homepage=homepage,search_name=m_name, movie_releaseDate=releaseDate)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
    #app.run()
