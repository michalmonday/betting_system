#leagues to correct: ['Ligue 1', 'Eredivisie','Portuguese','Super Lig']

import re
import requests
import time as timer
import matplotlib.pyplot as plt #chart
from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as BS

#date time.strftime("%d/%m/%y")

current_season = "1718"

profitable_leagues = ['Premier League','Championship','Serie A','La Liga','Bundesliga','Ligue 1','Eredivisie'] #maybe turkish Super Lig too but have to wait some time...
#double stakes = Premier League, Championship, Serie A, Bundesliga, Ligue 1

league_names = ['Premier League','Championship','Serie A','La Liga','Bundesliga', 'Ligue 1', 'Eredivisie','Portuguese','Super Lig']
season_link_symbols = {'Premier League':'E0','Championship':'E1','La Liga':'SP1', 'Serie A':'I1', 'Bundesliga':'D1', 'Ligue 1':'F1', 'Eredivisie':'N1','Portuguese':'P1','Super Lig':'T1'}#www.football-data.co.uk historic data

league_ws_fixtures_links = { #whoscored fixtures                  
    'Premier League':'https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/6829/Stages/15151/Fixtures/England-Premier-League-2017-2018',
    
    'Championship':'https://www.whoscored.com/Regions/252/Tournaments/7/Seasons/6365/Stages/13832/Fixtures/England-Championship-2016-2017',
    'Serie A':'https://www.whoscored.com/Regions/108/Tournaments/5/Seasons/6461/Stages/14014/Fixtures/Italy-Serie-A-2016-2017',
    'La Liga':'https://www.whoscored.com/Regions/206/Tournaments/4/Seasons/6436/Stages/13955/Fixtures/Spain-La-Liga-2016-2017',
    'Bundesliga':'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/6392/Stages/13872/Fixtures/Germany-Bundesliga-2016-2017',
    'Ligue 1':'https://www.whoscored.com/Regions/74/Tournaments/22/Seasons/6318/Stages/13768/Fixtures/France-Ligue-1-2016-2017',
    'Eredivisie':'https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/6331/Stages/13792/Fixtures/Netherlands-Eredivisie-2016-2017',
    'Portuguese':'https://www.whoscored.com/Regions/177/Tournaments/21/Seasons/6438/Stages/13957/Fixtures/Portugal-Liga-NOS-2016-2017',
    'Super Lig':'https://www.whoscored.com/Regions/225/Tournaments/17/Seasons/6447/Stages/13974/Fixtures/Turkey-Super-Lig-2016-2017'
    }

league_ws_tables = { #whoscored - teamstatistics
    'Premier League':'https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/6829/Stages/15151/TeamStatistics/England-Premier-League-2017-2018',
    
    'Championship':'https://www.whoscored.com/Regions/252/Tournaments/7/Seasons/6365/Stages/13832/TeamStatistics/England-Championship-2016-2017',
    'Serie A':'https://www.whoscored.com/Regions/108/Tournaments/5/Seasons/6461/Stages/14014/TeamStatistics/Italy-Serie-A-2016-2017',
    'La Liga':'https://www.whoscored.com/Regions/206/Tournaments/4/Seasons/6436/Stages/13955/TeamStatistics/Spain-La-Liga-2016-2017',
    'Bundesliga':'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/6392/Stages/13872/TeamStatistics/Germany-Bundesliga-2016-2017',
    'Ligue 1':'https://www.whoscored.com/Regions/74/Tournaments/22/Seasons/6318/Stages/13768/TeamStatistics/France-Ligue-1-2016-2017',
    'Eredivisie':'https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/6331/Stages/13792/TeamStatistics/Netherlands-Eredivisie-2016-2017',
    'Portuguese':'https://www.whoscored.com/Regions/177/Tournaments/21/Seasons/6438/Stages/13957/TeamStatistics/Portugal-Liga-NOS-2016-2017',
    'Super Lig':'https://www.whoscored.com/Regions/225/Tournaments/17/Seasons/6447/Stages/13974/TeamStatistics/Turkey-Super-Lig-2016-2017'
    }

whoscored_league_teamid_links = { #whoscored - examplous team
    'Premier League':'https://www.whoscored.com/Teams/32',
    'Championship':'https://www.whoscored.com/Teams/161',
    'Serie A':'https://www.whoscored.com/Teams/80',
    'La Liga':'https://www.whoscored.com/Teams/65',
    'Bundesliga':'https://www.whoscored.com/Teams/37',
    'Ligue 1':'https://www.whoscored.com/Teams/304',
    'Eredivisie':'https://www.whoscored.com/Teams/113',
    'Portuguese':'https://www.whoscored.com/Teams/296',
    'Super Lig':'https://www.whoscored.com/Teams/294'
    }

oddschecker_league_url_parts = {
    'Premier League':'english/premier-league',
    'Championship':'english/championship',
    'La Liga':'spain/la-liga-primera',
    'Serie A':'italy/serie-a',
    'Bundesliga':'germany/bundesliga',
    'Ligue 1':'france/ligue-1',
    'Eredivisie':'other/netherlands/eredivisie',
    'Portuguese':'other/portugal/primeira-liga',
    'Super Lig':'other/turkey/super-lig'
    }
    

#add STR to settings and check how it influences simulation
#write some documentation about functions:
#historic analize
#fixtures/odds gathering + bets suggestions
#database updates

odds_difference_default = 0.75
league_settings = {
    'Premier League':[3, 45, odds_difference_default, 0.16, 1.2],#[1, 1, 0.3, 0.16, 1], #homeadvantage, importance_ws, diff_border, importance_str, str_mult(weird/smart homeadvantage)
    'Championship':[0.8, 75, 0.45, 0.16, 1],
    'Serie A':[3, 45, odds_difference_default, 0.16, 1.2],#[1, 55, 0.3, 0.16, 3.2],
    'La Liga':[2.6, 55, 0.3, 0.16, 1.7],
    'Bundesliga':[3, 45, odds_difference_default, 0.16, 1.2],#[0.6, 45, 0.45, 0.16, 3.2],
    'Ligue 1':[3, 45, 0.45, 0.16, 1.2],
    'Eredivisie':[3, 75, 0.45, 0.25, 1.2],
    'Portuguese':[1, 25, 0.4, 0.16, 1],
    'Super Lig':[2, 75, 0.4, 0.25, 3.2]
    }


def GetWSMatchRatings(br, league_name, date, hometeam, awayteam, mode="live"):   #this has to be changed, it enters too many unnecessary pages repatedly
    with open(league_name+'/synonyms.txt','r') as f:
        synonymlines = f.readlines()
        hometeam_synonyms = [s for s in synonymlines if hometeam in s][0].split(',')
        hometeam_synonyms = hometeam_synonyms[:len(hometeam_synonyms)-1] #removes /n

        awayteam_synonyms = [s for s in synonymlines if awayteam in s][0].split(',')
        awayteam_synonyms = awayteam_synonyms[:len(awayteam_synonyms)-1] #removes /n

    #main league fixtures page
    loaded = False
    while(loaded == False):
        try:
            br.get(whoscored_league_teamid_links[league_name])
        except:
            #print "ERROR: Couldn't load page, trying again..."
            timer.sleep(2)
            br.quit()
            br = webdriver.Chrome()
            br.set_page_load_timeout(60)
        else:
            timer.sleep(2)
            loaded = True
           
    teams_section = re.findall(r'<select\sid="teams"\sname="teams">(.+?)</select>', repr(br.page_source))[0].replace(' selected="selected"','')
    options = BS(br.page_source,"lxml").find("select", {"id":"teams", "name":"teams"}).find_all("option")
    for hometeam_synonym in hometeam_synonyms:
        for option in options:
            if option.text == hometeam_synonym:
                hometeam_url = 'https://www.whoscored.com' + option.get("value").replace("Show", "Fixtures")
                break

        '''
        try:
            #<option value="/Teams/315">Bordeaux</option>
            #<option value="/Teams/304" selected="selected">Paris Saint Germain</option>/Teams/32
            hometeam_url = 'https://www.whoscored.com' + re.findall(re.compile('<option\svalue="(.+?)">'+ hometeam_synonym.replace(' ','\s') +'</option>'),repr(teams_section))[0] + '/Fixtures'
        except:
            pass
        else:
            break
        '''
    

    #hometeam fixtures page
    loaded = False
    while(loaded == False):
        try:
            br.get(hometeam_url)
        except:
            timer.sleep(2)
            br.quit()
            br = webdriver.Chrome()
            br.set_page_load_timeout(60)
        else:
            timer.sleep(2)
            loaded = True
    
    fixtures_table = re.findall(r'<table\sid="team-fixtures"(.+>)</table>', repr(br.page_source))[0]
    fixtures_sections = re.findall(r'<tr\sclass="item(.+?)</tr>',repr(fixtures_table))
    for f in fixtures_sections:
        date = re.findall(r'"date">(.+?)</td>',f)[0].replace('-','/')
        date = date[:len(date)-4] + date[len(date)-2:len(date)]
        awayteam = re.findall(r'>(.{1,35})</a>', re.findall(r'<td\sclass="team\saway(.+?)</td>', f)[0])[0]
        #print date
        #print awayteam

        for awayteam_synonym in awayteam_synonyms:
            if awayteam == awayteam_synonym:
                match_id = re.findall(r'href="/Matches/(\d+?)/Live',f)[0]
                break

    #match preview 
    loaded = False
    while(loaded == False):
        try:
            br.get('https://www.whoscored.com/Matches/' + match_id + '/' + mode)
        except:
            timer.sleep(2)
            br.quit()
            br = webdriver.Chrome()
            br.set_page_load_timeout(60)
        else:
            timer.sleep(2)
            loaded = True

    page = repr(br.page_source)
    wsh,wsa = ParseWSRatings(page, mode)
    return wsh,wsa,br  
        
    

