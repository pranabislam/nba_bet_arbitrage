#%%
import requests, json
import pprint
import csv
import threading
import time
import datetime
import os
import sys
from pytz import timezone
from bs4 import BeautifulSoup

url_pre = 'https://www.bovada.lv/services/sports/event/v2/events/A/description/basketball/nba?marketFilterId=def&preMatchOnly=true&lang=en'
url_live = 'https://www.bovada.lv/services/sports/event/v2/events/A/description/basketball/nba?marketFilterId=def&liveOnly=true&lang=en'

url_playoffs = 'https://www.bovada.lv/services/sports/event/v2/events/A/description/basketball/nba-playoffs?marketFilterId=def&liveOnly=true&lang=en'

eastern = timezone('US/Eastern')
loc_dt = datetime.datetime.now(eastern)
today_string = loc_dt.strftime("%b-%d-%Y")

game_path = "2020_2021 Season/" + today_string


if not os.path.isdir(game_path):
    os.mkdir(path=game_path)

# %%

def get_stats(data):

    '''
    Scrapes a json file containing information on the odds and team names of
    all live NBA games. run() will call this every 10 seconds.

    Inputs:
        data (json file) - from Bovada
        sent (list) of users / numbers who've met their ROI

    Returns:
        csv_line (csv): returns the outputted statistics 
    '''

    initial_odds_away = 0
    initial_odds_home = 0


    if len(data):
        events = data['events']
        for event in events:
            home_team = event['competitors'][0]['name']
            away_team = event['competitors'][1]['name']
            print('home team, away team under: \n')
            print(home_team, away_team)
            

            try:
                event_id = event['id']
                current_time, periodNumber, score = get_time_score(event_id)
            except KeyError:
                print("No event id found in dict; key error with get_time_score")
                print("Event_id: ", event_id)
                continue
            
            csv_line = [[away_team, score[1], current_time, periodNumber], [home_team, score[0], current_time, periodNumber]]
            
            counter = 0
            
            #pprint.pprint(str(event['description']))

            ## 2020 testing 
            ## print(event['displayGroups'][0]['markets'])
            ## looks like for pre games the money line is not there yet for the games that are farther out
            try:
                money_line = event['displayGroups'][0]['markets'][1]['outcomes']
                for element in money_line:
                    prices = element['price']

                    if prices['american'] == 'EVEN':
                        current_odds = 100
                    else:
                        current_odds = int(prices['american'])

                    csv_line[counter % 2].append(current_odds)

                    counter += 1                

                ml_away_odds = csv_line[0][-1]
                ml_home_odds = csv_line[1][-1]

                away_spread = event['displayGroups'][0]['markets'][0]['outcomes'][0]['price']['handicap']
                away_spread_line = event['displayGroups'][0]['markets'][0]['outcomes'][0]['price']['american']
                away_ind = event['displayGroups'][0]['markets'][0]['outcomes'][0]['type']
                
                home_spread = event['displayGroups'][0]['markets'][0]['outcomes'][1]['price']['handicap']
                home_spread_line = event['displayGroups'][0]['markets'][0]['outcomes'][1]['price']['american']
                home_ind = event['displayGroups'][0]['markets'][0]['outcomes'][1]['type']

                if away_spread_line == 'EVEN':
                    away_spread_line = 100
                if home_spread_line == 'EVEN':
                    home_spread_line = 100

                csv_line[0].extend([away_spread_line, away_spread, away_ind])
                csv_line[1].extend([home_spread_line, home_spread, home_ind])

                print('Here are current away and home [ML, spread]  in order: \n')
                print([ml_away_odds, away_spread], [ml_home_odds, home_spread])

                name = str(event['description']) + ".csv"
                write_csv(csv_line[0], name, game_path) 
                write_csv(csv_line[1], name, game_path)
            
            except:
                print("Moneyline or spread for {} is unavailable right now \n".format(str(event['description'])))
                continue

    return csv_line

def get_time_score(event_id):
    '''
    This helper function scrapes a different part of Bovada's site where
    they store a lot of their event (basketball game) information such as
    time, score, etc.

    Inputs:
        event_id (str): the specific game being played on Bovada's website

    Returns:
        relativeGT (str): the game time left in the quarter
        periodNumber (str): the quarter in which the game is being played
        home_score, away_score (tuple): the score of the game
    '''
    url = "https://services.bovada.lv/services/sports/results/api/v1/scores/" + event_id

    page = requests.get(url).json()
    gameTime = page['clock']['gameTime'] ## less useful than relative time
    periodNumber = page['clock']['periodNumber']
    relativeGT = page['clock']['relativeGameTimeInSecs']
    home_score = page['latestScore']['home']
    away_score = page['latestScore']['visitor']


    return relativeGT, periodNumber, (home_score, away_score)

def write_csv(given_list, filename, game_path):
    '''
    Takes a list and creates a csv line of that list or appends a new line
    to an already existing csv file

    Inputs:
        given_list (list)
        filename (str): file to store csv
        game_path (str): parent path for where the game will be saved

    Returns:
        None
    '''
    file_path = game_path + "/" + filename

    with open(file_path, "a") as outfile:
        writer = csv.writer(outfile, delimiter=",")
        writer.writerow(given_list)



# %%
def run(url):
    '''
    Scrapes Bovada's website for live game statistics every 10 seconds
    (odds, scores, times, etc.) and uses that information to send texts
    as appropriate to users who have registered through the website 
    through the get_stats() function.

    Inputs:
        URL

    Returns:
        None
    '''

    while True:
        try:
            data = requests.get(url).json()
            # page = requests.get(url_live)
            # data = json.loads(page.text)[0]
            if len(data) == 0:
                print(data)
                return "Done scraping"
            
            get_stats(data[0])
            time.sleep(15)
        
        ## If Bovada blocks us or there's another error with Bovada's site,
        ## sleep for a minute and run again

        except Exception as e: 
            print('here is the exception:\n')
            print(e)
            print('========')
            print(data)
            time.sleep(60)
            run(url)
#%%
## Geting pregame data for a later merge when ran live
pregame = requests.get(url_pre).json()
get_stats(pregame[0])

# %%
