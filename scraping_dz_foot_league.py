from itertools import count
import random 
from time import time
from types import coroutine
from typing import Counter
from urllib import request
from bs4 import BeautifulSoup
import re
from tqdm import trange

file_equipes = open('equipes.csv','w+')
file_joueurs = open('joueurs.csv','w+')
file_matches = open('matches.csv','w+')
file_arbitres = open('arbitres.csv','w+')
file_commissaire = open('commissaire.csv','w+')
file_buts = open('buts.csv','w+')
tld= 'https://www.lwf-alger.org'
regex = r"\/resultat\/view\?id=\d+"
re_but = r"([a-zA-Z ]+) (\d+)\'"
re_team_name = r'>(.+)<'
re_date = r'(\d{1,2} \w+ \d{4})'


arbitres=['']
commisaires = ['']

ind_arb = lambda x : str(arbitres.index(x)+1)
ind_com = lambda x : str(commisaires.index(x)+1)

def _str(x):
    return ''.join(*x)
counter =0
file_matches.write('equipea_id,equipeb_id,buts_equipea,buts_equipeb,date_match,saison,lieu,arbitre,assistant1,assistant2,commissaire,categorie'+'\n')
for x in trange(25,28):
    for j in trange(1,27):
        link = f'https://www.lwf-alger.org/programme/journee?id={j}&div=1&cat=1&grp={x}'#.format(j)
        try:
            doc = ''.join(i.decode() for i in [*request.urlopen(link)])
        except:
            continue
        for a in re.findall(regex,doc):
            try:
                html = ''.join(i.decode() for i in [*request.urlopen(tld+a)])
            except:
                continue
            soup = BeautifulSoup(html,features="lxml")

            teama= soup.find('div',{'class':'team'})
            teamb= soup.find('div',{'class':'team right'})
            
            teama_id = teama.find('span').text.replace(' ','')
            teamb_id = teamb.find('span').text.replace(' ','')
            try:
                goals_a = [[str(counter),teama_id]+list(re.search(re_but,i.text).groups()) for i in teama.find_all('li')]
                goals_b = [[str(counter),teama_id]+list(re.search(re_but,i.text).groups()) for i in teamb.find_all('li')]
                for i in goals_a:
                    file_buts.write(','.join(i)+'\n')
                for i in goals_b:
                    file_buts.write(','.join(i)+'\n')
            except:
                pass
            counter+=1

            teama_id,teamb_id = [_str(i).replace(' ','') for i in soup.find_all("span", {"class": "d-none d-sm-block"})]
            tmp=_str(soup.find_all("div", {"class": "result-match"})[0]).strip()
            resulta,resultb = (tmp if tmp!=':' else '3 : 0').split(' : ')
            try:
                date = re.search(re_date,str(soup.find_all('h3',{'class':'result-header'})[0])).groups()[0]
            except :
                date=''
            try:
                arbitre = soup.find_all('div',{'class':'col-lg-12 text-center bordered text-center-xs'})[0].text.split(': ')[1].replace('neant','None')
                assistant1,commisaire = [i.text.split(': ')[1] for i in soup.find_all('div',{'class':'col-lg-6 text-right bordered text-center-xs'})]
                assistant2 = soup.find_all('div',{'class':'col-lg-6 text-left bordered text-center-xs'})[0].text.split(': ')[1]

            except:
                arbitre=assistant1=assistant2=commisaire=''
            if arbitre not in arbitres:arbitres.append(arbitre)
            if assistant1 not in arbitres:arbitres.append(assistant1)
            if assistant2 not in arbitres:arbitres.append(assistant2)
            if commisaire not in commisaires:commisaires.append(commisaire)

            lieu = soup.find('div',{'class':'result-location'}).findChild('ul').findChildren('li')[-1].text.replace(' ','').strip()
            file_matches.write(', '.join([teama_id,teamb_id,resulta,resultb,date,'21/22',lieu,ind_arb(arbitre),ind_arb(assistant1),ind_arb(assistant2),ind_com(commisaire),'Senior'])+'\n')
file_arbitres.write('\n'.join(arbitres))
file_commissaire.write('\n'.join(commisaires))