def GenerateBets(league_name, show_already_placed):
    homeadvantage = league_settings[league_name][0]
    importance_ws = league_settings[league_name][1]
    diff_border = league_settings[league_name][2]
    importance_str = league_settings[league_name][3]
    str_mult = league_settings[league_name][4]

    with open(league_name + '/fixtures.txt', 'r') as f:
        fixtures = f.readlines()

    with open('bets log.txt', 'r') as f:
        bets_log = repr(f.readlines())    

    suggested_bets = []

    print '\n'+league_name
    
    for i,line in enumerate(fixtures):
        if i == 0:
            continue
        values = line.split(',')#Date,HomeTeam,AwayTeam,B365H,B365D,B365A,MR_H,MR_D,MR_A,HFR19,AFR19,STR,WS_HFORM,WS_AFORM,
        if not values[12]:
            continue


        '''
        date = values[0]
        hometeam = values[1]
        awayteam = values[2]
        b365_h = float(values[3])
        b365_d = float(values[4])
        b365_a = float(values[5])
        mr_h = float(values[6])
        mr_d = float(values[7])
        mr_a = float(values[8])
        hfr19 = (float(values[9]) if float(values[9]) > 0 else 0.1)
        afr19 = (float(values[10]) if float(values[10]) > 0 else 0.1)
        sameteamsratio = (float(values[11]) * importance_str if float(values[11]) > 1 else float(values[11]) / importance_str) * str_mult
        wsh = float(values[12])
        wsa = float(values[13])
        '''

        #SIMULATE BUG
        date = values[0]
        hometeam = values[1]
        awayteam = values[2]
        b365_h = float(values[3])
        b365_d = float(values[4])
        b365_a = float(values[5])
        mr_h = float(values[6])
        mr_d = float(values[7])
        mr_a = float(values[8])
        hfr19 = (float(values[11]) * importance_str if float(values[11]) > 1 else float(values[11]) / importance_str) * str_mult
        afr19 = (float(values[9]) if float(values[9]) > 0 else 0.1)
        sameteamsratio = (float(values[10]) if float(values[10]) > 0 else 0.1)
        wsh = float(values[12])
        wsa = float(values[13])
        #SIMULATE BUG

        if b365_h == 0 or b365_a == 0 or b365_d == 0:
            continue

        #here increase difference between whoscored forms
        ws_diff = wsh - wsa
        wsh += ws_diff * importance_ws
        wsa -= ws_diff * importance_ws

        if wsh <= 0:
            wsh = 0.1
        if wsa <= 0:
            wsa = 0.1

        

        #print date + ',' + hometeam + ',' + awayteam + ',' + str(hfr19) + ',' + str(homeadvantage) + ',' + str(sameteamsratio) + ',' + str(wsh) + ',' + str(wsa)
        hfr =  hfr19 * homeadvantage * sameteamsratio * (wsh / wsa)
        afr =  afr19                 
            
        draw_prob = 1 / (b365_d if b365_d > 0 else 3.3)
        win_lose_prob = 1 - draw_prob #idk how to calculate draw chances so I use the official odds instead and share the rest of probability between home win/away win
        forms = hfr + afr

        #print date + ',' + hometeam + ',' + awayteam + ',' + str(hfr) + ',' + str(forms) + ',' + str(win_lose_prob)

        home_odds = round(1 / ((hfr / forms) * win_lose_prob),2)#ERROR at this line if ws_importance is 13, float division by 0
        away_odds = round(1 / ((afr / forms) * win_lose_prob),2)


        #official odds
        '''
        b365_h = float(values[3])
        b365_d = float(values[4])
        b365_a = float(values[5])
        mr_h = float(values[6])
        mr_d = float(values[7])
        mr_a = float(values[8])
        '''

        '''
        print '\n' + hometeam + ' ' + awayteam 
        print 'myodds=' + str(home_odds) + ', ' + str(away_odds)
        print 'official b365 odds=' + str(b365_h) + ', ' + str(b365_a)
        print 'official mr odds=' + str(mr_h)
        '''
        
        #home_odds_o = float(values[keys.index('B365H')])#official
        #print home_odds_o
        #away_odds_o = float(values[keys.index('B365A')])
        b365_marge = ((1/b365_h) + (1/b365_d) + (1/b365_a))-1

        if not mr_h == 0 and not mr_a == 0 and not mr_d == 0:
            mr_marge = ((1/mr_h) + (1/mr_d) + (1/mr_a))-1
        if b365_h - (diff_border*(b365_h - 1)) > home_odds:            
            if mr_h > b365_h:
               bookmaker = 'Marathon Bet'
               odds = str(mr_h)
            else:
                bookmaker = 'Bet365'
                odds = str(b365_h)
            #suggested_bets.append(', '.join([bookmaker,'HOME',date,hometeam,awayteam,odds]))
            if not ', '.join([date,hometeam,awayteam]) in bets_log or show_already_placed:
                suggested_bets.append(', '.join(['HOME',date,hometeam,awayteam,'Bet365 odds='+str(b365_h),'Marathon odds='+str(mr_h)]))
                #suggested_bets.append(str(round(b365_h/home_odds,2)) + ' ' + str(round(home_odds,2)))
            #print "Bet on: " + date + " " + hometeam + " " + str(home_odds_o) + " " + awayteam + " " + res


        if b365_a - diff_border > away_odds:
            if mr_a > b365_a:
               bookmaker = 'Marathon Bet'
               odds = str(mr_a)
            else:
                bookmaker = 'Bet365'
                odds = str(b365_a)
            if not ', '.join([date,hometeam,awayteam]) in bets_log or show_already_placed:
                #suggested_bets.append(', '.join([bookmaker,'AWAY',date,hometeam,awayteam,odds]))
                suggested_bets.append(', '.join(['AWAY',date,hometeam,awayteam,'Bet365 odds='+str(b365_a),'Marathon odds='+str(mr_a)]))
                #suggested_bets.append(str(round(b365_a/away_odds,2)) + ' ' + str(round(away_odds,2)))
            
            #print "Bet on: " + date + " " + hometeam + " " + awayteam + " " + str(away_odds_o)  + " " + res

    for bet in suggested_bets:
        print bet
        
            

def ParseWSRatings(htmltext, mode):
    if mode.lower() == "Preview":
        pitchsection = re.findall(re.compile('<div\sclass="pitch">.+?<div\sid="probable-lineup-stats">'),htmltext)[0]
        homesection = re.findall(re.compile('<div\sclass="home">.+?<div\sclass="away">'),pitchsection)[0]
        awaysection = re.findall(re.compile('<div\sclass="away">.+?<div\sid="probable-lineup-stats">'),pitchsection)[0]
        #print homesection
        #print awaysection
        home_individual_ratings = re.findall(re.compile('<li\sclass="player-rating\src">(.+?)</li>'),homesection)
        away_individual_ratings = re.findall(re.compile('<li\sclass="player-rating\src">(.+?)</li>'),awaysection)
        #print home_individual_ratings
        #print away_individual_ratings  
        #if len(home_individual_ratings) != 11 or len(away_individual_ratings) != 11:
            #print 'ERROR: Length of home_individual_ratings on whoscored match preview is not equal to 11'
        hr,ar = 0,0
        for home_rating in home_individual_ratings:
            hr += float(home_rating)

        for away_rating in away_individual_ratings:
            ar += float(away_rating)

        hr /= len(home_individual_ratings)
        ar /= len(away_individual_ratings)
        return str(round(hr,3)), str(round(ar,3))
    elif mode.lower() == "live":
        soup = BS(htmltext, "lxml")
        hometeam = soup.find_all("a", class_="team-name")[0].text # re.findall(re.compile('class="team-name\s">(.+?)</a>'),htmltext)[0]
        awayteam = soup.find_all("a", class_="team-name")[1].text #re.findall(re.compile('class="team-name\s">(.+?)</a>'),htmltext)[1]
        #print hometeam
        #print awayteam
        
        #ratingsection = [s for s in re.findall(re.compile('<div class="stat">.+?</div>'),repr(htmltext)) if "Average Ratings" in s]
        #print '\n' + ratingsection[0]
        
        #homerating = re.findall(re.compile('[\][n]\s+([0-9.]+)'),ratingsection[0])[0]    
        #awayrating = re.findall(re.compile('[\][n]\s+([0-9.]+)'),ratingsection[0])[1]

        ratings = soup.find("div", class_="match-centre-stat-values").find_all("span", attrs={"class":re.compile('match-centre-stat-value'), "data-field":re.compile("home|away")})
        #print ratings
        homerating = float(ratings[0].text)
        awayrating = float(ratings[1].text)
        return str(round(homerating,3)), str(round(awayrating,3))

