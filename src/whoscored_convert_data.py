import re
import time


mykeys = ['Div','Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','HTHG','HTAG','HTR','Referee','HS','AS','HST','AST','HY','AY','HR','AR','B365H','B365D','B365A','HFR19','AFR19','STR', 'WS_HFORM', 'WS_AFORM']


#get all team names that aren't already saved in synonyms.txt
def UpdateSynonyms(league_name):
    with open(league_name + '/data.txt', 'r') as f:
        data = f.readlines()

    with open(league_name + '/synonyms.txt', 'r') as f:
        synonyms = f.readlines()

    teamnames = []
    for line in data:
        values = re.findall(re.compile('([0-9a-zA-Z <>.-/]*)[,]{0,1}'), line)
        if not values[2] in teamnames and not values[2] in re.findall(r'([0-9a-zA-Z <>.-/]*)[,]{0,1}',repr(synonyms)):
            teamnames.append(values[2])
        if not values[3] in teamnames and not values[3] in re.findall(r'([0-9a-zA-Z <>.-/]*)[,]{0,1}',repr(synonyms)):
            teamnames.append(values[3])
    for team in teamnames:
        print team
                  
#generate lines with whoscored ratings added to mydata
'''
concept:
whoscored dates are equal or earlier than my data
for every whoscored line get the date and find it in my data starting from the bottom
if the date matches check for home/away team synonyms
if there's no match at all print message
'''

def GetMyDataSynonym(teamname, synonyms):
    for s in synonyms:
        if teamname in s:
            values = s.split(",")
            return values[0]

def GenerateLines(league_name):
    print "Generating lines using data.txt and whoscored_ratings.txt for the: ", league_name, "..."
    print "The output is lines_to_replace.txt"
    with open(league_name + '/whoscored_ratings.txt', 'r') as f:
        ratings_data = f.readlines()

    with open(league_name + '/data.txt', 'r') as f:
        data = f.readlines()

    with open(league_name + '/synonyms.txt', 'r') as f:
        synonyms = f.readlines()

    lines_to_replace = []
    for r_line in ratings_data:
        values = r_line.split(",")[:-1]
        date, hometeam, awayteam, rating_home, rating_away = values[1], GetMyDataSynonym(values[2], synonyms), GetMyDataSynonym(values[3], synonyms), values[4], values[5]
        #print hometeam + ' ' + awayteam 
        reached_date = False
        found_line = False
        for line in reversed(data):
            values = line.split(",")[:-1]
            my_date, my_hometeam, my_awayteam = values[1], values[2], values[3]
            if my_date == date:
                reached_date = True
            if reached_date == True and found_line == False:
                if hometeam == my_hometeam and awayteam == my_awayteam:
                    #rewrite this line with ratings and add to a list "lines_to_replace"
                    newline = ''
                    for i,val in enumerate(values):
                        if i == mykeys.index('WS_HFORM'):
                            newline += rating_home + ','
                        elif i == mykeys.index('WS_AFORM'):
                            newline += rating_away + ','
                        else:
                            newline += val + ','
                    lines_to_replace.append(newline)
                    #print 'newline: ' + newline
                    found_line = True
                    
        if not reached_date:
            print 'DATE NOT REACHED', date, hometeam, awayteam

    print len(lines_to_replace)

    with open(league_name + '/lines_to_replace.txt', 'w+') as f:
        for line in lines_to_replace:
            f.write(line + '\n')
            
def ReplaceLines(league_name):
    print "Replacing lines using lines_to_replace.txt and data.txt for the: ", league_name, "..."
    print "The output is data_with_whoscored.txt"
    #replace lines
    with open(league_name + '/lines_to_replace.txt', 'r') as f:
        lines_to_replace = f.readlines()

    with open(league_name + '/data.txt', 'r') as f:
        data = f.readlines()

    newdata = []
    for i,line in enumerate(data):
        values = line.split(",")
        my_date, my_hometeam, my_awayteam = values[1], values[2], values[3]
        found_line_to_replace = False
        for r_line in lines_to_replace:
            values = r_line.split(",")
            date, hometeam, awayteam = values[1], values[2], values[3]
            if my_date == date and my_hometeam == hometeam and my_awayteam == awayteam:
                newline = r_line
                found_line_to_replace = True
        if found_line_to_replace:
            newdata.append(newline)
            #print newline
        else:
            newdata.append(line)
                   

    print len(newdata)
    print len(data)

    with open(league_name + '/data_with_whoscored.txt', 'w+') as f:
        for line in newdata:
            f.write(line)    


league = "Serie A"#"Bundesliga"#"Premier League"
#UpdateSynonyms(league)
#GenerateLines(league)
ReplaceLines(league)
    

#check length
'''
with open('count_check.txt', 'r') as f:
    data = f.readlines()

print len(data)
'''
    



