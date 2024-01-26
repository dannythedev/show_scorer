import json

import numpy as np

from Functions import scale_image_url, regexify
from Request import Request


def fill_missing_episodes(episodes_list, total_episodes_each_season):
    filled_episodes_list = []
    episode_index = 0
    if episodes_list[episode_index]['Index'] == (1,0):
        episodes_list.remove(episodes_list[episode_index])

    for season, total_episodes in total_episodes_each_season:
        for episode_number in range(1, total_episodes + 1):
            if episode_index < len(episodes_list) and episodes_list[episode_index]['Index'] == (
                    season, episode_number):
                filled_episodes_list.append(episodes_list[episode_index])
                episode_index += 1
            else:
                filled_episode = {
                    'Title': '',
                    'Description': '',
                    'Rating': np.nan,
                    'Index': (season, episode_number)
                }
                filled_episodes_list.append(filled_episode)

    return filled_episodes_list


class IMDB(Request):
    def __init__(self):
        super().__init__()

        self.home_url = 'https://www.imdb.com/title/{show_id}/episodes/?season={season}'
        self.search_url = 'https://www.imdb.com/find/?q='
        self.search_api_url = 'https://v3.sg.media-imdb.com/suggestion/x/{query}.json?includeVideos=1'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

        self.xpaths = {"seasons": "//ul[@class='ipc-tabs ipc-tabs--base ipc-tabs--align-left']/a",
                       "episodes": "//div[@class='sc-9115db22-4 kyIRYf']",
                       "show_title": "//h2[@data-testid]/text()",
                       "show_image": "//div[@class='sc-a885edd8-5 dZeWWh']//img[@class='ipc-image']//@src",
                       "title": ".//div[@class='ipc-title__text']/text()",
                       "desc": ".//div[@class='ipc-html-content-inner-div']/text()",
                       "rating": ".//div[3]/div/span/text()",
                       "highest_rated": ".//div[4]/div/span/text()",
                       "more_episodes_button": "(//span[@class='ipc-see-more__text']/text())[1]"}
        self.show_id = ''
        self.show_img = ''
        self.episodes = []
        self.num_of_seasons = 0
        self.title = ''

    def get_data(self, query):
        if not query.startswith("tt"):
            self.title = query
            response = self.get(self.search_api_url.format(query=query))
            response = json.loads(response.text)
            response = response['d']
            for q in response:
                if 'qid' in q:
                    if q['qid'].lower() == 'tvseries':
                        self.show_id = q['id']
                        self.title = q['l']
                        self.show_img = q['i']['imageUrl']
                        break
        else:
            self.show_id = query

        response = self.get(self.home_url.format(show_id=self.show_id, season=1))
        self.num_of_seasons = len(self.html.get_xpath_elements([self.xpaths["seasons"]]))
        if not self.title:
            self.title = self.html.get_xpath_elements([self.xpaths["show_title"]])[0]
        if not self.show_img:
            self.show_img = self.html.get_xpath_elements([self.xpaths["show_image"]])[0]
            self.show_img = scale_image_url(self.show_img, 4)

        self.total_episodes_every_season = []
        for s in range(1, self.num_of_seasons):
            episodes = self.html.get_xpath_elements([self.xpaths["episodes"]])
            print('Message: Fetched season {}'.format(s))
            if episodes:
                more_episodes_button = regexify(r'\d+',
                                                self.html.get_xpath_elements([self.xpaths["more_episodes_button"]]))
                if more_episodes_button:
                    if len(episodes) + int(more_episodes_button) > 50:
                        print('Caution: It seems there are more than 50 episodes for season {}.'.format(s))
                for ep in range(0, len(episodes)):
                    rating = episodes[ep].xpath(self.xpaths["rating"])
                    if not rating:
                        rating = episodes[ep].xpath(self.xpaths["highest_rated"])
                    if rating:
                        rating = float(rating[0])
                    else:
                        rating = np.nan
                    ep_title = episodes[ep].xpath(self.xpaths["title"])[0]
                    ep_index = int(regexify(r'S\d+\.E(\d+)', str(ep_title)))
                    ep_desc = episodes[ep].xpath(self.xpaths["desc"])
                    if ep_desc:
                        ep_desc = ep_desc[0]
                    self.episodes.append({'Title': ep_title,
                                          'Description': ep_desc,
                                          'Rating': rating,
                                          'Index': (s, ep_index)})
                    if ep == len(episodes) - 1:
                        total_season_ep_index = int(regexify(r'S\d+\.E(\d+)',
                                                             str(episodes[ep].xpath(self.xpaths["title"])[0])))
                        self.total_episodes_every_season.append((s, total_season_ep_index))
            response = self.get(self.home_url.format(show_id=self.show_id, season=s + 1))

        return {'Title': self.title, 'Image': self.show_img,
                'Episodes': fill_missing_episodes(self.episodes, self.total_episodes_every_season)}