def DownloadAllWSRatings(league_name): #download all previews for specific league to a file, then just parse the file (to avoid accessing the site multiple times)   
    br = webdriver.Chrome()
    br.set_page_load_timeout(60)

    loaded = False
    timer.sleep(1.5)
    while(loaded == False):
        try:
            br.get(league_ws_tables[league_name])
        except:
            #print "ERROR: Couldn't load page, trying again..."
            timer.sleep(2)
            br.close()
            br = webdriver.Chrome()
            br.set_page_load_timeout(60)
        else:
            loaded = True
    tbody = re.findall(r'<tbody\sid="top-team-stats-summary-content".+?</tbody>',repr(br.page_source))[0]
    team_sections = re.findall(r'<tr.+?</tr>',tbody)

    teamnames = []
    teamratings = []
    for section in team_sections:
        name = GetMyDataSynonym(league_name, re.findall(r'<a\sclass="team-link"\shref="/Teams/\d{1,9}/.+?">(.+?)</a>',section)[0])
        teamnames.append(name)
        #print name
        #print re.findall(r'stat-value rating">(.{1,6})</span>',section)[0]
        teamratings.append(re.findall(r'stat-value rating">(.{1,6})</span>',section)[0])
    
    #<tbody\sid="top-team-stats-summary-content".+?</tbody>
    #<tr.+?</tr>
    
    #<a class="team-link" href="/Teams/304">Paris Saint Germain</a>
    #<span class="stat-value rating">7.11</span>

    loaded = False
    timer.sleep(1.5)
    while(loaded == False):
        try:
            br.get(league_ws_fixtures_links[league_name])
        except:
            #print "ERROR: Couldn't load page, trying again..."
            timer.sleep(2)
            br.close()
            br = webdriver.Chrome()
            br.set_page_load_timeout(60)
        else:
            loaded = True
            br.execute_script("window.scrollTo(0, 350)")
    
    
    timer.sleep(2)
    htmltext = br.page_source
    match_preview_urls = []
    for mp_url in re.findall(re.compile('href="(/Matches/\d+?/Preview)"'),htmltext):
        match_preview_urls.append(mp_url)
        
    try:
        next_button = br.find_element_by_xpath('//*[@title="View next month"]')
    except:
        pass
    else:            
        next_button.click()
        timer.sleep(2)
        htmltext = br.page_source
        for mp_url in re.findall(re.compile('href="(/Matches/\d+?/Preview)"'),htmltext):
            match_preview_urls.append(mp_url)
            
    domain = 'https://www.whoscored.com'
    ratings_data = []
    for mp_url in match_preview_urls:
        loaded = False
        timer.sleep(1.5)
        while(loaded == False):
            try:
                br.get(domain + mp_url)
            except:
                #print "ERROR: Couldn't load page, trying again..."
                timer.sleep(2)
                br.close()
                br = webdriver.Chrome()
                br.set_page_load_timeout(60)
            else:
                loaded = True
        htmltext = br.page_source
        homerating, awayrating = ParseWSRatings(repr(htmltext), "Preview")
        hometeam = re.findall(re.compile('class="team-link\s">(.+?)</a>'),htmltext)[0]
        awayteam = re.findall(re.compile('class="team-link\s">(.+?)</a>'),htmltext)[1]
        datesections = re.findall(re.compile('<optgroup\slabel=".+?</optgroup>'),repr(htmltext))
        correct_section_index = 0
        for i,ds in enumerate(datesections):
            if hometeam + '-' + awayteam in ds:
                correct_section_index = i            
        date = re.findall(re.compile('<optgroup\slabel="(.+?)"'),datesections[correct_section_index])[0]
        #date = re.findall(re.compile('<optgroup\slabel="([a-zA-Z0-9 ,]+?)">[a-zA-Z0-9 /<"=]+?>' + hometeam + '-' + awayteam + '</option>'),repr(htmltext))[0]
        hometeam = GetMyDataSynonym(league_name, hometeam)
        awayteam = GetMyDataSynonym(league_name, awayteam)
        #<optgroup label="Sun, Sep 18 2016"><option value="/Matches/1080564" selected="selected">Watford-Manchester United</option>

        day = re.findall(r'\s\w{3}\s(\d+?)\s\d{4}', date)[0]
        if len(day)==1:
            day = '0' + day
        months = {'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12', 'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07'}
        month = months[re.findall(r'\s(\w{3})\s\d+?\s\d{4}',date)[0]]
        year = re.findall(r'\s\w{3}\s\d+?\s(\d{4})',date)[0][2:]
        date = day + '/' + month + '/' + year

        print date + ',' + hometeam + "," + awayteam + ',' + homerating + ',' + awayrating + ','
        ratings_data.append(date + ',' + hometeam + "," + awayteam + ',' + homerating + ',' + awayrating + ',')

    #with open(league_name + "/whoscored_fixtures.txt", 'w') as f:
    #    for d in ratings_data:
    #        f.write("%s\n" % d)
    
    br.close()
    return ratings_data, teamnames, teamratings

    

def TransformOddsCheckerDate(date):
    parts = date.split('-')
    date = str(parts[2]) + '/' + str(parts[1]) + '/' + str(parts[0])[2:]    
    return date

def GetMyDataSynonym(league_name,teamname):
    with open(league_name + '/synonyms.txt', 'r') as f:
        synonyms = f.readlines()
        for s in synonyms:
            if teamname in s:
                #values = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), s)
                values = s.split(",")
                return values[0]

#databases are going to be updated only from the original football-data.co.uk database + then ratings/str/ws_forms have to be added
#lines_to_replace have to be appended with the new fixtures
def UpdateFixtures(league_name):
    ws_data, ws_teams, ws_ratings = DownloadAllWSRatings(league_name)#change this function to provide full table ratings even if there's no match preview
    
    c = requests.Session()
    domain = 'http://www.oddschecker.com'    

    dates = []
    times = []
    hometeams = []
    awayteams = []
    bet365_1 = []
    bet365_x = []
    bet365_2 = []
    marathon_1 = []
    marathon_x = []
    marathon_2 = []
    hfr19s = []
    afr19s = []
    sameteamsratios = []
    wshs = []
    wsas = []
    matches_url_parts = 0
    page = c.get(domain + '/football/' + oddschecker_league_url_parts[league_name]).content
    matches_url_parts = [url for url in re.findall(re.compile('odds"\shref="(.+?winner)"'),page) if url.startswith('/football')]
    while matches_url_parts == 0:
        timer.sleep(2)
        page = c.get(domain + '/football/' + oddschecker_league_url_parts[league_name]).content
        matches_url_parts = [url for url in re.findall(re.compile('odds"\shref="(.+?winner)"'),page) if url.startswith('/football')]
        print len(matches_url_parts)
    for url_part in matches_url_parts:
        pageres = c.get(domain + url_part)
        while pageres.status_code != 200:
            timer.sleep(1)
            pageres = c.get(domain + url_part)
        page = pageres.content

        title = re.findall(re.compile('<title>(.+?)</title>'),repr(page))[0]
        if not ' v ' in title:
            continue
        print title
        date = TransformOddsCheckerDate(re.findall(r'data-time="(.+?)\s.+?"',page)[0])
        time = re.findall(r'data-time=".+?\s(.+?)"',page)[0]
        time = time[:len(time)-3]
        
        hometeam = GetMyDataSynonym(league_name,re.findall(r'<title>(.+?)\sv\s.+?\sWinner',page)[0])
        awayteam = GetMyDataSynonym(league_name,re.findall(r'<title>.+?\sv\s(.+?)\sWinner',page)[0])        

        rows = re.findall(r'<tr\sclass="diff-row\seventTableRow.+?</tr>',page)

        #the only way to know which row is playing home is to compare its name with hometeam
        try:
            upperteam_name = GetMyDataSynonym(league_name,re.findall(r'data-name="(.+?)"',rows[0])[0])
        except:
            print 'No upperteam name found'
            continue

        try:
            upperteam_odds = re.findall(r'data-odig="(.*?)"',rows[0])#list
        except:
            print 'No upperteam odds found'
            continue

        try:
            midteam_name = GetMyDataSynonym(league_name,re.findall(r'data-name="(.+?)"',rows[1])[0])
        except:
            print 'No middleteam name found'
            continue

        try:
            midteam_odds = re.findall(r'data-odig="(.*?)"',rows[1])
        except:
            print 'No middleteam odds found'
            continue

        try:
            lowerteam_name = GetMyDataSynonym(league_name,re.findall(r'data-name="(.+?)"',rows[2])[0])
        except:
            print 'No lowerteam name found'
            continue

        try:
            lowerteam_odds = re.findall(r'data-odig="(.*?)"',rows[2])#list
        except:
            print 'No lowerteam odds found'
            continue

        dates.append(date)
        times.append(time)
        hometeams.append(hometeam)
        awayteams.append(awayteam)

        #add synonym check
        if upperteam_name == hometeam:
            home_odds = upperteam_odds
            if midteam_name == awayteam:
                away_odds = midteam_odds
                draw_odds = lowerteam_odds
            elif lowerteam_name == awayteam:
                away_odds = lowerteam_odds
                draw_odds = midteam_odds
            else:
                'ERROR: could not recognise oddschecker team name, type:1 ' + hometeam + ' ' + awayteam 
            
        elif midteam_name == hometeam:
            home_odds = midteam_odds
            if upperteam_name == awayteam:
                away_odds = upperteam_odds
                draw_odds = lowerteam_odds
            elif lowerteam_name == awayteam:
                away_odds = lowerteam_odds
                draw_odds = midteam_odds
            else:
                'ERROR: could not recognise oddschecker team name, type:2 ' + hometeam + ' ' + awayteam 
                
        elif lowerteam_name == hometeam:
            home_odds = lowerteam_odds
            if upperteam_name == awayteam:
                away_odds = upperteam_odds
                draw_odds = midteam_odds
            elif midteam_name == awayteam:
                away_odds = midteam_odds
                draw_odds = upperteam_odds
            else:
                'ERROR: could not recognise oddschecker team name, type:3 ' + hometeam + ' ' + awayteam
                
        bookmakers_row = re.findall(r'<tr\sclass="eventTableHeader">(.+?)</tr>',page)[0]
        bookmakers_symbols = re.findall(r'<td\sdata-bk="(.+?)"',bookmakers_row)

        if 'B3' in bookmakers_symbols:
            bet365_index = bookmakers_symbols.index('B3')
            bet365_1.append(home_odds[bet365_index])
            bet365_x.append(draw_odds[bet365_index])  
            bet365_2.append(away_odds[bet365_index])
        else:
            bet365_1.append('')
            bet365_x.append('')
            bet365_2.append('')


        if 'MR' in bookmakers_symbols:
            marathon_index = bookmakers_symbols.index('MR')
            marathon_1.append(home_odds[marathon_index])
            marathon_x.append(draw_odds[marathon_index])
            marathon_2.append(away_odds[marathon_index])
        else:
            marathon_1.append('')
            marathon_x.append('')
            marathon_2.append('')

        ws_applies = False
        #print '=' + date + ' ' + hometeam + ' ' + awayteam 
        for ws_line in ws_data:
            values = ws_line.split(',')
            #print 'ws_date=' + values[0] + ' ' + values[1] + ' ' + values[2]
            if values[0] == date and values[1] == hometeam and values[2] == awayteam:
                wshs.append(values[3])
                wsas.append(values[4])
                ws_applies = True

        if ws_applies == False:
            #maybe change this to add ratings from the full table (DownloadAllWSRatings(league_name) would have to return 2 lists, one made from previews, one with full league table including ratings per each team)
            home_found = False
            away_found = False
            for i,team in enumerate(ws_teams):
                if team == hometeam:
                    wshs.append(ws_ratings[i])
                    home_found = True
                    
                if team == awayteam:
                    wsas.append(ws_ratings[i])
                    away_found = True

            if not home_found:       
                wshs.append('')
            if not away_found:
                wsas.append('')
            

        #here I should get the following for each game:
        #HFR19 AFR19
        #STR
        #WS_HFORM WS_AFORM

        with open(league_name+"/data_with_whoscored.txt", 'r') as f:
            historic_data = f.readlines()

        hform = GetLastXGamesFormRating(historic_data, hometeam, date, 19, True) #(4/3) playing at home advantage
        aform = GetLastXGamesFormRating(historic_data, awayteam, date, 19, True)

        hfr19s.append(str(hform) if hform != 0 else str(0.1))
        afr19s.append(str(aform) if aform != 0 else str(0.1))

        sameteamsratios.append(str(GetSameTeamsGamesRatio(historic_data, hometeam, awayteam, date, True)))
                               
        

    f = open(league_name+"/fixtures.txt", 'w')
    i=0
    
    f.write('Date,HomeTeam,AwayTeam,B365H,B365D,B365A,MR_H,MR_D,MR_A,HFR19,AFR19,STR,WS_HFORM,WS_AFORM,Time\n')
    while i<len(dates):
        '''
        print ''
        print i
        print dates[i]
        print hometeams[i]
        print awayteams[i]
        print bet365_1[i]
        print bet365_x[i]
        print bet365_2[i]
        print marathon_1[i]
        print marathon_x[i]
        print marathon_2[i]
        print sameteamsratios[i]
        print hfr19s[i]
        print afr19s[i]
        print wshs[i]
        print wsas[i]
        print times[i]
        '''
        line = ",".join([dates[i], hometeams[i], awayteams[i], bet365_1[i], bet365_x[i], bet365_2[i], marathon_1[i], marathon_x[i], marathon_2[i], hfr19s[i], afr19s[i], sameteamsratios[i], wshs[i], wsas[i], times[i], '\n'])
        f.write(line)
        i+=1
    f.close
    print league_name + ' fixtures has been updated.'
    #return hometeams,awayteams,bet365_1,bet365_x,bet365_2,marathon_1,marathon_x,marathon_2