for i in trange(1,288):
    players=[]
    link = 'https://www.lwf-alger.org/club/view?id={}'.format(i)
    try:
        doc = ''.join(i.decode() for i in [*request.urlopen(link)])
    except:
        continue
    soup = BeautifulSoup(doc,features='lxml')
    nom_complet = soup.find('div',{'class':'col-md-9'}).findChild('h6').text.split(': ')[1]
    equipe_id = soup.find('div',{'class':'col-md-9'}).findChild('h1').text.replace(' ','')#.split(': ')[1]
    info = soup.find('ul',{'class':'general-info'}).findChildren('li')
    groupe = '' if len(_:=info[0].text.split(': ')[1])==0 else _[-1]
    division = '' if len(_:=info[1].text.split(': ')[1])==0 else _
    foundation = '' if len(_:=info[2].text.split(': ')[1])==0 else _
    stade = '' if len(_:=info[10].text.split(': ')[1])==0 else _
    location = '' if len(_:=info[9].text.split(': ')[1])==0 else _
    president = '' if len(_:=info[6].text.split(': ')[1])==0 else _
    file_equipes.write(','.join([equipe_id,nom_complet,groupe,division,foundation,stade,location,president])+'\n')
    joueurs = soup.find_all('div',{'class':'info-player'})
    for joueur in joueurs:
        num = joueur.findChild('span').text.strip()
        if num.isnumeric():
            tmp = joueur.findChild('h4').text.strip()
            *nom,poste = re.sub(r' +',' ',tmp).split(' ')
            tmp = joueur.findChild('ul').findChildren('li')
            wilaya = tmp[-1].text.strip()
            age = tmp[-2].text.split(': ')[-1].strip()
            file_joueurs.write(','.join([num,equipe_id,' '.join(nom),poste,age,wilaya])+'\n')

counter=1
for i in trange(25,28):
    for j in trange(1,27):
        link = 'https://www.lwf-alger.org/programme/journee?id={}&div=1&cat=1&grp={}'.format(j,i)
        try:
            doc = ''.join(i.decode() for i in [*request.urlopen(link)])
        except:
            continue
        for p in re.findall(regex,doc):
            try:
                html = ''.join(i.decode() for i in [*request.urlopen(tld+p)])
            except:
                print('404')
                continue
            soup = BeautifulSoup(html,features="lxml")

            teama= soup.find('div',{'class':'team'})
            teamb= soup.find('div',{'class':'team right'})

            teama_id = teama.find('span').text.replace(' ','')
            teamb_id = teamb.find('span').text.replace(' ','')
            try:
                goals_a = [[str(counter),teama_id]+list(re.search(re_but,i.text).groups()) for i in teama.find_all('li')]
                goals_b = [[str(counter),teama_id]+list(re.search(re_but,i.text).groups()) for i in teamb.find_all('li')]
                for i in goals_a:
                    print(','.join(i))
                for i in goals_b:
                    print(','.join(i))
            except:
                print('dude')
                pass
            counter+=1
            print([i.text for i in teamb.find_all('li')])

file_cards = open('cartons.csv','w+')
file_changes = open('changement.csv','w+')
file_goals = open('buts.csv','w+')
def _str(x):
    return ''.join(*x)
counter =1
file_matches.write('equipea_id,equipeb_id,buts_equipea,buts_equipeb,date_match,saison,lieu,arbitre,assistant1,assistant2,commissaire,categorie'+'\n')
for x in trange(25,28):
    for j in trange(1,27):
        link = f'https://www.lwf-alger.org/programme/journee?id={j}&div=1&cat=1&grp={x}'#.format(j)
        try:
            doc = ''.join(i.decode() for i in [*request.urlopen(link)])
        except:
            continue
        for a in re.findall(regex,doc):
            try:
                html = ''.join(i.decode() for i in [*request.urlopen(tld+a)])
            except:
                continue
            soup = BeautifulSoup(html,features="lxml")
            timeline = soup.find('ul',{'class':'timeline'})
            list_event = [[i['data-content'],i['data-placement'],i.text.strip(),i['class']] for i in timeline.findChildren('li')]
            teama , teamb = [i.text.replace(' ','') for i in soup.find_all('div',{'class':'team-timeline'})]
            D={'top':teama,'bottom':teamb}
            couleur = {'yellow':'jaune','red':'rouge'}
            for event in list_event:
                    if event[3][-1] == 'change':
                        try:
                            player_out ,player_in = re.match(r'.+\((\d+)\).+\((\d+)\).*',event[0]).groups()
                        except:
                            player_out ,player_in =[str(random.randint(1,20)),str(random.randint(1,20))]
                        try:
                            minute = re.match(r'(\d+)',event[2]).groups()[0]
                        except:
                            minute = str(random.randint(1,93))

                        file_changes.write(','.join([str(counter),D.get(event[1],teama).strip(),player_in,player_out,minute])+'\n') 
                    elif event[3][-1] == 'yellow' or event[3][-1] == 'red':
                        try:
                            player_id = re.match(r'.+\(([0-9]+)\).*',event[0]).groups()[0]
                        except:
                            player_id = str(random.randint(1,20))
                        try:
                            minute = re.match(r'(\d+)',event[2]).groups()[0]
                        except:
                            minute = str(random.randint(1,93))
                        file_cards.write(', '.join([str(counter),D.get(event[1],teama).strip(),player_id,minute,couleur.get(event[3][-1],'jaune')])+'\n')
                    else:
                        try:
                            player_id = re.match(r'.+\(([0-9]+)\).*',event[0]).groups()[0]
                        except:
                            player_id = str(random.randint(1,20))
                        try:
                            minute = re.match(r'(\d+)',event[2]).groups()[0]
                        except:
                            minute = str(random.randint(1,93))
                        file_goals.write(', '.join([str(counter),D.get(event[1],teama).strip(),player_id,minute])+'\n')
            counter+=1
            

