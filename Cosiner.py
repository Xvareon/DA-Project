import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pd.set_option('display.max_columns', None)

# csv file name to be cosined
in_csv = './data/intermediate_data/steam_games5000.csv'

# Read the csv
dataGames = pd.read_csv(in_csv)

# Lower all the string names
dataGames['name'] = dataGames['name'].str.lower()

# Cosine computation
dataGames['genre'] = dataGames['genre'].fillna('')
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(dataGames['genre'])
cosine_sim_matrix = cosine_similarity(
    count_matrix, count_matrix)

# Save the output
np.savetxt("./OUTPUT/cosined_data.csv", cosine_sim_matrix, delimiter=",")
# cosine_sim_matrix.to_csv(
#       out_csv,
#       index=False,
# )#size of data to append for each loop