#<a class="button btn-1-small" title="View all Hull v Arsenal odds" href="/football/english/premier-league/hull-v-arsenal/winner" onclick="s_objectID
#odds" href="/football/english/premier-league/west-ham-v-middlesbrough/winner"
#<span class="date">Sunday 25th September / 16:00</span>


def IsDateNewerThan(date,date2):
    date = date.split('/')
    date2 = date2.split('/')
    
    year = float(date[2])
    month = float(date[1])
    day = float(date[0])

    year2 = float(date2[2])
    month2 = float(date2[1])
    day2 = float(date2[0])

    if year < year2:
        return False
    elif year > year2:
        return True
    elif month < month2:
        return False
    elif month > month2:
        return True
    elif day < day2:
        return False
    elif day > day2:
        return True
    return False




def Placebet(odds, res, bank, stake):
    if res == "won":
        bank = bank + (stake*odds) - stake
    else:
        bank = bank - stake
    return bank

'''
def i(key):
    return datakeys.index(key)

    
def GetGoalsRatio(teamname, range_matches):
    scored = 0
    lost = 0
    j = 0
    for line in reversed(database):
        if line == database[0]:
            continue
        if j>=range_matches:
            if lost == 0:
                lost = 0.01
            if scored == 0:
                scored = 0.01
            return scored/lost, j
        
        #d = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*),"), line)
        d = line.split(",")
        if d[i('HomeTeam')] == teamname:
            scoredkey = "FTHG"
            lostkey = "FTAG"
            j+=1
        elif d[i('AwayTeam')] == teamname:
            scoredkey = "FTAG"
            lostkey = "FTHG"
            j+=1
        else:
            continue
        scored+= float(d[i(scoredkey)])
        lost+= float(d[i(lostkey)])      
    #FTHG = Full Time Home Team Goals
    #FTAG = Full Time Away Team Goals
    if lost == 0:
        lost = 0.01
    if scored == 0:
        scored = 0.01
    return scored/lost, j
'''


def AddRating(data):#based on last x number of matches
    #there must be a data check to see if the date is newer than the first game in the list

    #keys = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), data[0])
    keys = data[0].split(",")
    for index, line in enumerate(data):
        #print line
        if index > len(data)-2:
            break            
        if line == data[0] or len(line) < 60:
            continue

        
        #print "len = " + str(len(line))
        #values = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), line)
        values = line.split(",")
        date = values[keys.index('Date')]
        hometeam = values[keys.index('HomeTeam')]
        awayteam = values[keys.index('AwayTeam')]
        h_form = GetLastXGamesFormRating(data, hometeam, date, 19, True) #(4/3) playing at home advantage
        a_form = GetLastXGamesFormRating(data, awayteam, date, 19, True)

        if a_form == 0:
            a_form = 0.1
        if h_form == 0:
            h_form = 0.1

        curHFR =  values[keys.index('HFR19')]
        curAFR =  values[keys.index('AFR19')]

        if curHFR == "" and curAFR == "":
            data[index] = ""
            i = 0
            while i<len(values):
                if i == keys.index('HFR19'):
                    data[index] += str(h_form) + ','
                elif i == keys.index('AFR19'):
                    data[index] += str(a_form) + ','  
                else:
                    data[index] += values[i] + ','
                i+=1
            #print date + " Added ratings(19)= " + str(h_form) + " " + str(a_form)
    return data

def GetLastXGamesFormRating(data, teamname, date, num, signbool):#significance decrease with time
    #keys = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), data[0])
    keys = data[0].split(",")
    #print teamname + " " + date +" "+ str(num)
    h_ind = keys.index('HomeTeam')
    a_ind = keys.index('AwayTeam')
    date_ind = keys.index('Date')
    res_ind = keys.index('FTR')
    foundline = False
    #gamelist = []
    winningcount = 0
    count = 0
    #print date
    i = 0
    significance = 1
    #opponents_ratings = 0
    for line in data:
        i+=1
        if line == data[0] or len(line) < 60:
            continue

        
        #print len(line)
        #values = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), line)
        values = line.split(",")
        
        if line == data[1]:#to add rating to fixtures
            if IsDateNewerThan(date,values[date_ind]):
                foundline = True
        
        if values[date_ind] == date and (values[h_ind] == teamname or values[a_ind] == teamname):
            foundline = True
            #print "\nfoundline"
        elif foundline == True:
            if values[h_ind] == teamname:
                #print "h" + values[h_ind]
                if values[res_ind] == "H":
                    winningcount += 1*significance
                elif values[res_ind] == "D":
                    winningcount += 0.5*significance
                count += 1*significance
                significance *= 0.95 if signbool == True else 1
                #opponents_ratings += GetLastXGamesFormRatingDuplicate(data, values[a_ind], date, num, True)*significance
            elif values[a_ind] == teamname:
                #print "a "+values[a_ind]
                if values[res_ind] == "A":
                    winningcount += 1*significance
                elif values[res_ind] == "D":
                    winningcount += 0.5*significance
                count += 1*significance
                significance *= 0.95 if signbool == True else 1
                #opponents_ratings += GetLastXGamesFormRatingDuplicate(data, values[h_ind], date, num, True)*significance
        if count >= num:
            break
    #print winningcount
    #print count
        if i == len(data)-1 and count == 0:
            return 0.5

    #print "Ratings=" + str(round(winningcount / count, 2)) + " Opponents ratings=" + str(round(opponents_ratings/count,2))      
    #return round(((winningcount / count) + (opponents_ratings/count)) / 2, 2)
    rating = (round(winningcount / count, 2) if round(winningcount / count, 2) > 0 else 0.1)
    return rating


def AddSameTeamsRatio(data):
    #keys = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), data[0])
    keys = data[0].split(",")
    for index, line in enumerate(data):
        #print line
        if index > len(data)-2:
            break            
        if line == data[0] or len(line) < 60:
            continue
        #print "len = " + str(len(line))
        #values = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), line)
        values = line.split(",")
        date = values[keys.index('Date')]
        hometeam = values[keys.index('HomeTeam')]
        awayteam = values[keys.index('AwayTeam')]
        ratio = GetSameTeamsGamesRatio(data, hometeam, awayteam, date, True)

        curSTR =  values[keys.index('STR')]

        if curSTR == "":
            data[index] = ""
            i = 0
            while i<len(values):
                if i == keys.index('STR'):
                    data[index] += str(ratio) + ','
                    #print date + " added STR=" + str(ratio) + " " + hometeam + " " + awayteam 
                else:
                    data[index] += values[i] + ','
                i+=1
    return data    

