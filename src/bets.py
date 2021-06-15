import re
import time
import random
import requests

#import historic_data_analyse
#database = historic_data_analyse.Database()
#database.CreateNewDatabase('mynewdatabase.txt')
#raise SystemExit

max_synonyms = 7

def perc_odd(odd):#string to float
    return 1/float(odd)

def GetSynonym(name, index):
    s = open('synonyms.txt','r')
    s_lines = s.readlines()
    ret = "No synonym"
    for line in s_lines:
        if name in line:
            synonyms = re.findall(re.compile('([a-zA-Z ]+),'), line) 
            try:
                ret = synonyms[index]
            except:
                pass
            else:
                break
    s.close()
    return ret

def GetGenRatings(myTeams):#http://www.soccer-rating.com/England/
    c = requests.Session()
    text = c.get('http://www.soccer-rating.com/England/').content.decode("utf-8")    
    gr_teams = re.findall(re.compile('">(\w+\s*\w*\s*\w*\s*)<.a><.td><td>UK1<.td><td><img src="..flags.UK.gif"\swidth="[0-9]{0,3}"\sheight="[0-9]{0,3}"><.td><td>\d{1,4}[.]\d{0,4}<.td>'),text)
    #">Manchester City</a></td><td>UK1</td><td><img src="./flags/UK.gif" width="28" height="19"></td><td>2340.07</td>
    #">Manchester United</a></td><td>UK1</td><td><img src="./flags/UK.gif" width="28" height="19"></td><td>2292.89</td></tr>
    ratings = re.findall(re.compile('">\w+\s*\w*\s*\w*\s*<.a><.td><td>UK1<.td><td><img src="..flags.UK.gif"\swidth="[0-9]{0,3}"\sheight="[0-9]{0,3}"><.td><td>(\d{1,4}[.]\d{0,4})<.td>'),text)
    ratinglist = []
    ratingindex = 0
    if len(gr_teams) != len(ratings):
        print "The length of scrapped ratings is not equal to scrapped names. Names=" + str(len(gr_teams)) + " ratings=" + str(len(ratings))
        return None
    i = 0   
    while i<len(myTeams):
        try:
            ratingindex = gr_teams.index(myTeams[i]) #form index appropriate for current myTeams[i]
        except:
            j = 0
            while j<max_synonyms:
                try:
                    ratingindex = gr_teams.index(GetSynonym(myTeams[i],j))          
                except:
                    ratingindex = 999 #not found
                    pass
                else:
                    #print 'found synonym: ' + GetSynonym(myTeams[i],j)
                    j = max_synonyms
                j+=1
        finally:
            if ratingindex != 999:                
                ratinglist.append(ratings[ratingindex])
            else:
                print "GenRatings SYNONYM NOT FOUND for:" + myTeams[i]
        i+=1            
    return ratinglist
    
def GetFormData(myTeams):#whoscored.com
    c = requests.Session()
    baseurl = "http://api.datascraping.co"
    resturl = "/v1/output/31f699901e?offset=0&limit=1000"
    h = {
        'x-datascraping-api-id': "PZ0P2BYEXW",
        'x-datascraping-api-key': "17fd7647320e573c9407d97571f224e2",
        'content-type': "csv"
        }
    text = c.get(baseurl+resturl, headers = h).content.decode("utf-8")
    ws_teams = re.findall(re.compile('TeamsStats":"(\w+\s*\w*\s*\w*\s*)"'),text)
    forms = re.findall(re.compile('TeamsStats":"(\d[.]\d{2})"'),text)
    #print str(len(ws_teams)) + " " + str(len(forms)) 
    formlist = []
    i = 0
    while i<len(myTeams):
        try:
            formindex = ws_teams.index(myTeams[i]) #form index appropriate for current myTeams[i]
        except:
            j = 0
            while j<max_synonyms:
                try:
                    formindex = ws_teams.index(GetSynonym(myTeams[i],j))
                except:
                    formindex = 999
                    pass
                else:
                    #print 'found synonym: ' + GetSynonym(myTeams[i],j)
                    j = max_synonyms
                j+=1
        finally:
            if formindex != 999:
                formlist.append(forms[formindex])
            else:
                print "GetForm SYNONYM NOT FOUND for:" + myTeams[i]    
        i+=1            
    return formlist

def xor0_1(i):
    if i == 1:
        return 0
    else:
        return 1
    
def Sort_odds(odds):
    odds_1 = []
    odds_x = []
    odds_2 = []
    i = 0
    for o in odds:
        i+=1
        if i == 1:
            odds_1.append(o)
        elif i == 2:
            odds_x.append(o)
        elif i == 3:
            odds_2.append(o)
            i = 0
    return odds_1, odds_x, odds_2
    

def Sort_teams(teams):
    hometeams = []
    awayteams = []
    b = 0
    for t in teams:
        b = xor0_1(b)
        if b == 1:
            hometeams.append(t)
        else:
            awayteams.append(t)
    return hometeams, awayteams

def LengthCheck(h, a, o_1, o_x, o_2):
    if h != a:
        print str(h) + " " + str(a) + " home and away teams number don't match"
    if o_1 != o_x or o_1 != o_2 or o_x != o_2:
        print str(o_1) + " " + str(o_x) + " " + str(o_2) + " odds types number don't match"        
    return None

c = requests.Session()
url='http://www.oddschecker.com/football/english/premier-league'
oddspage = c.get(url).content.decode("utf-8")

odds = re.findall(re.compile('data-best-odds="([0-9]{1,3}[.]{0,1}[0-9]{0,3})"'),oddspage)
#data-best-odds="3.4"
oddspage = oddspage.replace('<span class="fixtures-bet-name">Draw</span>','<span class="fixtures-bet-name"></span>') #needed to extract the team names
teams = re.findall(re.compile('<span class="fixtures-bet-name">(.{1,30})</span>'),oddspage)

