import time
import datetime

def GetDate(days_offset):
    date = str(datetime.date.today() + datetime.timedelta(days=days_offset))
    return date.split('-')[2] + '/' + date.split('-')[1] + '/' + date.split('-')[0][2:]

with open('bets log.txt','r') as f:
    betlines = [l[:len(l)-1] for l in f.readlines()]

while True:
    myinput = raw_input('Enter the day offset:')
    days = int(float(myinput)) if myinput != '' else 0
    
    for day in range(days+1):
        date = GetDate(day)
        print date
        for line in betlines:
            if date in line:
                myline = line.split(date+', ')[1]
                if "HOME" in line:
                    print str('>> '+myline.split(', ')[0]+' <<').upper().ljust(15) + ' vs    ' + myline.split(',')[1]
                elif "AWAY" in line:
                    print myline.split(', ')[0].ljust(15) + ' vs    ' + '>> '+myline.split(', ')[1].upper()+' <<'
        print ''
    print '\n'


raw_input('\n\nPress enter')
