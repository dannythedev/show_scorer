from io import BytesIO
import math
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap, Normalize
from Functions import read_json, write_json, truncate_string, wrap_text
from IMDB import IMDB

def _dark_mode():
    # Dark metallic blue color
    background_color = '#242633'  # Adjust the color code as needed

    # Set the background color
    plt.style.use('dark_background')
    plt.rcParams['axes.facecolor'] = background_color
    plt.rcParams['figure.facecolor'] = background_color
    plt.rcParams['text.color'] = 'white'

def ratings():
    max_rating = max([x['Rating'] for x in extracted_data])
    min_rating = min([x['Rating'] for x in extracted_data])
    try:
        max_episodes = [[x['Title'], x['Description']] for x in extracted_data if x['Rating'] == max_rating][0]
        min_episodes = [[x['Title'], x['Description']] for x in extracted_data if x['Rating'] == min_rating][0]

        max_episodes[0] = 'Highest rated episode: ' + truncate_string(max_episodes[0].replace('∙ ', '\n'))
        min_episodes[0] = 'Lowest rated episode: ' + truncate_string(min_episodes[0].replace('∙ ', '\n'))

        plt.text(-0.45 + OFFSET_X, 0.1 + OFFSET_Y, str(max_episodes[0]), fontsize=9, color='white', transform=ax.transAxes)
        plt.text(-0.45 + OFFSET_X, 0.02 + OFFSET_Y, str(min_episodes[0]), fontsize=9, color='white', transform=ax.transAxes)

    except IndexError:
        pass
    # Create mini heatmaps for max and min ratings
    ax_max = plt.axes([0.025 + OFFSET_X*OFFSET_MULT, 0.18 + OFFSET_Y*OFFSET_MULT, 0.05, 0.05], frameon=False)
    ax_min = plt.axes([0.025 + OFFSET_X*OFFSET_MULT, 0.12 + OFFSET_Y*OFFSET_MULT, 0.05, 0.05], frameon=False)
    sns.heatmap([[max_rating]], annot=True, norm=norm, cmap=cmap, cbar=False, ax=ax_max)
    sns.heatmap([[min_rating]], annot=True, norm=norm, cmap=cmap, cbar=False, ax=ax_min)
    ax_max.set_yticklabels([])
    ax_max.set_xticklabels([])
    ax_min.set_yticklabels([])
    ax_min.set_xticklabels([])


def average():
    average_rating = [x['Rating'] for x in extracted_data if not math.isnan(x['Rating'])]
    if average_rating:
        average_rating = sum(average_rating) / len(average_rating)
        plt.text(-0.45, -0.125 + OFFSET_Y, 'Average rating', fontsize=9, color='white', transform=ax.transAxes)
        # Create mini heatmaps for max and min ratings
        ax_avg = plt.axes([0.025 + OFFSET_X * OFFSET_MULT, 0.00 + OFFSET_Y * OFFSET_MULT, 0.05, 0.05], frameon=False)
        sns.heatmap([[average_rating]], annot=True, norm=norm, cmap=cmap, cbar=False, ax=ax_avg)
        ax_avg.set_xticklabels([])
        ax_avg.set_yticklabels([])

def most_rated_season():
    season_averages = {season: sum(ratings) / len(ratings) for season, ratings in data.items() if ratings}
    season_averages = {key: val for key, val in season_averages.items() if not math.isnan(val)}
    if season_averages:
        most_rated_season = max(season_averages, key=season_averages.get)
        plt.text(-0.45 + OFFSET_X, -0.06 + OFFSET_Y, 'Most rated season:\nSeason {}'.format(most_rated_season), fontsize=9, color='white', transform=ax.transAxes)
        ax_season = plt.axes([0.025 + OFFSET_X*OFFSET_MULT, 0.06 + OFFSET_Y*OFFSET_MULT, 0.05, 0.05], frameon=False)
        sns.heatmap([[season_averages[most_rated_season]]], annot=True, norm=norm, cmap=cmap, cbar=False, ax=ax_season)
        ax_season.set_xticklabels(["10"])
        ax_season.set_yticklabels([])


def show_image(image):
    if image:
        try:
            response = requests.get(image)
            image = Image.open(BytesIO(response.content))
            image_ax = ax.inset_axes([-0.6 + OFFSET_X, 0.2 + OFFSET_Y, 0.6, 0.6], transform=ax.transAxes)
            image_ax.imshow(image)
            image_ax.axis('off')  # Turn off axis
        except:
            print('Caution: No image was found.')

def generate_lineplot():
    episode_count = 0
    palette = sns.color_palette("hsv", len(df.columns))  # Color palette for seasons

    ax = plt.axes([0.87, 0.11, 0.1, 0.77])  # Position and size of the line graph

    for idx, (season, ratings) in enumerate(df.items()):
        num_episodes = len(ratings.dropna())
        episode_numbers = range(episode_count + 1, episode_count + num_episodes + 1)
        sns.lineplot(x=episode_numbers, y=ratings.dropna(), ax=ax, color=palette[idx], label=season, marker='o')
        episode_count += num_episodes

    ax.set_ylim(0, 10)
    ax.set_xlabel('Rating/Time', fontsize=7, color='white')
    ax.set_ylabel('', fontsize=7, color='white')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.legend(title='Seasons', prop={'size': 6})

def adjust_font_size(episodes):
    if episodes >= 45: return 5.5
    if episodes >= 35: return 6
    if episodes >= 25: return 9
    if episodes >= 15: return 12
    return 14

def generate_heatmap():
    # Define the custom colormap
    cmap = LinearSegmentedColormap.from_list(
        name='rating_cmap',
        colors=['#3D3D3D', '#DB0022', '#F12A20', '#F58220', '#FFC20E', '#B2D34A', '#46BB4D']
        # dark red, grey, nature green
    )
    norm = Normalize(vmin=0, vmax=10)
    # Creating the heatmap
    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(df, annot=True, norm=norm, cmap=cmap, linewidths=.5)
    # Adjust the y-axis to better align with the rows
    ax.set_yticks([x + 0.5 for x in range(df.shape[0])])
    episodes = df.shape[0] + 1
    ax.set_yticklabels(range(1, episodes), fontsize=adjust_font_size(episodes))
    # Set axis labels and title
    ax.set_xlabel('Season', fontsize=12, color='white')
    ax.set_ylabel('Episode Number', fontsize=12, color='white')
    FONT = 'Arial'
    plt.title('{} IMDb Ratings per Episode per Season'.format(title), fontname=FONT, fontsize=16, fontweight='bold')
    plt.xlabel('Season', fontname=FONT, fontsize=16)
    plt.ylabel('Episode', fontname=FONT, fontsize=16)
    plt.subplots_adjust(left=0.3)
    return cmap, norm, ax


extracted_data = read_json()
if not extracted_data:
    print("Look for ratings of a show.")
    site = IMDB()
    extracted_data = site.get_data(query=str(input()))
    write_json(extracted_data)

title = extracted_data['Title']
image = extracted_data['Image']
extracted_data = extracted_data['Episodes']
data = {
    '{}'.format(season): [
        item['Rating'] for item in extracted_data if item['Index'][0] == season
    ]
    for season in set(item['Index'][0] for item in extracted_data)
}
df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
_dark_mode()
OFFSET_X, OFFSET_Y = 0, 0.2
OFFSET_MULT = 0.764
cmap, norm, ax = generate_heatmap()
generate_lineplot()

most_rated_season()
ratings()
average()

show_image(image)


# Show the plot
plt.show()