def GetSameTeamsGamesRatio(data, hometeam, awayteam, date, signbool):
    #keys = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), data[0])
    keys = data[0].split(",")
    h_ind = keys.index('HomeTeam')
    a_ind = keys.index('AwayTeam')
    date_ind = keys.index('Date')
    res_ind = keys.index('FTR')
    foundline = False
    count = 0
    hometeam_score = 0
    awayteam_score = 0
    significance = 1
    for line in data:
        if line == data[0] or len(line) < 60:
            continue
        #print len(line)
        #values = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), line)
        values = line.split(",")
        if line == data[1]:#to add rating to fixtures
            if IsDateNewerThan(date,values[date_ind]):
                foundline = True
        if values[date_ind] == date and values[h_ind] == hometeam and values[a_ind] == awayteam:
            foundline = True
            #print "\nfoundline"
        elif foundline == True:
            if values[h_ind] == hometeam and values[a_ind] == awayteam:                   
                count+=1
                if values[keys.index('FTR')] == "H":
                    hometeam_score += 1*significance
                elif values[keys.index('FTR')] == "A":
                    awayteam_score += 1*significance
                else:
                    hometeam_score += 0.5*significance
                    awayteam_score += 0.5*significance                    
                #print hometeam_score
                #print awayteam_score
                significance *= 0.8 if signbool == True else 1
            elif values[h_ind] == awayteam and values[a_ind] == hometeam:
                count+=1
                if values[keys.index('FTR')] == "A":
                    hometeam_score += 1*significance
                elif values[keys.index('FTR')] == "H":
                    awayteam_score += 1*significance
                else:
                    hometeam_score += 0.5*significance
                    awayteam_score += 0.5*significance
                #print hometeam_score
                #print awayteam_score
                significance *= 0.8 if signbool == True else 1
            else:
                continue
            #print "Previous game: " + values[date_ind] + " " + values[h_ind] + " vs " + values[a_ind]
    if hometeam_score == 0:
        hometeam_score = 0.5
    if awayteam_score == 0:
        awayteam_score = 0.5
    return round(hometeam_score / awayteam_score, 2)
    


'''
Div = League Division
Date = Match Date (dd/mm/yy)
HomeTeam = Home Team
AwayTeam = Away Team
FTHG = Full Time Home Team Goals
FTAG = Full Time Away Team Goals
FTR = Full Time Result (H=Home Win, D=Draw, A=Away Win)
HTHG = Half Time Home Team Goals
HTAG = Half Time Away Team Goals
HTR = Half Time Result (H=Home Win, D=Draw, A=Away Win)

Match Statistics (where available)
Referee = Match Referee
HS = Home Team Shots
AS = Away Team Shots
HST = Home Team Shots on Target
AST = Away Team Shots on Target
HY = Home Team Yellow Cards
AY = Away Team Yellow Cards
HR = Home Team Red Cards
AR = Away Team Red Cards
B365H = Bet365 home win odds
B365D = Bet365 draw odds
B365A = Bet365 away win odds
HFR19 = home form rating based on last 19 games
AFR19 = away form rating based on last 19 games
STR = same teams ratio (based on hometeam vs awayteam previous games) over 1.0 = hometeam is stronger, under 1.0 = awayteam is stronger
'''

