from re import T
from turtle import ycor
from matplotlib.pyplot import text
from matplotlib.style import use
import pandas as pd
import numpy as np
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as msg
from pandastable import Table
from tkintertable import TableCanvas

from pandas import read_csv, Series, DataFrame, concat
import pathlib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import xlsxwriter
from openpyxl import *
import tkinter as tk
import time
import csv


userGames = [0, 0, 0, 0, 0]
numOfGames = 1
userInput1 = []
userInput = []
recommendedGames = []
gamesLbl = []
listGames = []
listDesc = []
cosined_data = np.empty((0))


class recommend:

    def __init__(self, root):

        self.root = root
        self.file_name = ''
        self.f = Frame(self.root.configure(background='#f1c95e'),
                       height=1500,
                       width=1500,
                       bg="#f1c95e")

        # Place the frame on root window
        self.f.pack()

        # Creating label widgets
        self.message_label = Label(self.f,
                                   text='\n\nGame Recommender',
                                   font=('Fixedsys', 22),
                                   fg='#051544', bg="#f1c95e")
        self.message_label2 = Label(self.f,
                                    text='Steam Games Version',
                                    font=('Fixedsys', 16),
                                    fg='#2a5e60', bg="#f1c95e")

        # Buttons
        self.input_button = Button(self.f,
                                   text='Input',
                                   font=('MS Sans Serif', 12),
                                   bg='#eaae50',
                                   fg='Black',
                                   command=self.user_input)
        self.display_button = Button(self.f,
                                     text='Display',
                                     font=('MS Sans Serif', 12),
                                     bg='#529490',
                                     fg='Black',
                                     command=self.display_xls_file)
        self.exit_button = Button(self.f,
                                  text='Exit',
                                  font=('MS Sans Serif', 12),
                                  bg='#b0d7d1',
                                  fg='Black',
                                  command=root.destroy)

        # Placing the widgets using grid manager
        self.message_label.grid(row=1, column=1)
        self.message_label2.grid(row=2, column=1)
        self.input_button.grid(row=3, column=0,
                               padx=0, pady=15)
        # self.convert_button.grid(row=3, column=1,
        #                          padx=0, pady=15)
        self.display_button.grid(row=3, column=1,
                                 padx=10, pady=15)
        self.exit_button.grid(row=3, column=3,
                              padx=10, pady=15)

        # Load cosined data of games
        global cosined_data
        locationGamesFile = pathlib.Path(
            r'././OUTPUT/cosined_data.csv')
        cosined_data = np.genfromtxt(
            locationGamesFile, delimiter=",")  # CSV to NP ARRAY
    #######################################################################################

    def user_input(self):
        self.input_button["state"] = "disabled"
        global userInput1
        global userInput
        global numOfGames
        global listGames
        numOfGames = 1
        userInput = []
        userInput1 = []

        # Load steam games
        locationGamesFile = pathlib.Path(
            r'././data/intermediate_data/steam_games5000.csv')
        dataGames = read_csv(locationGamesFile)
        dataGames['name'] = dataGames['name'].str.lower()
        listGames = dataGames['name'].unique()

        def recommend_csv():
            n_recommendation = 10

            # get review info from csv
            locationReviewFile = pathlib.Path(
                r'././data/intermediate_data/steam_games_reviews.csv')
            dataReviews = read_csv(locationReviewFile, usecols=[
                "name", "percentage_positive_review"],)

            # Construct a reverse map of indices and game names

            dataReviews['name'] = dataReviews['name'].str.lower()
            indices = Series(
                dataGames.index, index=dataGames['name']).drop_duplicates()
            # get list of games we have info about

            # create dataframe for recommendations
            col_names = list(map(str, range(1, n_recommendation + 1)))
            col_names = ["user_id"] + col_names

            #######################################################################################
            # Function that takes in game name and Cosine Similarity matrix as input and outputs most similar games
            def get_recommendations(title):
                global cosined_data

                if title not in listGames:
                    return []  # for blank

                # Get the index of the game that matches the name
                idx = indices[title]

                # if there's 2 games or more with same name (game RUSH)
                if type(idx) is Series:
                    return []  # for duplicate

                # Get the pairwise similarity scores of all games with that game
                sim_scores = list(enumerate(cosined_data[idx]))

                # Sort the games based on the similarity scores
                sim_scores = sorted(
                    sim_scores, key=lambda x: x[1], reverse=True)

                # Get the scores of the most similar games
                # (not the first one because this games as a score of 1 (perfect score) similarity with itself)
                x = int(n_recommendation/len(userGames))

                sim_scores = sim_scores[1:x + 1]

                # VECTOR DATA OF N RECOMMENDATIONS

                df = pd.DataFrame(data={"vectors": sim_scores})
                df.to_csv("./closest_vectors.csv",
                          sep=',', index=False)

                # Get the games indices
                movie_indices = [i[0] for i in sim_scores]

                # print(dataGames['developer'].iloc[movie_indices])

                return dataGames['name'].iloc[movie_indices].tolist()
            #######################################################################################

            def make_recommendation_for_user(user_id, game_list, game_user_have):
                global listDesc
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

                # Return the top most similar games
                dataGames['developer'] = (
                    dataGames['developer'] + " " + dataGames['original_price'].astype(str))

                global recommendedGames
                recommendedGames = []
                idx = []
                i = 0
                for games in recommendation_reviews["name"]:
                    recommendedGames.insert(i, games)
                    idx.append(indices[games])
                    i = i+1
                listDesc = dataGames['developer'].iloc[idx].tolist()

                if len(recommendation_reviews.index) < n_recommendation:
                    return DataFrame(data=[[user_id] + recommendation_reviews["name"].tolist() +
                                           [""] * (n_recommendation - len(recommendation_reviews.index))],
                                     columns=col_names)
                else:
                    return DataFrame(data=[[user_id] + recommendation_reviews["name"].tolist()[0:n_recommendation]],
                                     columns=col_names)
            #######################################################################################

            def generate_recommendation_output():
                recommendationByUserData = DataFrame(columns=col_names)

                previousId = ""
                listSuggestion = list()
                listGamesUserHas = list()

                # loop on all row and get recommendations for user
                for game in userGames:
                    listSuggestion.extend(get_recommendations(game))

                # add the last element for the last user
                recommendationByUserData = concat([recommendationByUserData,
                                                   make_recommendation_for_user(previousId, listSuggestion, userGames)],
                                                  ignore_index=True)

            generate_recommendation_output()

            msg.showinfo('HELLO!', 'Recommendations Processed')

            self.input_button["state"] = "normal"
            window.destroy()
        #######################################################################################

        #  New window for input
        window = Tk()
        window.title('Game Recommendation Window')
        window.geometry("1000x500")
        window.configure(bg='#FFF89A')

        userGames.clear()

        def close_window():
            self.input_button["state"] = "normal"
            window.destroy()

        errorMessage = []

        def new_entry():
            global userInput1
            global userInput
            global listGames
            global userGames
            userGames = []
            i = 0
            j = 0

            for i in range(len(errorMessage)):
                errorMessage[i].destroy()
            errorMessage.clear()

            for games in userInput:
                game = games.get().lower()
                # Check if it is in our csv
                if game not in listGames:
                    lbl_1 = tk.Label(window, text="*Invalid",
                                     fg='black', font=('Fixedsys', 16), bg='#FFF89A')
                    lbl_1.place(x=400, y=80 + (j*1.5) * 25)
                    errorMessage.append(lbl_1)

                # Check for duplicates
                elif game in userGames:
                    lbl_1 = tk.Label(window, text="*Duplicate game input",
                                     fg='black', font=('Fixedsys', 16), bg='#FFF89A')
                    lbl_1.place(x=400, y=80 + (j*1.5) * 25)
                    errorMessage.append(lbl_1)

                # Inserts the valid game
                else:
                    userGames.insert(i, game)
                    i = i+1
                j = j+1

            if (i == j):
                btn_recommend["state"] = "normal"

        # TITLE
        lbl_0 = tk.Label(window, text="Game Recommendation Entry \n(Space Sensitive)",
                         fg='black', font=('Fixedsys', 16), bg='#FFF89A')
        lbl_0.place(x=100, y=10)

        # SAVE BUTTON
        btn = tk.Button(window, text="Save Entry",
                        font=('System', 10),
                        fg='black', command=new_entry, bg='#9DDFD3', width=10)
        btn.place(x=600, y=10)

        # RECOMMEND BUTTON
        btn_recommend = tk.Button(window, text="Recommend",
                                  font=('System', 10),
                                  fg='black', command=recommend_csv, bg='#DBF6E9', width=10)
        btn_recommend.place(x=725, y=10)
        btn_recommend["state"] = "disabled"
        # EXIT BUTTON
        btn_exit = tk.Button(window, text="Exit",
                             font=('System', 10),
                             fg='black', command=close_window, bg='#FFC93C', width=10)
        btn_exit.place(x=850, y=10)

        # OPTION MENU

        def display_selected(choice):
            global numOfGames
            global userInput1
            global userInput
            global userGames
            numOfGames = variable.get()
            btn_recommend["state"] = "disabled"
            # Delete labels and text fields in the window
            for i in range(len(userInput)):
                userInput[i].destroy()
                userInput1[i].destroy()

            for i in range(len(errorMessage)):
                errorMessage[i].destroy()
            # Reinitialized the list
            userInput = []
            userInput1 = []
            userGames = []
            for i in range(numOfGames):
                # LABELS
                lbl_1 = tk.Label(window, text="Game Name",
                                 fg='black', font=('Fixedsys', 16), bg='#FFF89A')
                lbl_1.place(x=100, y=80 + (i*1.5) * 25)
                userInput1.append(lbl_1)
                # TEXT FIELDS
                txtfld_1 = tk.Entry(window, bg='white', fg='black', bd=5)
                txtfld_1.place(x=250, y=78 + (i*1.5) * 25)

                userInput.append(txtfld_1)

        # For first run, initialize 1 label and textfield
        lbl_1 = tk.Label(window, text="Game Name",
                         fg='black', font=('Fixedsys', 16), bg='#FFF89A')
        lbl_1.place(x=100, y=80)
        userInput1.append(lbl_1)
        txtfld_1 = tk.Entry(window, bg='white', fg='black', bd=5)
        txtfld_1.place(x=250, y=78)

        userInput.append(txtfld_1)

        # Option Menu
        options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        variable = IntVar(window)
        variable.set(options[numOfGames-1])  # default value
        w = OptionMenu(window, variable, *options, command=display_selected)
        w.config(width=10, bg='#95D1CC', font=('MS Sans Serif', 12))
        w.pack()
        w.place(x=400, y=10)

        def on_closing():
            self.input_button["state"] = "normal"
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()
        #######################################################################################

    def display_xls_file(self):
        global numOfGames
        global gamesLbl

        # Deleting the game labels
        for i in range(len(gamesLbl)):
            gamesLbl[i].destroy()

        # Reinitialized the list
        gamesLbl = []

        # For printin the recommenedGames
        lbl_1 = tk.Label(root, text="Games Recommended:",
                         fg='black', font=('Fixedsys', 16), bg='#FFF89A')
        lbl_1.place(x=200, y=175)
        print(recommendedGames)
        for i in range(len(recommendedGames)):
            # LABELS
            lbl_1 = tk.Label(root, text="{}.) {} - {}".format(i+1, recommendedGames[i].upper(), listDesc[i]),
                             fg='black', font=('Fixedsys', 16), bg='#FFF89A')
            lbl_1.place(x=200, y=225 + (i*1.5) * 25)
            gamesLbl.append(lbl_1)


#######################################################################################
# Driver Code
root = Tk()
root.title('Game Recommendation')

obj = recommend(root)
root.geometry('1800x1600')
root.mainloop()