odds_1, odds_x, odds_2 = Sort_odds(odds)
hometeams, awayteams = Sort_teams(teams)

LengthCheck(len(hometeams),len(awayteams), len(odds_1), len(odds_x), len(odds_2))

#homeforms = GetFormData(hometeams)
#awayforms = GetFormData(awayteams)

#home_genratings = GetGenRatings(hometeams) #http://www.soccer-rating.com/England/
#away_genratings = GetGenRatings(awayteams)

i = 0
while i<len(hometeams):
    #print hometeams[i] + " " + home_genratings[i] + " vs " + awayteams[i] + " " + away_genratings[i]
    print hometeams[i] + " vs " + awayteams[i]
    print odds_1[i]
    print odds_x[i]
    print odds_2[i]
    i+=1

'''
margin calculation
i = 0
>>> while i<len(odds_1):
	print str(float(odds_1[i])) + " " + str((1/float(odds_1[i]))+(1/float(odds_2[i]))) + " " + str(float(odds_2[i]))
	i+=1
'''

#values so far... hometeam, awayteam, ht_form, at_form, odds_1, odds_x, odds_2






#matchlinks_odds = re.findall(re.compile(''),oddspage)






'''
class="match-on "><td class="time"><p>15:00</p></td>
<td data-bid="18189217604" data-best-odds="2.3" data-track="&amp;lid=card&amp;lpos=basket-add
" title="Add Bournemouth to betslip"><p><span title="Add Bournemouth to betslip" class="add-to-bet-basket" data-name="Bournemouth"></span>
<span class="fixtures-bet-name">Bournemouth</span>
<span class="odds"> (13/10)</span></p></td>
<td data-bid="18189217595" data-best-odds="3.3" data-track="&amp;lid=card&amp;lpos=basket-add
" title="Add Draw to betslip"><p><span title="Add Draw to betslip" class="add-to-bet-basket" data-name="Draw"></span>
<span class="fixtures-bet-name">Draw</span><span class="odds"> (23/10)</span></p></td>
<td data-bid="18189217589" data-best-odds="3.4" data-track="&amp;lid=card&amp;lpos=basket-add
" title="Add West Brom to betslip"><p><span title="Add West Brom to betslip" class="add-to-bet-basket" data-name="West Brom"></span>
<span class="fixtures-bet-name">West Brom</span><span class="odds"> (12/5)</span></p></td>
<td class="betting"><a class="button btn-1-small" title="View all Bournemouth v West Brom odds" href="/football/english/premier-league/bournemouth-v-west-brom/winner">All Odds<span class="arrow"></span>
</a></td></tr><tr data-mid="2787200945"



http://www.oddschecker.com/football/english/premier-league/winner
#data-best-dig="1.2"

<select class="quick-switch other-matches"><option value="">Match select...</option>
<option value="/football/english/premier-league/west-ham-v-bournemouth/winner">West Ham v Bournemouth</option>
<option value="/football/english/premier-league/tottenham-v-liverpool/winner">Tottenham v Liverpool</option>
<option value="/football/english/premier-league/chelsea-v-burnley/winner">Chelsea v Burnley</option>
<option value="/football/english/premier-league/crystal-palace-v-bournemouth/winner">Crystal Palace v Bournemouth</option>
<option value="/football/english/premier-league/everton-v-stoke/winner">Everton v Stoke</option>
<option value="/football/english/premier-league/leicester-v-swansea/winner">Leicester v Swansea</option>
<option value="/football/english/premier-league/southampton-v-sunderland/winner">Southampton v Sunderland</option>
<option value="/football/english/premier-league/watford-v-arsenal/winner">Watford v Arsenal</option>
<option value="/football/english/premier-league/hull-v-man-utd/winner">Hull v Man Utd</option>
<option value="/football/english/premier-league/west-brom-v-middlesbrough/winner">West Brom v Middlesbrough</option>
<option value="/football/english/premier-league/man-city-v-west-ham/winner">Man City v West Ham</option>
<option value="/football/english/premier-league/man-utd-v-man-city/winner">Man Utd v Man City</option>
<option value="/football/english/premier-league/arsenal-v-southampton/winner">Arsenal v Southampton</option>
<option value="/football/english/premier-league/bournemouth-v-west-brom/winner">Bournemouth v West Brom</option>
<option value="/football/english/premier-league/burnley-v-hull/winner">Burnley v Hull</option>
<option value="/football/english/premier-league/middlesbrough-v-crystal-palace/winner">Middlesbrough v Crystal Palace</option>
<option value="/football/english/premier-league/stoke-v-tottenham/winner">Stoke v Tottenham</option>
<option value="/football/english/premier-league/west-ham-v-watford/winner">West Ham v Watford</option>
<option value="/football/english/premier-league/liverpool-v-leicester/winner">Liverpool v Leicester</option>
<option value="/football/english/premier-league/swansea-v-chelsea/winner">Swansea v Chelsea</option>
<option value="/football/english/premier-league/sunderland-v-everton/winner">Sunderland v Everton</option>
<option value=""></option>
<option value="/football/english/premier-league/winner">Premier League</option></select>
'''
'''
j = json.loads()
j = j["result"]
leagues = []
team = {}
form = {}
i = 0
for x in j:
    print x["TeamsStats"]
    if "Team Statistics" in x["TeamsStats"]:
        leagues.append(x["TeamsStats"])        
    else:
        teamsdata.append(x["TeamsStats"])
        i+=1
print league
print teamsdata
'''
