import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as msg
from pandastable import Table
from tkintertable import TableCanvas

from pandas import read_csv, Series, DataFrame, concat
import pathlib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class recommend:

    def __init__(self, root):

        self.root = root
        self.file_name = ''
        self.f = Frame(self.root,
                       height=200,
                       width=300)

        # Place the frame on root window
        self.f.pack()

        # Creating label widgets
        self.message_label = Label(self.f,
                                   text='Game Recommender',
                                   font=('Arial', 19, 'underline'),
                                   fg='Green')
        self.message_label2 = Label(self.f,
                                    text='Steam Games Version',
                                    font=('Arial', 14, 'underline'),
                                    fg='Red')

        # Buttons
        self.convert_button = Button(self.f,
                                     text='Recommend',
                                     font=('Arial', 14),
                                     bg='Orange',
                                     fg='Black',
                                     command=self.recommend_csv)
        self.display_button = Button(self.f,
                                     text='Display',
                                     font=('Arial', 14),
                                     bg='Green',
                                     fg='Black',
                                     command=self.display_xls_file)
        self.exit_button = Button(self.f,
                                  text='Exit',
                                  font=('Arial', 14),
                                  bg='Red',
                                  fg='Black',
                                  command=root.destroy)

        # Placing the widgets using grid manager
        self.message_label.grid(row=1, column=1)
        self.message_label2.grid(row=2, column=1)
        self.convert_button.grid(row=3, column=0,
                                 padx=0, pady=15)
        self.display_button.grid(row=3, column=1,
                                 padx=10, pady=15)
        self.exit_button.grid(row=3, column=2,
                              padx=10, pady=15)

    def recommend_csv(self):

        n_recommendation = 3

        # Get games data from CSV
        locationGamesFile = pathlib.Path(
            r'././data/intermediate_data/processed_games_for_content-based.csv')
        dataGames = read_csv(locationGamesFile)

        # Get users data from CSV
        # locationUsersFile = pathlib.Path(
        #     r'././data/model_data/steam_user_train.csv')   # data/purchase_play
        locationUsersFile = pathlib.Path(
            r'././data/model_data/testing.csv')
        dataUsers = read_csv(locationUsersFile)

        # get review info from csv
        locationReviewFile = pathlib.Path(
            r'././data/intermediate_data/steam_games_reviews.csv')
        dataReviews = read_csv(locationReviewFile, usecols=[
            "name", "percentage_positive_review"],)

        # Construct a reverse map of indices and game names
        indices = Series(
            dataGames.index, index=dataGames['name']).drop_duplicates()

        # get list of games we have info about
        listGames = dataGames['name'].unique()

        # create dataframe for recommendations
        col_names = list(map(str, range(1, n_recommendation + 1)))
        col_names = ["user_id"] + col_names

        # Function that takes in game name and Cosine Similarity matrix as input and outputs most similar games

        def get_recommendations(title, cosine_sim):

            if title not in listGames:
                return []

            # Get the index of the game that matches the name
            idx = indices[title]

            # if there's 2 games or more with same name (game RUSH)
            if type(idx) is Series:
                return []

            # Get the pairwise similarity scores of all games with that game
            sim_scores = list(enumerate(cosine_sim[idx]))

            # Sort the games based on the similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

            # Get the scores of the most similar games
            # (not the first one because this games as a score of 1 (perfect score) similarity with itself)
            sim_scores = sim_scores[1:n_recommendation + 1]

            # Get the games indices
            movie_indices = [i[0] for i in sim_scores]

            # Return the top most similar games
            return dataGames['name'].iloc[movie_indices].tolist()

        def make_recommendation_for_user(user_id, game_list, game_user_have):
            if type(game_list) is not list or len(game_list) == 0:
                # return empty one
                return DataFrame(data=[[user_id] + [""] * n_recommendation], columns=col_names)

            # get reviews of game recommendation, remove the games the user already has and order them by reviews
            recommendation_reviews = dataReviews.loc[dataReviews['name'].isin(
                game_list)]
            recommendation_reviews = recommendation_reviews.loc[~recommendation_reviews['name'].isin(
                game_user_have)]
            recommendation_reviews = recommendation_reviews.sort_values(
                by="percentage_positive_review", ascending=False)

            if len(recommendation_reviews.index) < n_recommendation:
                return DataFrame(data=[[user_id] + recommendation_reviews["name"].tolist() +
                                       [""] * (n_recommendation - len(recommendation_reviews.index))],
                                 columns=col_names)
            else:
                return DataFrame(data=[[user_id] + recommendation_reviews["name"].tolist()[0:n_recommendation]],
                                 columns=col_names)

        def generate_recommendation_output(column_name, location_output_file):
            recommendationByUserData = DataFrame(columns=col_names)

            # need to do some modification on data to make sure there is no NaN in column
            dataGames[column_name] = dataGames[column_name].fillna('')
            # Compute the Cosine Similarity matrix using the column
            count = CountVectorizer(stop_words='english')
            count_matrix = count.fit_transform(dataGames[column_name])
            cosine_sim_matrix = cosine_similarity(count_matrix, count_matrix)

            previousId = ""
            listSuggestion = list()
            listGamesUserHas = list()

            # loop on all row and get recommendations for user
            for j, row in dataUsers.iterrows():
                if previousId != row["user_id"]:
                    recommendationByUserData = concat([recommendationByUserData,
                                                       make_recommendation_for_user(previousId, listSuggestion, listGamesUserHas)],
                                                      ignore_index=True)
                    previousId = row["user_id"]
                    listSuggestion = list()
                    listGamesUserHas = list()
                listGamesUserHas.extend([row["game_name"]])
                listSuggestion.extend(get_recommendations(
                    row["game_name"], cosine_sim_matrix))

            # add the last element for the last user
            recommendationByUserData = concat([recommendationByUserData,
                                               make_recommendation_for_user(previousId, listSuggestion, listGamesUserHas)],
                                              ignore_index=True)

            recommendationByUserData.to_csv(location_output_file, index=False)

        generate_recommendation_output('genre',
                                       pathlib.Path(r'././data/output_data/content_based_recommender_ELMOoutput_genre.csv'))
        msg.showinfo('HELLO!', 'Recommendations Processed')

    def display_xls_file(self):
        try:
            self.file_name = pathlib.Path(
                r'././data/output_data/content_based_recommender_ELMOoutput_genre.csv')

            df = pd.read_csv(self.file_name)

            if (len(df) == 0):
                msg.showinfo('No records', 'No records')
            else:
                pass

            # Now display the DF in 'Table' object
            # under'pandastable' module
            self.f2 = Frame(self.root, height=200, width=300)
            self.f2.pack(fill=BOTH, expand=1)
            self.table = Table(self.f2, dataframe=df, read_only=True)
            self.table.show()

        except FileNotFoundError as e:
            print(e)
            msg.showerror('Error in opening file', e)


# Driver Code
root = Tk()
root.title('Game Recommendation')

obj = recommend(root)
root.geometry('800x600')
root.mainloop()
