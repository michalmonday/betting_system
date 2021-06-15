from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup as BS

league_name = "Championship"#"Serie A"#"Bundesliga"#"Premier League"

#with open(league_name + "/season_links.txt", "r") as f:
#    season_links = [l.replace("\r","").replace("\n","") for l in f.readlines()]
    
br = webdriver.Chrome()
 
with open(league_name + '/whoscored_match_links_left.txt', 'r') as f:
    links = f.readlines()

br.set_page_load_timeout(60)
br.set_script_timeout(60)

ratings_data = []
match_ids = []

def ConvertDate(date):
    months = {'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12', 'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07'}
    day = re.findall(r'\s\w{3}\s(\d+?)\s\d{4}',date)[0]
    if len(day)==1:
        day = '0' + day
    month = months[re.findall(r'\s(\w{3})\s\d+?\s\d{4}',date)[0]]
    year = re.findall(r'\s\w{3}\s\d+?\s(\d{4})',date)[0][2:]
    return date.split(",")[0] + "," +day + '/' + month + '/' + year


for i,url in enumerate(links):        
    loaded = False
    while(loaded == False):
        try:
            br.get(url)
            htmltext = br.page_source
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
            homerating = ratings[0].text
            awayrating = ratings[1].text

            associated_date = ConvertDate(re.findall(re.compile('<optgroup\slabel="(.+?)">'),htmltext)[0])
            #<optgroup label="Sat, Aug 14 2010">
        except Exception as e:
            #print "ERROR: Couldn't load page, trying again..."
            time.sleep(2)
            br.quit()
            br = webdriver.Chrome()
            with open(league_name + "/debug.txt", "a+")as f:
                f.write(str(e) + "\n\n" + url + "\n\n\n")
        else:
            loaded = True

    outputLine = ",".join([associated_date,hometeam,awayteam,homerating,awayrating]) + ","
    print outputLine, url.split("/")[-2:][0]
    ratings_data.append(outputLine)
    with open(league_name + "/whoscored_ratings_appended.txt", "a+") as f:
        f.write(outputLine + "\n")
        

f = open(league_name + "/whoscored_ratings.txt", 'w')
for d in ratings_data:
    f.write("%s\n" % d)
f.close()

br.close()


    
