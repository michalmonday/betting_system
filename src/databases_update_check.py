import requests
import time
import re

league_names = ['England','Serie A','La Liga','Bundesliga', 'Ligue 1', 'Eredivisie','Portuguese','Super Lig']
league_update_symbols = {
    'England':'englandm',
    'Serie A':'italym',
    'La Liga':'spainm',
    'Bundesliga':'germanym',
    'Ligue 1':'francem',
    'Eredivisie':'netherlandsm',
    'Portuguese':'portugalm',
    'Super Lig':'tyrkeym'
    }

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

today_date = time.strftime("%d/%m/%y")

c = requests.Session()
for league_name in league_names:
    page = c.get('http://www.football-data.co.uk/'+league_update_symbols[league_name]+'.php').content
   
    date = re.findall(r'<I>Last\supdated:(.+?)</I>',repr(page))[0].split('t')[1]
    print league_name
    print date + '\n'
    #<I>Last updated: 	18/09/16</I>

raw_input('\n\nPress enter')


