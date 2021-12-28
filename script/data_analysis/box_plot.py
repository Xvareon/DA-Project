import pathlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Load Matplotlib default settings.
mpl.rcParams.update(mpl.rcParamsDefault)


def box_plot(csv_file, plot_file, nb_games=20):
    """
    Function to create a box-plot based on input data (steam user data).
    It is assumed data is provided in the following column order:
      [user_id] [game_name] [hours] [purchase] [play]
    """

    # Load user data.
    csv_location = pathlib.Path(csv_file)
    df_data_users = pd.read_csv(csv_location)

    # Get column names from csv.
    col_names = df_data_users.columns
    col_user = col_names[0]
    col_game = col_names[1]
    col_hour = col_names[2]
    col_play = col_names[4]

    # Compute the total number of hours and total number of users per game.
    # Only users with 'play' set to 1 are considered.
    user_count = df_data_users.loc[df_data_users[col_play] == 1]. \
        groupby(col_game)[col_user].agg('count').sort_values(ascending=False)
    hours_played = df_data_users.loc[df_data_users[col_play] == 1]. \
        groupby(col_game)[col_hour].agg(np.sum).sort_values(ascending=False)

    # Create dataframe of top most played games with total hours and total
    # users per game.
    df_top_hours_played = pd.DataFrame({'game_name': hours_played.index,
                                        'hours_played': hours_played.values,
                                        'user_count': user_count.values})[0:nb_games]

    # Mask criteria for box plot.
    mask_criteria = df_data_users[col_game].isin(df_top_hours_played['game_name'])
    df_box_plot = df_data_users.loc[mask_criteria]. \
        loc[df_data_users[col_play] == 1][[col_hour, col_game]]

    # Create box-plot.
    fig_h = 1 + 0.25 * max(1, nb_games)
    fig, ax = plt.subplots(figsize=(12, fig_h))
    sns.set_style("whitegrid")
    ax = sns.boxplot(x=col_hour, y=col_game, data=df_box_plot,
                     order=df_top_hours_played['game_name'].to_list(),
                     palette="colorblind",
                     saturation=1,
                     linewidth=1,
                     fliersize=2)
    plt.title('Box Plot: Top most {} played games [hrs]'.format(nb_games),
              fontsize=15, fontweight='heavy')
    plt.xlabel('Hours', fontsize=13, fontweight='demi')
    plt.ylabel('Game', fontsize=13, fontweight='demi')
    plt.show()

    # Save plots as png.
    plot_location = pathlib.Path(plot_file)
    fig.savefig(plot_location, dpi=800, quality=100)

    # Compute statistics summary of top played games as dataframe.
    df_stats = df_box_plot.groupby(col_game).describe(). \
        reindex(df_top_hours_played['game_name'].to_list())

    return df_stats


if __name__ == "__main__":
    csv_data = r'../../data/raw_data/steam_users_purchase_play.csv'
    plot_png = r'../../plots/boxplot_top_20_games.png'
    stats = box_plot(csv_data, plot_png, 20)
