# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 23:08:07 2013
Project	:IMESymGrabber
Version	:0.0.3
@author	:macrobull

"""
__version__="0.0.3"

import sys
import codecs
import copy
import urllib,urllib2
#from lcs import *

from symbolConvert import *


reload(sys)
sys.setdefaultencoding('utf-8')

MIN_LEN=5
MAX_LEN=20
MAX_LEN_RATIO=1.5
SELECTION_THRES=0.7
EXT_COEFF=2.0
BLANK_CHAR_SET=('\0','\t',' ','\r','\n','　',u'\ufeff')
SPLIT_CHAR_SET=('\t','\n','\r','\0')

H_THRES=0.20
GAMMA=1.5

if len(sys.argv)<4:
	print('IMESymGrabber.py Template(txt/xml) Source(txt/xml/-URL-) Dest(txt/xml) [mode]')
	exit()

mode=1
if len(sys.argv)==5:
	mode= int(sys.argv[4])

def validEmoji(t):
	if not(MIN_LEN<=len(t)<=MAX_LEN):
		return False
	valid=True
	for sp in SPLIT_CHAR_SET:
		if sp in t:
			valid=False
			break
	return valid

def init_t():
	global ts, pc, pts, s, lenf , tTh , tET, tInfos

	if sys.argv[1].lower().endswith('xml'):
		tET=ET.ElementTree(file=sys.argv[1])
		ts=[]
		tInfos=[]
		for symbol in tET.xpath('/symbols/category/symbol'):
			t=symRstrip(symbol.text)
			if validEmoji(t):
				ts.append(t)
				tInfos.append(symbol)
	else:
		tInfos=None
		tf=codecs.open(sys.argv[1] , 'r',encoding='utf-8')
		ts=[symRstrip(t) for t in tf.readlines() if len(t)<=MAX_LEN ]

	lenf=sum([len(t) for t in ts])
	print("load {} template from file in size {}".format(len(ts),lenf))
	pc={}
	pts=[]
	for t in ts:
		pt={}
		lent=len(t)
		for c in t:
			pc[c]= (pc.has_key(c) and pc[c] )+1./lenf
			pt[c]= (pt.has_key(c) and pt[c] )+1./lent

		pt['\0']=0
		pts.append(pt)

	pc[' ']=0

	tTh = sum([sum([pc[c] for c in t])/len(t) for t in ts]) / len(ts)


def psCalc(s):
	return sum([pc.has_key(c) and pc[c] for c in s])

def init_s():
	global s,ps , sps

	if sys.argv[2].find('://')>0:
		request = urllib2.Request(sys.argv[2])
		try:
			result = urllib2.urlopen(request)
		except BaseException,e:
			exit()
		s=result.read()
		s=s[s.find('<body'):s.find('</body>')+7]
		#print s
		s='\n'.join(ET.fromstring(s).xpath('.//text()'))

	elif sys.argv[2].lower().endswith('xml'):
		s='\n'.join(ET.ElementTree(file=sys.argv[2]).xpath('.//text()'))
	else:
		sf=codecs.open(sys.argv[2],'r' , encoding='utf-8')
		s=sf.read()

	#s='\0'+s #pos0 #sps=sum(0,i-1)
	s=symShrink(s)
	ps=[pc.has_key(c) and pc[c] for c in s]
	sps=reduce(lambda a,b:a+[a[-1]+b],ps,[0])[1:]
	maxlent=max([len(t) for t in ts])

	sr=[]
	th=tTh*SELECTION_THRES
	for l in range(MIN_LEN,min(MAX_LEN,int(maxlent*MAX_LEN_RATIO))):
		i=1
		ra=False
		while i<len(s)-l-1:
			if ps[i+l]>ps[i]:
				ra=True
			else:
				if ra and (sps[i+l-1]-sps[i-1]>th*l) and validEmoji(s[i:i+l]):
					ava=True
					for si in sr:
						if si['s']==s[i:i+l]:
							ava=False
							break
					if ava:
						sr.append( dict(s=s[i:i+l] , pos=(i,i+l)))
				ra=False

			i+=1

	return sr


def fig():
	#scatter([ord(c)for c in pc.keys()],pc.values())
	plot(ps)
	show()

def hmm0(t,pt,s):
	t='\0'+t+'\0'
	lent=len(t)
	f1=[int(s[0]==t[i]) for i in range(lent)]+[0 for i in range(lent)]
	#0~l-1:t2t,l~2l-1:t2f
	for i in range(1,len(s)):
		c1,c2=s[i-1],s[i]
		f0=copy.copy(f1)
		#f1=[0 for j in range(lent*2)]

		if c1 in pt: cond=6
		elif c1 in pc: cond=1
		else: cond=0

		if c2 in pt: cond+=4
		elif c2 in pc: cond+=2
		else: cond+=0

		if cond==10:
			for u in range(lent):
				if c2==t[u]:
					for v in range(u):
						if c1==t[v]:
							f1[u]=max(f1[u],f0[v]+1./(u-v))
		if cond==8:
			for v in range(lent):
				if c1==t[v]:
					f1[lent+v]=max(f1[lent+v],f0[v])#+pc[c2])
		if cond==5:
			for u in range(lent):
				if c2==t[u]:
					for v in range(u):
						f1[u]=max(f1[u],f0[lent+v]+pc[c1]*1./(u-v))
		if cond==3:
			for v in range(lent):
				f1[lent+v]=f0[lent+v]+pc[c1]  #meaning...?
		#print c2,f1

	return float(max(f1))/len(s)

def hmm1(t,pt,s):
	t='\0'+t+'\0'
	lent=len(t)
	f=[[int(s[0]==t[i]) for i in range(lent)]+[0 for i in range(lent)],]
	#0~l-1:t2t,l~2l-1:t2f
	for i in range(1,len(s)):
		c=s[i]
		#f0=copy.copy(f1)
		f1=[0 for j in range(lent*2)]

		for j in range(i):
			d=i-j
			for u in range(lent):
				if c==t[u]:
					for v in range(u):
						if s[j]==t[v]:
							f1[u]=max(f1[u],f[j][v]+1./(u-v)/d)
						else:
							f1[u]=max(f1[u],f[j][lent+v]+ EXT_COEFF * pt[c] / lent /(u-v)/d)  ###suck!! pc[c1] cannot be stored!
				elif c in pc:
					for v in range(u):
						if s[j]==t[v]:
							f1[lent+u]=max(f1[lent+u],f[j][v]+ pc[c]  /(u-v)/d)
						else:
							f1[lent+u]=max(f1[lent+u],f[j][lent+v]+  pc[c]*pt[t[v]] /(u-v)/d )

		f.append(f1)
		#print c,f1
	#print float(max(f1))/len(s)
	return float(max(f1))/len(s)


def calculate(ss,debug=False):
	sr=[]
	cnt=0
	for s in ss:
		if (s['s'].find('\n')<0) and not (s['s'].startswith(' ')):
			hm=0
			if mode:
				for i in range(len(ts)):
					h=hmm1(ts[i],pts[i],s['s'])
					if h>hm:
						tmi=i
						hm=h
			else:
				for i in range(len(ts)):
					h=hmm0(ts[i],pts[i],s['s'])
					if h>hm:
						tmi=i
						hm=h

			s.update(dict(ti_match=tmi,h=hm))
			sr.append(s)

			cnt+=1
			if cnt % 20==0:
				print('{}/{}'.format(cnt,len(ss)))

			if debug:
				print('"{}"  ,  matches {}  , h={} , pos={}' .format(s['s'], ts [s['ti_match']],s['h'],s['pos']))

	return sr



def hCmp(s1,s2):
	return cmp(s1['h'],s2['h'])

def lenCmp(s1,s2):
	return cmp([len(s1['s']),s1['h']] , [len(s2['s']),s2['h']])


def mixCmp(s1,s2):
	#print s1['s'],s1['h'],s2['s'],s2['h']
	#print(s1['h']**GAMMA * len(s1['s']) , s2['h'] ** GAMMA * len(s2['s']))
	return cmp(s1['h']**GAMMA * len(s1['s']) , s2['h'] ** GAMMA * len(s2['s']))

def refine(ss):
	sr=[]
	for s in ss:

		#Threshold
		if s['h']<H_THRES:
			continue
		#############

		found=False
		for i in range(len(sr)):
			sp,ep=sr[i]['pos']
			ss,es=s['pos']
			if not((ep<ss) or (sp>es)):

				periodCmp=mixCmp
				if periodCmp(s,sr[i])>0:
					sr[i]=copy.copy(s)

				sr[i]['pos']=(min(sp,ss),max(ep,es))
				found=True
				#print s['s'], sp,ep,ss,es
				break

		if not(found):
			sr.append(s)

	i=0
	while i<len(sr):
		st=sr[i]['s']
		tst=ts[sr[i]['ti_match']]
		for c in BLANK_CHAR_SET:
			st=st.replace(c,'')
			tst=tst.replace(c,'')

		if st==tst:
			print("repeat pattern {} = {} skipped".format(sr[i]['s'] , ts[sr[i]['ti_match']] ) )
			sr.pop(i)
		else:
			i+=1

	return sr


def output(ss):


	#ot= (len(sys.argv)==4) and sys.argv[3][-3:]
	ot=sys.argv[3][-3:]

	if (ot=='xml')and not(tInfos):
		ot==None

	if ot=='txt':
		oS=''

	if ot=='xml':
		oRoot=emojiRoot(None,__version__,"by SymGrabber")

	for si in ss :
		#print s[0], ts[s[1]], s[2]
		print('"{}" in full : "{}" ,  matches {} , h={}'.format(si['s'],s[si['pos'][0]:si['pos'][1]], ts [si['ti_match']],si['h']))

		if ot=='txt': oS+=si['s']+'\t:\t'+s[si['pos'][0]:si['pos'][1]]+'\n'

		if ot=='xml':
			oSymbol=ET.Element('symbols')
			oSymbol.text=si['s']
			oSymbol.attrib['note']=s[si['pos'][0]:si['pos'][1]]
			cat=tInfos[si['ti_match']].getparent()
			categories = oRoot.xpath('/symbols/category[@name="' + cat.attrib['name'] + '"]')
			if categories:
				categories[0].append(oSymbol)
			else:
				ET.SubElement(oRoot,'category',cat.attrib).append(oSymbol)


	if ot=='txt':
		of=codecs.open(sys.argv[3],'w' , encoding='utf-8')
		of.write(oS)
		of.close()

	if ot=='xml':
		ET.ElementTree(oRoot).write(file=sys.argv[3],encoding='utf-8',pretty_print=True)






if __name__ == '__main__':

	init_t()

	s0=init_s()

	'''
	for si in s0 :
		print('{} "{}" ' .format(len(si['s']),si['s']))

	print '='*80

	'''
	print('calculating for {} selected part...'.format(len(s0)))
	s1=calculate(s0 )#,True)

	print '='*80

	s2=refine(s1)

	output(s2)

	'''

	from pylab import *
	fig()

	'''
