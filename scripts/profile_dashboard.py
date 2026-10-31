"""Generate original SVG panels from GitHub data. Standard library only."""
from pathlib import Path
from xml.sax.saxutils import escape
from datetime import datetime,timezone,timedelta
import json,urllib.request,os,sys,calendar
R=Path(__file__).resolve().parents[1];A=R/'assets';D=R/'data'
BG='#0d0d15';WHITE='#f6eef3';MUTED='#b5a7b9';ROSE='#e7a1bf';TEAL='#88d9ca';LINE='#392b40'
def text(x,y,s,size=24,c=WHITE,bold=False):return f'<text x="{x}" y="{y}" fill="{c}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}">{escape(str(s))}</text>'
def rect(x,y,w,h,c,rx=0,stroke=None):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{c}"'+(f' stroke="{stroke}"' if stroke else '')+'/>'
def save(name,w,h,body,title):
 (A/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>{body}</svg>')
def render(data):
 stamp=data['updated'][:10];stats=[(data['followers'],'FOLLOWERS'),(len(data['pins']),'PINNED REPOS'),(sum(p['stars'] for p in data['pins']),'STARS ON PINNED'),(data['total'],'PUBLIC CONTRIBUTIONS')]
 for mobile in (False,True):
  w,h=(680,420) if mobile else (1200,265);b=rect(0,0,w,h,BG,20,LINE)
  b+=text(30,33,'GITHUB / PUBLIC ACTIVITY',14,ROSE,True)
  colors=['#e35990','#55b7ed','#e4bd60','#67dac4']
  icons=['M-13 13v-6c0-9 26-9 26 0v6M0-6a7 7 0 1 0 0-14 7 7 0 0 0 0 14M-18-3a5 5 0 1 0 0-10M18-3a5 5 0 1 0 0-10','M-10-17h20v34L0 10l-10 7Z','M0-19 6-6 20-4 10 6 13 20 0 13-13 20-10 6-20-4-6-6Z','M-9-15v30M-9 0h10q12 0 12-12M-9-15a4 4 0 1 0 0-.1M-9 15a4 4 0 1 0 0-.1M13-16a4 4 0 1 0 0-.1']
  for j,(n,label) in enumerate(stats):
   cw=300 if mobile else 272;x=30+(j%2)*320 if mobile else 30+j*293;y=54+(j//2)*161 if mobile else 57
   b+=rect(x,y,cw,143,'#13121d',12,LINE)
   b+=f'<g transform="translate({x+cw/2},{y+29})" fill="none" stroke="{colors[j]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{icons[j]}"/></g>'
   b+=f'<text x="{x+cw/2}" y="{y+92}" text-anchor="middle" fill="{WHITE}" font-family="Georgia,serif" font-size="46">{n:,}</text>'
   names=['Followers','Pinned repos','Stars on pinned','Public contributions']
   b+=f'<text x="{x+cw/2}" y="{y+125}" text-anchor="middle" fill="{MUTED}" font-family="Georgia,serif" font-size="21">{names[j]}</text>'
  b+=text(30,h-17,'GITHUB DATA / '+stamp,13,ROSE)
  save('stats-mobile-cinematic.svg' if mobile else 'stats-cinematic.svg',w,h,b,'Genuine GitHub snapshot: '+', '.join(str(n)+' '+l.lower() for n,l in stats)+'. Updated '+stamp)
 # Individual pinned cards stay separate and clickable in a 3-column desktop table.
 descriptions={'Jameel-Fabrics-Kunjah':('JAMEEL FABRICS','Retail ERP','Business operations,','connected to the storefront.'),'Jameel-Fabrics-Online-Website':('JAMEEL FABRICS','Customer website','A digital storefront','for a real clothing business.'),'The-H-Portfolio-Template':('THE H PORTFOLIO','Community template','A cinematic starter kit','to make your own.')}
 for i,p in enumerate(data['pins']):
  title,role,l1,l2=descriptions.get(p['name'],(p['name'],'Repository','',''))
  b=rect(0,0,390,280,BG,17,LINE)+text(25,40,'PINNED / 0'+str(i+1),14,ROSE)+text(25,91,title,27,WHITE,True)+text(25,127,role,20,TEAL)+text(25,171,l1,18,MUTED)+text(25,197,l2,18,MUTED)
  b+=text(25,250,p['language'] or 'Code',16,ROSE)+text(210,250,'★ '+str(p['stars'])+'   Forks '+str(p['forks']),16,MUTED)
  save(f'pin-{i+1}-v3.svg',390,280,b,p['name']+': '+role+'. '+str(p['stars'])+' stars, '+str(p['forks'])+' forks. Updated '+stamp)
 # Responsive pinned overview: readable cards instead of a squeezed mobile table.
 cards=[(A/f'pin-{i+1}-v3.svg').read_text() for i in range(len(data['pins']))]
 for mobile in (False,True):
  w,h=(680,1510) if mobile else (1200,280);body=''
  for i,card in enumerate(cards):
   if mobile:card=card.replace('width="390" height="280"',f'x="0" y="{i*505}" width="680" height="488"',1)
   else:card=card.replace('width="390" height="280"',f'x="{i*405}" y="0" width="390" height="280"',1)
   body+=card
  save('pins-mobile-v3.svg' if mobile else 'pins-v3.svg',w,h,body,'Pinned repositories: retail ERP, customer website and community portfolio template.')
 # A genuine year calendar. Future days are absent, not filled with invented activity.
 days=sorted(data['days'],key=lambda x:x['date']);start=datetime.fromisoformat(days[0]['date']).date();start-=timedelta(days=(start.weekday()+1)%7)
 b=rect(0,0,1200,460,BG,20,LINE)+text(35,49,'PUBLIC CONTRIBUTION ACTIVITY',19,ROSE,True)+text(35,112,f'{data["total"]:,} public contributions',47,WHITE,True)+text(35,150,'Public activity across the past 12 months.',23,MUTED)
 palette=['#211c2b','#593047','#864365','#bb688d','#edb0cc'];months={}
 for day in days:
  dt=datetime.fromisoformat(day['date']).date();col=(dt-start).days//7;row=(dt.weekday()+1)%7;level=min(4,max(0,int(day.get('level',min(4,day['count'])))))
  b+=rect(38+col*21,205+row*21,17,17,palette[level],3)
  if dt.day<=7 and row==0:months[col]=dt.strftime('%b')
 for col,m in months.items():b+=text(38+col*21,190,m,14,MUTED)
 b+=text(36,404,'PAST 12 MONTHS',15,TEAL)+text(36,433,'SOURCE: GITHUB / UPDATED '+stamp,14,MUTED)+text(927,409,'LESS',13,MUTED)
 for k,c in enumerate(palette):b+=rect(975+k*24,395,17,17,c,3)
 save('activity-v3.svg',1200,460,b,'Public GitHub contribution calendar: '+str(data['total'])+' contributions in the past year. Updated '+stamp)
 # Six monthly totals, calculated from the same real calendar.
 monthly={}
 for day in days:monthly[day['date'][:7]]=monthly.get(day['date'][:7],0)+day['count']
 months=sorted(monthly)[-6:];mx=max([monthly[m] for m in months]+[1]);b=rect(0,0,1200,310,BG,20,LINE)+text(35,47,'MONTH BY MONTH',19,ROSE,True)+text(35,83,'Public contributions recorded by GitHub',21,MUTED)
 for j,m in enumerate(months):
  x=37+j*195;bh=100*monthly[m]/mx;b+=rect(x,122,155,100,'#211c2b',7)+rect(x,222-bh,155,bh,'#9d5279',7)+text(x,259,datetime.strptime(m,'%Y-%m').strftime('%b %Y'),18,MUTED)+text(x+105,118,monthly[m],21,TEAL,True)
 save('monthly-v3.svg',1200,310,b,'Monthly contributions: '+', '.join(m+': '+str(monthly[m]) for m in months)+'. Updated '+stamp)

def fetch():
 token=os.environ['GH_TOKEN'];login=os.environ.get('PROFILE_LOGIN','Hamza-Muhammadi')
 query='''query($login:String!){user(login:$login){followers{totalCount} pinnedItems(first:6,types:REPOSITORY){nodes{... on Repository{name stargazerCount forkCount primaryLanguage{name}}}} contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}'''
 req=urllib.request.Request('https://api.github.com/graphql',data=json.dumps({'query':query,'variables':{'login':login}}).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','User-Agent':'Hamza-Profile-Dashboard'})
 with urllib.request.urlopen(req,timeout=45) as r:payload=json.load(r)
 if payload.get('errors'):raise RuntimeError('GitHub query failed; previous panels retained.')
 u=payload['data']['user'];cal=u['contributionsCollection']['contributionCalendar'];levels={'NONE':0,'FIRST_QUARTILE':1,'SECOND_QUARTILE':2,'THIRD_QUARTILE':3,'FOURTH_QUARTILE':4}
 known={'Jameel-Fabrics-Kunjah','Jameel-Fabrics-Online-Website','The-H-Portfolio-Template'}
 pins=[{'name':p['name'],'stars':p['stargazerCount'],'forks':p['forkCount'],'language':(p.get('primaryLanguage') or {}).get('name')} for p in u['pinnedItems']['nodes'] if p['name'] in known]
 if len(pins)!=3:raise RuntimeError('Pinned set changed; review card layout before refreshing.')
 order=['Jameel-Fabrics-Kunjah','Jameel-Fabrics-Online-Website','The-H-Portfolio-Template'];pins.sort(key=lambda p:order.index(p['name']))
 return {'updated':datetime.now(timezone.utc).strftime('%Y-%m-%d'),'followers':u['followers']['totalCount'],'pins':pins,'total':cal['totalContributions'],'days':[{'date':d['date'],'count':d['contributionCount'],'level':levels[d['contributionLevel']]} for w in cal['weeks'] for d in w['contributionDays']]}
if __name__=='__main__':
 p=D/'profile-dashboard.json';data=json.loads(p.read_text()) if '--from-snapshot' in sys.argv else fetch();render(data)
 if '--from-snapshot' not in sys.argv:p.write_text(json.dumps(data,indent=2)+'\n')
 print('Profile panels rendered from GitHub data.')