class Database:
    def __init__(self, league_name="Premier League"):
        self.keys = self.GetLines(league_name)[0].split(",")
        
    def CreateNewDatabase(self, league_name):
        data = []
        c = requests.Session()
        i = 18   
        data.append(",".join(mykeys)) #first line
        print "Downloading " + league_name + " data from \"football-data.co.uk\"..."
        while i>5:
            season_index1 = (str(i-1) if len(str(i-1)) > 1 else '0' + str(i-1))
            season_index2 = (str(i) if len(str(i)) > 1 else '0' + str(i))
            url = 'http://www.football-data.co.uk/mmz4281/' + season_index1 + season_index2 + '/' + season_link_symbols[league_name] + '.csv'
            print "Url = ", url
            text = c.get(url).content.decode("utf-8")
            #print text
            lines = re.findall(re.compile('(.+)\r'),text)
            #keys = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), lines[0])
            keys = lines[0].split(",")
            for l in reversed(lines):
                empty_found = False
                myline = ""
                for key in mykeys:
                    try:
                        ind = keys.index(key)
                    except:
                        #print 'Index for key=' + key + ' not found. Season link=' + season_links[i]
                        myline += ','
                        continue
                    else:
                        #values = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), l)
                        values = l.split(",")
                        if values[ind] == "":
                            empty_found = True
                            #print "Value for key=" + key + " is empty. Season link=" + season_links[i] 
                        myline += values[ind] + ","
                if l == lines[0]:
                    myline = "-----NEW_SEASON-----"
                elif empty_found == False:
                    data.append(myline + ",")
            i-=1

        #for d in data:
            #print d

        print "\nAdding ratings..."

        data = AddRating(data)

        print "Adding same teams ratios..."
        data = AddSameTeamsRatio(data)

        f = open(league_name+"/data.txt", 'w')
        for d in data:
          f.write("%s\n" % d)
        f.close()

        print "Done :)"

    def GetLines(self, league_name):
        with open(league_name + '/data_with_whoscored.txt', 'r') as f:
            data = f.readlines()
        return data

    def SaveLines(self, league_name, data):
        with open(league_name + '/data_with_whoscored.txt', 'w') as f:
            f.writelines(data)

    def GetLastXGamesValues(self, league_name, teamname, date, amount, valueKeys):
        with open(league_name + "/data_with_whoscored.txt", "r") as f:
            data = f.readlines()
        #keys = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), data[0])
        keys = data[0].split(",")
        #print teamname + " " + date +" "+ str(num)
        h_ind = keys.index('HomeTeam')
        a_ind = keys.index('AwayTeam')
        date_ind = keys.index('Date')
        val_inds = [keys.index(key) for key in valueKeys]
        foundline = False
        winningcount = 0
        count = 0
        i = 0
        returned_values = []
        #opponents_ratings = 0
        for line in data:
            i+=1
            if line == data[0] or len(line) < 30:
                continue

            #values = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), line)
            values = line.split(",")
            
            if line == data[1]:
                if IsDateNewerThan(date,values[date_ind]):
                    foundline = True

            if values[date_ind] == date and (values[h_ind] == teamname or values[a_ind] == teamname):
                foundline = True
            elif foundline == True:
                if values[h_ind] == teamname:
                    returned_values.append(values[val_inds[0]])
                    count += 1
                elif values[a_ind] == teamname:
                    returned_values.append(values[val_inds[1]])
                    count += 1
            if count >= amount:
                break
        #print winningcount
        #print count
            if i == len(data)-1 and count == 0:
                return returned_values
        return returned_values
    
    #database.CalculatePerformanceRating("Premier League", "Man City", "21/08/17", 10)
    def CalculatePerformanceRating(self, league_name, teamname, date, amount):
        performances = self.GetLastXGamesValues(league_name, teamname, date, amount, ["WS_HFORM", "WS_AFORM"])
        significance = 1.0
        overall = 0
        signCount = 0
        for p in performances:
            try:
                overall += float(p) * significance
            except Exception as e:
                #print performances
                overall += 6.87 * significance 
            signCount += significance
            significance *= 0.9
        return overall / signCount if signCount > 0 else 1

    def UpdateDatabase(self, league_name):
        print 'Updating database for: ' + league_name
        with open(league_name + '/data_with_whoscored.txt', 'r') as f:
            data = f.readlines()

        br = webdriver.Chrome()#GetWSMatchRatings(br.league_name, date, hometeam, awayteam)
        br.set_page_load_timeout(60)
            
        c = requests.Session()
        text = c.get('http://www.football-data.co.uk/mmz4281/' + current_season + '/' + season_link_symbols[league_name] + '.csv').content.decode("utf-8")
        newdata = re.findall(re.compile('(.+)\r'),text)
        

        new_matches = []
        for i,n_line in enumerate(newdata):
            if i == 0:
                keys = n_line.split(',')
                continue
            values = n_line.split(',')
            date = values[keys.index('Date')]
            hometeam = values[keys.index('HomeTeam')]
            awayteam = values[keys.index('AwayTeam')]
            if values[keys.index('FTHG')] == '':
                continue
            

            if not ','.join([date,hometeam,awayteam]) in repr(data):
                wsh, wsa, br = GetWSMatchRatings(br, league_name, date, hometeam, awayteam)
                empty_found = False
                newline = ""
                for j,key in enumerate(mykeys):
                    try:
                        ind = keys.index(key)
                    except:
                        if j == mykeys.index('HFR19'):
                            newline += str(GetLastXGamesFormRating(data, hometeam, date, 19, True))+','
                        elif j == mykeys.index('AFR19'):
                            newline += str(GetLastXGamesFormRating(data, awayteam, date, 19, True))+','
                        elif j == mykeys.index('STR'):
                            newline += str(GetSameTeamsGamesRatio(data, hometeam, awayteam, date, True))+','
                        elif j == mykeys.index('WS_HFORM'):
                            newline += wsh+','
                        elif j == mykeys.index('WS_AFORM'):
                            newline += wsa+','
                        else:
                            newline += ','
                        continue
                    else:                    
                        newline += values[ind] + ","
                print newline
                new_matches.append(newline+'\n')

        new_data = []
        for i,line in enumerate(data):
            if i == 0:
                new_data.append(line)
                continue
            values = line.split(',')
            for new_line in reversed(new_matches):
                new_values = new_line.split(',')
                if IsDateNewerThan(new_values[1],values[1]):
                    new_data.append(new_line)
                    new_matches.remove(new_line)
            new_data.append(line)

        f = open(league_name+"/data_with_whoscored.txt", 'w')
        for new_line in new_data:
            f.write("%s" % new_line)
        f.close()

        print league_name + ' database has been updated.\n\n'
        br.close()   

    def GetDataKeys(self, data):
        return data[0].split(",")

    def SimulateLongTermBetting(self, league_name, bank, stake, diff_border, importance_ws, homeadvantage, importance_str, str_mult, from_date, to_date, chart_bets_step, WS_BOOL, ws_number_of_games=1):
        f = open(league_name+"/data_with_whoscored.txt", 'r')
        data = f.readlines()
        f.close()

        keys = data[0].split(",")
        
        
        homebets = 0
        awaybets = 0
        totalodds = 0
        initialbank = bank
        chart_data = []
        chart_data.append(initialbank)
        chart_index = 0
                
        h_ind = mykeys.index('HomeTeam')
        a_ind = mykeys.index('AwayTeam')
        date_ind = mykeys.index('Date')
        res_ind = mykeys.index('FTR')
        hfr19_ind = mykeys.index('HFR19')
        afr19_ind = mykeys.index('AFR19')
        #hfr5_ind = mykeys.index('HFR5')
        #afr5_ind = mykeys.index('AFR5')
        str_ind = mykeys.index('STR')
        wsh_ind = mykeys.index('WS_HFORM')
        wsa_ind = mykeys.index('WS_AFORM')
        hg_ind = mykeys.index('FTHG') #home goals index
        ag_ind = mykeys.index('FTAG')
        totalpercentmarge = 0

        bets_output_list = ["bet,date,hometeam,awayteam,homegoals,awaygoals,bank,my_homeodds,my_awayodds,official_homeodds,official_awayodds,hfr19,afr19,str,wsh_form,wsa_form\n"]
        
        for index, line in enumerate(reversed(data)):
            #print line
            if index > len(data)-2:
                break        
            if line == data[0] or len(line) < 60:
                continue
            #print len(line)
            #values = re.findall(re.compile("([0-9a-zA-Z <>./_'-]*)[,]{0,1}"), line)
            values = line.split(",")
            if not values[wsh_ind]:
                continue
            
            date = values[date_ind]
            if IsDateNewerThan(from_date, date) or IsDateNewerThan(date, to_date):
                continue
 
            
            hometeam = values[h_ind]
            awayteam = values[a_ind]
            homegoals = values[hg_ind]
            awaygoals = values[ag_ind]
            sameteamsratio = (float(values[str_ind]) * importance_str if float(values[str_ind]) > 1 else float(values[str_ind]) / importance_str)* str_mult
            if WS_BOOL == True:
                wsh_form = self.CalculatePerformanceRating(league_name, hometeam, date, ws_number_of_games)#float(values[wsh_ind])
                wsa_form = self.CalculatePerformanceRating(league_name, awayteam, date, ws_number_of_games)#float(values[wsa_ind])
                #print wsh_form, wsa_form
            else:
                wsh_form = 7
                wsa_form = 7
            #here increase difference between whoscored forms
            ws_diff = wsh_form - wsa_form
            wsh_form += ws_diff * importance_ws
            wsa_form -= ws_diff * importance_ws
            
            
            if wsh_form <= 0:
                wsh_form = 0.1
            if wsa_form <= 0:
                wsa_form = 0.1

            hfr19 = (float(values[hfr19_ind]) if float(values[hfr19_ind]) > 0 else 0.1)
            afr19 = (float(values[afr19_ind]) if float(values[afr19_ind]) > 0 else 0.1)
            '''
            #SIMULATE MY BUG
            hometeam = values[h_ind]
            awayteam = values[a_ind]
            
            sameteamsratio = (float(values[afr19_ind]) if float(values[afr19_ind]) > 0 else 0.1)
            wsh_form = float(values[wsh_ind])
            wsa_form = float(values[wsa_ind])
            #here increase difference between whoscored forms
            ws_diff = wsh_form - wsa_form
            wsh_form += ws_diff * importance_ws
            wsa_form -= ws_diff * importance_ws

            if wsh_form <= 0:
                wsh_form = 0.1
            if wsa_form <= 0:
                wsa_form = 0.1

            hfr19 = (float(values[str_ind]) * importance_str if float(values[str_ind]) > 1 else float(values[str_ind]) / importance_str)* str_mult
            afr19 = (float(values[hfr19_ind]) if float(values[hfr19_ind]) > 0 else 0.1)
            #SIMULATE MY BUG
            '''
            
            #print date + ',' + hometeam + ',' + awayteam + ',' + str(hfr19) + ',' + str(homeadvantage) + ',' + str(sameteamsratio) + ',' + str(wsh_form) + ',' + str(wsa_form)
            hfr =  hfr19 * homeadvantage * sameteamsratio * (wsh_form / wsa_form) #STR can be higher or lower than 1
            afr =  afr19            

            #hfr = homeadvantage * sameteamsratio * wsh_form
            #afr = wsa_form
                           
            draw_prob = 1 / float(values[mykeys.index('B365D')])
            win_lose_prob = 1 - draw_prob #idk how to calculate draw chances so I use the official odds instead and share the rest of probability between home win/away win
            forms = hfr + afr

            #print date + ',' + hometeam + ',' + awayteam + ',' + str(hfr) + ',' + str(forms) + ',' + str(win_lose_prob)

            home_odds = round(1 / ((hfr / forms) * win_lose_prob),2)#ERROR at this line if ws_importance is 13, float division by 0
            away_odds = round(1 / ((afr / forms) * win_lose_prob),2)

            home_odds_o = float(values[mykeys.index('B365H')])#official
            #print home_odds_o
            away_odds_o = float(values[mykeys.index('B365A')])

            if away_odds < 0 or home_odds < 0:
                print "My odds correctness check, should be equal to 1: " + str(round((1/home_odds) + (1/away_odds) + (1/float(values[mykeys.index('B365D')])),2))
                print "Official odds correctness check, should be equal to 1: " + str(round((1/home_odds_o) + (1/away_odds_o) + (1/float(values[mykeys.index('B365D')])),2))
                
                #print "Odds differences: " + date + " "  + hometeam + " = " + str(home_odds - home_odds_o) + " " + awayteam + " = " + str(away_odds - away_odds_o)
                print "My odds = " + str(home_odds) + " " + values[mykeys.index('B365D')] + " " + str(away_odds)
                print "Official odds = " + str(home_odds_o) + " " + values[mykeys.index('B365D')] + " " + str(away_odds_o)
                print ''
            #print date + " " + str(home_odds) + " " + str(away_odds)

            '''
            print '\n' + hometeam + ' ' + awayteam
            print hfr19
            print afr19
            print sameteamsratio
            print importance_str
            print homeadvantage
            print wsh_form
            print wsa_form
            print "My odds = " + str(home_odds) + " " + values[mykeys.index('B365D')] + " " + str(away_odds)
            print "Official odds = " + str(home_odds_o) + " " + values[mykeys.index('B365D')] + " " + str(away_odds_o)
            '''             
            
            marge = 0
            
            if home_odds_o - (diff_border*(home_odds_o - 1)) > home_odds:
                if values[mykeys.index('FTR')] == 'H':
                    res = 'won'
                else:
                    res = 'lost'
                bank = Placebet(home_odds_o, res, bank, stake)
                marge = ((1/home_odds_o) + (1/float(values[mykeys.index('B365D')])) + (1/away_odds_o))-1
                #print "Bet on " + hometeam + ": "  + date + " " + hometeam + " " + str(home_odds_o) + " " + awayteam + " " + res
                #print home_odds
                homebets += 1
                totalodds += home_odds_o
                #bets_output_list = ["bet,date,hometeam,awayteam,homegoals,awaygoals,bank,my_homeodds,my_awayodds,official_homeodds,official_awayodds,hfr19,afr19,str,wsh_form,wsa_form\n"]
                bets_output_list.append(",".join([str(item) for item in["1", date, hometeam, awayteam, homegoals, awaygoals, bank, home_odds, away_odds, home_odds_o, away_odds_o, hfr19, afr19, sameteamsratio, wsh_form, wsa_form]]) + "\n")

            if away_odds_o - (diff_border*(away_odds_o - 1)) > away_odds:
                if values[mykeys.index('FTR')] == 'A':
                    res = 'won'
                else:
                    res = 'lost'
                bank = Placebet(away_odds_o, res, bank, stake)
                marge = ((1/home_odds_o) + (1/float(values[mykeys.index('B365D')])) + (1/away_odds_o))-1
                #print "Bet on " + awayteam + ": " + date + " " + hometeam + " " + awayteam + " " + str(away_odds_o)  + " " + res
                #print away_odds
                awaybets += 1
                totalodds += away_odds_o

                bets_output_list.append(",".join([str(item) for item in["2", date, hometeam, awayteam, homegoals, awaygoals, bank, home_odds, away_odds, home_odds_o, away_odds_o, hfr19, afr19, sameteamsratio, wsh_form, wsa_form]]) + "\n")
                
            chart_index += 1

            if chart_index >= chart_bets_step:
                chart_index = 0
                chart_data.append(bank)

            '''
#just an example to show what would happen if I bet on home win every time
            if values[mykeys.index('FTR')] == 'H':
                res = 'won'
            else:
                res = 'lost'
            bank = Placebet(home_odds_o, res, bank, 1)
            marge = ((1/home_odds_o) + (1/float(values[mykeys.index('B365D')])) + (1/away_odds_o))-1
            '''

            totalpercentmarge += marge

        if homebets > 0 or awaybets > 0:
            averageodds = str(round(totalodds / (homebets+awaybets),1))
        else:
            averageodds = str('None')
        #print "Bank=" + str(bank)
        #print "Total marge=" + str(round(totalpercentmarge,2)) + "% (percent of money you lose if you bet on all three options)"
        #print "Won=" + str(round(bank - initialbank + totalpercentmarge, 2)) + "% - " + str(round(totalpercentmarge, 2)) + "% (winnings - marge). Average odds=" + averageodds + ' Home/Away='+str(homebets)+'/'+str(awaybets)

        with open(league_name + "/bets_output.csv", "w+") as bets_output_file:
            bets_output_file.writelines(bets_output_list)
        return chart_data, bank - initialbank, homebets, awaybets

    def Produce_Bets_Output(self, league_name, initial_bank, stake, from_date, to_date, chart_data_bet_step):
        default_homeadvantage = league_settings[league_name][0]
        default_ws_importance = league_settings[league_name][1]
        default_odds_border = league_settings[league_name][2]
        default_str_importance = league_settings[league_name][3]
        default_str_mult = league_settings[league_name][4]

        database.SimulateLongTermBetting(league_name, initial_bank, stake, default_odds_border, default_ws_importance, default_homeadvantage, default_str_importance, default_str_mult, from_date, to_date, chart_data_bet_step, False)
        print "Finished simulation for the: " + league_name

