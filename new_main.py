import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from flatdict import FlatDict
import time
import threading
import requests
import json
from pprint import pprint
import random
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys


match_records = []
url = ''


class FootballScraper:
    def __init__(self, num_of_days, year, month, day):
        self.csv = 'matches.csv'
        self.num_of_days = num_of_days
        self.year = year
        self.month = month
        self.day = day
        self.max_time = 20
        self.total = []
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.scrape_id(self.num_of_days, self.year, self.month, self.day)
    
    def crawl(self, id, date):
        accesstoken = ['e3bfdc98-1aa1', 'a1354fe3-d21c', '6b981418-e930', '148ed8bc-f0c4',
                       'de412b58-02e4', '05522c91-cdda', '8c930f4c-83e9', '110c0484-d642',
                       'd948b7c5-257f', '9aeccb20-1ac2', '3bea6bb7-ef1d', '75141827-40a7',
                       '62bd03c8-4df0', '1bb90fe8-e38f', 'cb10585e-3ff5', '91ba6c85-a4c5',
                       'f5bca94d-5e7a']
        trial = 1
        while True:
            random.shuffle(accesstoken)
            headers = {
                'authority': 'api.makeyourstats.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'accesstoken': accesstoken[0],
                'origin': 'https://app.makeyourstats.com',
                'referer': 'https://app.makeyourstats.com/',
                'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27',
            }

            params = {
                'timezone': '1',
                'last_games': 'l_all',
            }

            response = requests.get(f'https://api.makeyourstats.com/api/fixture/{id}/{date}', params=params, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print('XHR Success')
                # pprint(result)
                data = self.jsontodf1(result)
                if type(data) != bool:
                    with open("football.json", "a") as file:
                        json.dump(data
                                  , file
                                  , ensure_ascii=False
                                  , indent=4
                                  , separators=(',', ': ')
                                  , sort_keys=True)
                    print('json file saved successfully')
                    # try:
                    #     existing_without_df = pd.read_csv(self.csv)
                    #     if existing_without_df.empty:
                    #         df = pd.DataFrame(data)
                    #         df.to_csv(self.csv, index=False)  # used to save the last x number of matches into a csv
                    #     else:
                    #         df = pd.DataFrame(data)
                    #         df.to_csv(self.csv, mode='a', index=False, header=False)
                    # except Exception as e:
                    #     df = pd.DataFrame(data)
                    #     df.to_csv(self.csv, index=False)  # used to save the last x number of matches into a csv
                break
            trial += 1
            time.sleep(1)
            if trial == 4:
                with open("failedfootball.json", "a") as file:
                    json.dump({"id": id, "date": date}
                              , file
                              , ensure_ascii=False
                              , indent=4
                              , separators=(',', ': ')
                              , sort_keys=True)
                break
            # print(pprint(response.json()))

    def id_to_crawl(self, all_matches):
        for all_match in all_matches[:1]:
            self.crawl(all_match['id'], all_match['date'])
            time.sleep(1.5)
        
    def scrape_id(self, num_of_days, year1, month1, day1):
        start = datetime(year1, month1, day1)
        # print(start)
        date = start
        for i in range(num_of_days):
            date = date + relativedelta(days=1)
            if len(str(date.month)) == 1:
                month = '0' + str(date.month)
            else:
                month = str(date.month)
            if len(str(date.day)) == 1:
                day = '0' + str(date.day)
            else:
                day = str(date.day)
            url = f'https://app.makeyourstats.com/?date={date.year}-{month}-{day}'
            print(url)
            ser = Service(executable_path="C:\chromedriver.exe")
            driver = webdriver.Chrome(service=ser,
                                      options=self.chrome_options)
        
            try:
                driver.get(url)
                time.sleep(self.max_time)
                total_ids = []
                container = driver.find_element(By.CSS_SELECTOR, '#content-container > div.filters > div > ul > li > button')
                container.click()
                num_of_scrolls = 0
                while True:
                    time.sleep(3)
                    container.send_keys(Keys.END)
                    # print('sleeping')
                    time.sleep(5)
                    h = driver.execute_script("return document.body.innerHTML")
                    soup = BeautifulSoup(h, 'lxml')
                    all_matches = soup.find_all('div', {'data-v-3e2eccfa': '', 'class': 'card m-1 py-1 ft-game-bg'})
                    all_matches = [match.get('id').replace('fixture', '').replace('inner', '') for match in all_matches]
                    print(all_matches)
                    if set(all_matches).issubset(set(total_ids)):
                        container.send_keys(Keys.END)
                        num_of_scrolls += 1
                        print(num_of_scrolls)
                        if num_of_scrolls > 0:
                            break
                    else:
                        num_of_scrolls = 0
                        container.send_keys(Keys.END)
                        total_ids.clear()
                        for game_id in all_matches:
                            total_ids.append(game_id)
                    print('Loading more matches...')
                driver.quit()
                all_matches = [{"id": match, "date": f'{day}-{month}-{date.year}'} for match in all_matches]
                t = threading.Thread(target=self.id_to_crawl, args=(all_matches,))
                t.start()
                print(f'Active Threads: {threading.active_count()}')
                self.total.extend(all_matches)
                print(date)
                print({'total': self.total})
                # t.join()
            except:
                pass

    def jsontodf1(self, jsonned):
        print('Number of matches: ')
        print(jsonned['localteam_calculated_stats_all']['i'],jsonned['neutral_venue'], jsonned['league_is_cup'])
        if int(jsonned['localteam_calculated_stats_all']['i']) > 5 \
                and int(jsonned['visitorteam_calculated_stats_all']['i']) > 5 \
                and jsonned['league_is_cup'] == False and jsonned['neutral_venue'] == False:
            data = {
                'league': jsonned['league_name'],
                'date': jsonned['date'],
                'localteam_name': jsonned['localteam_name'],
                'visitorteam_name': jsonned['visitorteam_name'],
                'localteam_position': int(jsonned['localteam_standings']['position']),
                'visitorteam_position': int(jsonned['visitorteam_standings']['position']),
                'teams_in_league': int(jsonned['teams_in_league']),
            }
            data.update({
                'localteam_formation_def': int(jsonned['formations']['localteam_formation'].split('-')[0]),
                'localteam_formation_mid': int(jsonned['formations']['localteam_formation'].split('-')[1]) if len(jsonned['formations']['localteam_formation'].split('-')) == 3 else int(jsonned['formations']['localteam_formation'].split('-')[2]) + int(jsonned['formations']['localteam_formation'].split('-')[1]),
                'localteam_formation_att': int(jsonned['formations']['localteam_formation'].split('-')[2]) if len(jsonned['formations']['localteam_formation'].split('-')) == 3 else int(jsonned['formations']['localteam_formation'].split('-')[3]),
                'visitorteam_formation_def': int(jsonned['formations']['visitorteam_formation'].split('-')[0]),
                'visitorteam_formation_mid': int(jsonned['formations']['visitorteam_formation'].split('-')[1]) if len(jsonned['formations']['visitorteam_formation'].split('-')) == 3 else int(jsonned['formations']['visitorteam_formation'].split('-')[2]) + int(jsonned['formations']['localteam_formation'].split('-')[1]),
                'visitorteam_formation_att': int(jsonned['formations']['visitorteam_formation'].split('-')[2]) if len(jsonned['formations']['visitorteam_formation'].split('-')) == 3 else int(jsonned['formations']['visitorteam_formation'].split('-')[3]),
            })

            print('I am here')
            print(data)
            data.update(FlatDict({'game_stats': jsonned['game_stats']}))
            data.update(FlatDict({'game_stats_intervals': jsonned['game_stats_intervals']}))
            data.update(FlatDict({'localteam_calculated_stats': jsonned['localteam_calculated_stats']}))
            data.update(FlatDict({'localteam_calculated_stats_all': jsonned['localteam_calculated_stats_all']}))
            data.update(FlatDict({'visitorteam_calculated_stats': jsonned['visitorteam_calculated_stats']}))
            data.update(FlatDict({'visitorteam_calculated_stats_all': jsonned['visitorteam_calculated_stats_all']}))
            try:
                data.update(FlatDict({'odd_new': jsonned['odd_new']}))
            except:
                pass

            print(pprint({'data': data}))

            return data
        else:
            return False


FootballScraper(1, 2021, 4, 30)