mykeys = ['Div','Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','HTHG','HTAG','HTR','Referee','HS','AS','HST','AST','HY','AY','HR','AR','B365H','B365D','B365A','HFR19','AFR19','STR', 'WS_HFORM', 'WS_AFORM']

#no ref
#Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HTR,HS,AS,HST,AST,HF,AF,HC,AC,HY,AY,HR,AR,B365H,B365D,B365A,BWH,BWD,BWA,IWH,IWD,IWA,LBH,LBD,LBA,PSH,PSD,PSA,WHH,WHD,WHA,VCH,VCD,VCA,Bb1X2,BbMxH,BbAvH,BbMxD,BbAvD,BbMxA,BbAvA,BbOU,BbMx>2.5,BbAv>2.5,BbMx<2.5,BbAv<2.5,BbAH,BbAHh,BbMxAHH,BbAvAHH,BbMxAHA,BbAvAHA,PSCH,PSCD,PSCA

#league_names = ['Premier League','Championship','Serie A','La Liga','Bundesliga', 'Ligue 1', 'Eredivisie','Portuguese','Super Lig']

'''
database = Database()

profitable_only = True
for league_name in ['Premier League']:#league_names:
    if profitable_only == True:
        if not league_name in profitable_leagues:
            continue
    #database.UpdateDatabase(league_name)
    UpdateFixtures(league_name)
    #GenerateBets(league_name, True) # (league_name, show_already_placed)
    
raise SystemExit
'''


#create function to check which bets should be placed

#create UpdateDatabase function which will directly go to whoscored and check last month/2 months matches
#maybe just update data.txt + add few new lines to lines_to_replace.txt if they don't exist there yet, then replace them all


        
database = Database()
#database.CreateNewDatabase('Serie A')
#database.CreateNewDatabase('La Liga')
#database.CreateNewDatabase('Ligue 1')
#database.CreateNewDatabase('Eredivisie')
#database.CreateNewDatabase('Portuguese')
#database.CreateNewDatabase('Super Lig')
#database.CreateNewDatabase('Championship')
#raise SystemExit


initial_bank = 400
stake = 20
#default_homeadvantage = 2.6#1.33
#default_odds_border = 0 #0.3
#default_ws_importance = 40
chart_data_bet_step = 1 #how smooth/sharp the graph will be (1 - sharp) (30 - smooth)
from_date = '01/01/11'
#from_date = '01/08/16' #season
#from_date = '19/09/16' #started betting
#from_date = '01/10/16'
to_date = '01/08/99'

for league_name in ["Championship"]:#["Premier League", "Bundesliga", "Serie A"]:
    database.Produce_Bets_Output(league_name, initial_bank, stake, from_date, to_date, chart_data_bet_step)
raise SystemExit

axis_y_mult = 150 #was 450
default_only = False
total_bets = 0
total_profit = 0

for league_name in ["Premier League"]:#["Premier League"]:#["Bundesliga"]:#league_names:    
    default_homeadvantage = league_settings[league_name][0]
    default_ws_importance = league_settings[league_name][1]
    default_odds_border = league_settings[league_name][2]
    default_str_importance = league_settings[league_name][3]
    default_str_mult = league_settings[league_name][4]

    print '\n'+league_name

    if default_only:
        chart_data, profit, home_bets, away_bets = database.SimulateLongTermBetting(league_name, initial_bank, stake, default_odds_border, default_ws_importance, default_homeadvantage, default_str_importance, default_str_mult, from_date, to_date, chart_data_bet_step)
        total_bets += home_bets + away_bets
        total_profit += profit
        print profit
        print total_profit
        continue

    
    highest_data_length = 0

      
    #homeadvantage graph
    plt.style.use('bmh')
    plt.subplot(6, 1, 1)
    chart_legend_varlist = []
    homeadvantage = 0.6
    while homeadvantage < 4.0:
        chart_legend_varlist.append(str(homeadvantage))
        #print 'Importance of WS var=' + str(round(i_ws,1))
        chart_data, profit, home_bets, away_bets = database.SimulateLongTermBetting(league_name, initial_bank, stake, default_odds_border, default_ws_importance, homeadvantage, default_str_importance, default_str_mult, from_date, to_date, chart_data_bet_step, False)#(bank, stake, diff_border, importance_ws, homeadvantage, chart_bets_step):
        data_length = len(chart_data)
        if data_length > highest_data_length:
            highest_data_length = data_length
        plt.plot(range(data_length), chart_data)
        homeadvantage +=1

    plt.plot([0,highest_data_length],[0,0], 'k')#black 0 line
    plt.plot([0,highest_data_length],[initial_bank,initial_bank], 'g', linestyle='dashed')#black bank line
    plt.axis([0,highest_data_length*1.01,stake*-axis_y_mult,(axis_y_mult * stake)+initial_bank])
    plt.ylabel('Home_advantage')
    plt.legend(chart_legend_varlist, loc='upper left')
    
    
    
    #whoscored ratings importance
    plt.style.use('bmh')
    plt.subplot(6, 1, 2)

    i_ws = 0.6 
    chart_legend_varlist = []
    
    while i_ws < 1.7:
        chart_legend_varlist.append(str(i_ws))
        #print 'Importance of WS var=' + str(round(i_ws,1))
        chart_data, profit, home_bets, away_bets = database.SimulateLongTermBetting(league_name, initial_bank, stake, default_odds_border, i_ws, default_homeadvantage, default_str_importance, default_str_mult, from_date, to_date, chart_data_bet_step, True)#(bank, stake, diff_border, importance_ws, homeadvantage, chart_bets_step):

        data_length = len(chart_data)
        plt.plot(range(data_length), chart_data)
        i_ws += 0.5
        print "Whoscored ratings importance: ", i_ws

    plt.plot([0,highest_data_length],[0,0], 'k')#black 0 line

    plt.plot([0,highest_data_length],[initial_bank,initial_bank], 'g', linestyle='dashed')#green bank line
    plt.axis([0,highest_data_length*1.01,stake*-axis_y_mult,(axis_y_mult * stake)+initial_bank])
    plt.ylabel('WS_importance')
    plt.legend(chart_legend_varlist, loc='upper left')

    #whoscored ratings - number of previous games taken into account
    plt.style.use('bmh')
    plt.subplot(6, 1, 3)

    '''
    number_of_previous_games = 1 
    chart_legend_varlist = []
    
    while number_of_previous_games < 8:
        chart_legend_varlist.append(str(number_of_previous_games))
        #print 'Importance of WS var=' + str(round(i_ws,1))
        chart_data, profit, home_bets, away_bets = database.SimulateLongTermBetting(league_name, initial_bank, stake, default_odds_border, default_ws_importance, default_homeadvantage, default_str_importance, default_str_mult, from_date, to_date, chart_data_bet_step, True, number_of_previous_games)#(bank, stake, diff_border, importance_ws, homeadvantage, chart_bets_step):

        data_length = len(chart_data)
        plt.plot(range(data_length), chart_data)
        number_of_previous_games += 3
        print "Games num: ", number_of_previous_games

    plt.plot([0,highest_data_length],[0,0], 'k')#black 0 line
    plt.plot([0,highest_data_length],[initial_bank,initial_bank], 'g', linestyle='dashed')#black bank line
    plt.axis([0,highest_data_length*1.01,stake*-axis_y_mult,(axis_y_mult * stake)+initial_bank])
    plt.ylabel('WS_gameNum')
    plt.legend(chart_legend_varlist, loc='upper left')
    '''

    
    #odds border
    plt.style.use('bmh')
    plt.subplot(6, 1, 4)

    odds_border = 0
    chart_legend_varlist = []
    while odds_border < 1.6:
        chart_legend_varlist.append(str(odds_border))
        #print 'Importance of WS var=' + str(round(i_ws,1))
        chart_data, profit, home_bets, away_bets = database.SimulateLongTermBetting(league_name, initial_bank, stake, odds_border, default_ws_importance, default_homeadvantage, default_str_importance, default_str_mult, from_date, to_date, chart_data_bet_step, False)#(bank, stake, diff_border, importance_ws, homeadvantage, chart_bets_step):
        data_length = len(chart_data)
        plt.plot(range(data_length), chart_data)
        odds_border += 0.4

    plt.plot([0,highest_data_length],[0,0], 'k')#black 0 line
    plt.plot([0,highest_data_length],[initial_bank,initial_bank], 'g', linestyle='dashed')#black bank line
    plt.axis([0,highest_data_length*1.01,stake*-axis_y_mult,(axis_y_mult * stake)+initial_bank])
    plt.ylabel('odds_diff')
    plt.legend(chart_legend_varlist, loc='upper left')


    #str importance
    plt.style.use('bmh')
    plt.subplot(6, 1, 5)

    i_str = 0.05
    chart_legend_varlist = []
    while i_str < 0.3:
        chart_legend_varlist.append(str(i_str))
        #print 'Importance of WS var=' + str(round(i_ws,1))
        chart_data, profit, home_bets, away_bets = database.SimulateLongTermBetting(league_name, initial_bank, stake, default_odds_border, default_ws_importance, default_homeadvantage, i_str, default_str_mult, from_date, to_date, chart_data_bet_step, False)#(bank, stake, diff_border, importance_ws, homeadvantage, chart_bets_step):
        data_length = len(chart_data)
        plt.plot(range(data_length), chart_data)
        i_str += 0.1

    plt.plot([0,highest_data_length],[0,0], 'k')#black 0 line
    plt.plot([0,highest_data_length],[initial_bank,initial_bank], 'g', linestyle='dashed')#black bank line
    plt.axis([0,highest_data_length*1.01,stake*-axis_y_mult,(axis_y_mult * stake)+initial_bank])
    plt.ylabel('STR_importance')
    plt.legend(chart_legend_varlist, loc='upper left')


    #str mult (weird but increases profit, probably increases home advantage in some 'smart' way) 
    plt.style.use('bmh')
    plt.subplot(6, 1, 6)

    str_mult = 0.2
    chart_legend_varlist = []
    while str_mult < 3.5:
        chart_legend_varlist.append(str(str_mult))
        #print 'Importance of WS var=' + str(round(i_ws,1))
        chart_data, profit, home_bets, away_bets = database.SimulateLongTermBetting(league_name, initial_bank, stake, default_odds_border, default_ws_importance, default_homeadvantage, default_str_importance, str_mult, from_date, to_date, chart_data_bet_step, False)#(bank, stake, diff_border, importance_ws, homeadvantage, chart_bets_step):
        data_length = len(chart_data)
        plt.plot(range(data_length), chart_data)
        str_mult += 1

    plt.plot([0,highest_data_length],[0,0], 'k')#black 0 line
    plt.plot([0,highest_data_length],[initial_bank,initial_bank], 'g', linestyle='dashed')#black bank line
    plt.axis([0,highest_data_length*1.01,stake*-axis_y_mult,(axis_y_mult * stake)+initial_bank])
    plt.ylabel('STR mult')
    plt.legend(chart_legend_varlist, loc='upper left')
    

    plt.suptitle(league_name)
    plt.show()


raise SystemExit


'''
BbMxH = Betbrain maximum home win odds
BbAvH = Betbrain average home win odds
BbMxD = Betbrain maximum draw odds
BbAvD = Betbrain average draw win odds
BbMxA = Betbrain maximum away win odds
BbAvA = Betbrain average away win odds
'''

'''
Notes for Football Data

All data is in csv format, ready for use within standard spreadsheet applications. Please note that some abbreviations are no longer in use (in particular odds from specific bookmakers no longer used) and refer to data collected in earlier seasons. For a current list of what bookmakers are included in the dataset please visit http://www.football-data.co.uk/matches.php

Key to results data:

Div = League Division
Date = Match Date (dd/mm/yy)
HomeTeam = Home Team
AwayTeam = Away Team
FTHG = Full Time Home Team Goals
FTAG = Full Time Away Team Goals
FTR = Full Time Result (H=Home Win, D=Draw, A=Away Win)
HTHG = Half Time Home Team Goals
HTAG = Half Time Away Team Goals
HTR = Half Time Result (H=Home Win, D=Draw, A=Away Win)

Match Statistics (where available)
Attendance = Crowd Attendance
Referee = Match Referee
HS = Home Team Shots
AS = Away Team Shots
HST = Home Team Shots on Target
AST = Away Team Shots on Target
HHW = Home Team Hit Woodwork
AHW = Away Team Hit Woodwork
HC = Home Team Corners
AC = Away Team Corners
HF = Home Team Fouls Committed
AF = Away Team Fouls Committed
HO = Home Team Offsides
AO = Away Team Offsides
HY = Home Team Yellow Cards
AY = Away Team Yellow Cards
HR = Home Team Red Cards
AR = Away Team Red Cards
HBP = Home Team Bookings Points (10 = yellow, 25 = red)
ABP = Away Team Bookings Points (10 = yellow, 25 = red)
B365H = Bet365 home win odds
B365D = Bet365 draw odds
B365A = Bet365 away win odds

Key to 1X2 (match) betting odds data:

B365H = Bet365 home win odds
B365D = Bet365 draw odds
B365A = Bet365 away win odds
BSH = Blue Square home win odds
BSD = Blue Square draw odds
BSA = Blue Square away win odds
BWH = Bet&Win home win odds
BWD = Bet&Win draw odds
BWA = Bet&Win away win odds
GBH = Gamebookers home win odds
GBD = Gamebookers draw odds
GBA = Gamebookers away win odds
IWH = Interwetten home win odds
IWD = Interwetten draw odds
IWA = Interwetten away win odds
LBH = Ladbrokes home win odds
LBD = Ladbrokes draw odds
LBA = Ladbrokes away win odds
PSH = Pinnacle home win odds
PSD = Pinnacle draw odds
PSA = Pinnacle away win odds
SOH = Sporting Odds home win odds
SOD = Sporting Odds draw odds
SOA = Sporting Odds away win odds
SBH = Sportingbet home win odds
SBD = Sportingbet draw odds
SBA = Sportingbet away win odds
SJH = Stan James home win odds
SJD = Stan James draw odds
SJA = Stan James away win odds
SYH = Stanleybet home win odds
SYD = Stanleybet draw odds
SYA = Stanleybet away win odds
VCH = VC Bet home win odds
VCD = VC Bet draw odds
VCA = VC Bet away win odds
WHH = William Hill home win odds
WHD = William Hill draw odds
WHA = William Hill away win odds

Bb1X2 = Number of BetBrain bookmakers used to calculate match odds averages and maximums
BbMxH = Betbrain maximum home win odds
BbAvH = Betbrain average home win odds
BbMxD = Betbrain maximum draw odds
BbAvD = Betbrain average draw win odds
BbMxA = Betbrain maximum away win odds
BbAvA = Betbrain average away win odds



Key to total goals betting odds:

BbOU = Number of BetBrain bookmakers used to calculate over/under 2.5 goals (total goals) averages and maximums
BbMx>2.5 = Betbrain maximum over 2.5 goals
BbAv>2.5 = Betbrain average over 2.5 goals
BbMx<2.5 = Betbrain maximum under 2.5 goals
BbAv<2.5 = Betbrain average under 2.5 goals

GB>2.5 = Gamebookers over 2.5 goals
GB<2.5 = Gamebookers under 2.5 goals
B365>2.5 = Bet365 over 2.5 goals
B365<2.5 = Bet365 under 2.5 goals


Key to Asian handicap betting odds:

BbAH = Number of BetBrain bookmakers used to Asian handicap averages and maximums
BbAHh = Betbrain size of handicap (home team)
BbMxAHH = Betbrain maximum Asian handicap home team odds
BbAvAHH = Betbrain average Asian handicap home team odds
BbMxAHA = Betbrain maximum Asian handicap away team odds
BbAvAHA = Betbrain average Asian handicap away team odds

GBAHH = Gamebookers Asian handicap home team odds
GBAHA = Gamebookers Asian handicap away team odds
GBAH = Gamebookers size of handicap (home team)
LBAHH = Ladbrokes Asian handicap home team odds
LBAHA = Ladbrokes Asian handicap away team odds
LBAH = Ladbrokes size of handicap (home team)
B365AHH = Bet365 Asian handicap home team odds
B365AHA = Bet365 Asian handicap away team odds
B365AH = Bet365 size of handicap (home team)


Closing odds (last odds before match starts)

PSCH = Pinnacle closing home win odds
PSCD = Pinnacle closing draw odds
PSCA = Pinnacle closing away win odds

Football-Data would like to acknowledge the following sources which have been utilised in the compilation of Football-Data's results and odds files.

Historical results:
International Soccer Server - http://sunsite.tut.fi/rec/riku/soccer.html
European Football - http://www.eurofootball.be/
RSSSF Archive - http://www.rsssf.com/

Current results (full time, half time)
TBWSport - http://www.tbwsport.com
Livescore- http://www.livescore.com

Match statistics
Sportinglife, ESPN Soccer, Bundesliga.de, Gazzetta.it and Football.fr

Bookmakers betting odds
Betbrain - http://www.betbrain.com
Betbase - http://www.betbase.info

Betting odds for weekend games are collected Friday afternoons, and on Tuesday afternoons for midweek games.

Additional match statistics (corners, shots, bookings, referee etc.) for the 2000/01 and 2001/02 seasons for the English, Scottish and German leagues were provided by Sports.com (now under new ownership and no longer available).
'''
