# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 23:08:07 2013
Project	:Symbol Converter
Version	:0.0.1
@author	:macrobull

"""
__version__="0.0.1"

RSTRIP_CHAR_SET=('\t',' ','\n','\r',u'　',u'\ufeff','\0')
REMOVABLE_CHAR_SET=('\r',u'\ufeff','\0')

import time,re
import codecs
from copy import deepcopy
#from copy import copy

import lxml.etree as ET
'''
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
'''

def symRstrip(s):
	for c in RSTRIP_CHAR_SET:
		s=s.rstrip(c)
	return s


def symShrink(s):
	for c in REMOVABLE_CHAR_SET:
		s=s.replace(c,'')
	return s

def emojiRoot(rootElement=None,version=None,note="none"):
	if version == None: version = __version__
	if rootElement:
		root=rootElement
	else:
		root=ET.Element('symbols')
	info=ET.SubElement(root,'info')
	ET.SubElement(info,'version').text=version
	ET.SubElement(info,'created_timestamp').text=str(int(time.time()))
	ET.SubElement(info,'note').text=note

	return root

#class baiduSymbol(ET._ElementTree):
def baiduSymbolElementTree(rootElement=None,file=None):
	root=emojiRoot(rootElement,__version__,'Generated by SymbolConvert V' + __version__ + ' from Baidu IME sym file (.ini)')
	if file:

		ET.SubElement(info,'source').text=file
		f=codecs.open(file,'r',encoding='utf-16')

		for line in f.readlines():
			attr_start=line.find('[')
			attr_end=line.find(']')
			if (attr_start==0)and(attr_end>=0):
				#print line,attr_end
				category,split_space,continuous = line[attr_start+1:attr_end].split(',')[:3]
				cat=ET.SubElement(root,'category',{'name':category,'split':split_space,'continuous':continuous})

				line=symRstrip(line)
				if split_space=='1':
					syms=line[attr_end+2:].split(' ')
				else:
					syms=line[attr_end+2:]
				for s in syms:
					sym=ET.SubElement(cat,'symbol')
					sym.text=s
					#print(s,len(s))
					#note=''
		f.close()
	return ET.ElementTree(root)

def txtSymbolElementTree(rootElement=None,file=None,category='New'):
	root=emojiRoot(rootElement,__version__,'Generated by SymbolConvert V' + __version__ + ' from text file')
	if file:
		cat=ET.SubElement(root,'category',{'name':category})
		ET.SubElement(root[0],'source').text=file
		#f=codecs.open(file,'r')#,encoding='utf-9')
		f=codecs.open(file,'r',encoding='utf-8')
		fMul=False
		name=None
		symStr=''
		for line in f.readlines():
			prename=re.match('.*\s+:\s+',line) #get name by "name : " form
			if prename:
				prename=prename.group()
				if not(fMul) or re.match('_{4,}',line[len(prename):]):
					line=line[len(prename):]
					name=re.sub('\s+:\s+','',prename)
					print('Note "{}" found'.format(name))

			if not(fMul):   #skip blank line
				if re.match('\s*$',line) : continue
				#if re.match('_{4,}',line) : continue


			if re.match('_{4,}',line):   #underline split mode
				if re.match('_{4,}\s*$',line):
					if fMul and symStr:
						sym.text=symRstrip(symStr)
						sym=ET.SubElement(cat,'symbol')
					fMul=True
					symStr=''
			elif fMul:
				if (line.find('</mul>')==0): #<mul> mode
					fMul=False
					sym.text=symRstrip(symStr)
				else:
					symStr+=line
			elif (line.find('<mul>')==0):
				sym=ET.SubElement(cat,'symbol')
				symStr=''
				fMul=True
			elif line!='' :   #single line mode
				sym=ET.SubElement(cat,'symbol')
				#sym.text=line.rstrip('\n').rstrip('\r').rstrip(' ')#.lstrip('\r').lstrip('\n')
				sym.text=symRstrip(line)

			if name:
				sym.attrib['name']=name

		f.close()
		if fMul:
			symStr=symRstrip(symStr)
			if symStr:
				sym.text=symStr
			else:
				cat.remove(sym)

	return ET.ElementTree(root)

def KTSymbolWrite(tree,file,**kwarg):
	#tree=tree.__deepcopy__(tree)
	tree=deepcopy(tree)
	root=tree.getroot()
	root.tag='emoji'
	root[0].clear()
	root[0].tag='infoos'
	root[0].text=u'ლ(｡◕ˇ‿ˇ◕｡ლ)'
	for sym in tree.getroot().findall('.//symbol'):
		ET.SubElement(sym,'string').text=sym.text
		if sym.attrib.has_key('name'):
			ET.SubElement(sym,'note').text=sym.attrib['name']
			del(sym.attrib['name'])
		sym.tag='entry'

		sym.text=''
	tree.write(file=file,**kwarg)


def baiduSymbolWrite(tree,file,hint=False):
	root=tree.getroot()
	f=codecs.open(file,'w',encoding='utf-16')
	for category in root.iterfind('./category'):
		#print(category.attrib)
		try:
			f.write('[{name},{split},{continuous}]'.format(**category.attrib))
			split=int(category.attrib['split'])
		except KeyError:
			f.write('[{name},1,0]'.format(**category.attrib))
			split=1
		for symbol in category.iterfind('./symbol'):
			sym=symbol.text

			if sym.find('\n')>=0:
				if hint:
					sym='invalid'
				else:
					continue

			sym=sym.replace(' ','　')

			f.write(' '*split+sym)
		f.write('\n')
	f.close()

def txtSymbolWrite(tree,file,note=True):
	def refine(s):
		s.rstrip('\n').rstrip(' ').rstrip('\n')
		#print(s.find('\n'))
		if s.find('\n')>=0: s='<mul>\n'+s+'\n</mul>'
		return s+'\n\n'
	root=tree.getroot()
	f=codecs.open(file,'w',encoding='utf-8')
	#f.writelines(map(refine,root.xpath('//symbol/@name | //symbol/text()')))# no note yet...
	for sym in root.xpath('//symbol'):
		if note and sym.attrib.has_key('name'):
			f.write('{}\t: '.format(sym.attrib['name']))
		f.write(refine(sym.text))
	f.close()

def merge(*symsETs,**kwarg):
	crosscategory=kwarg.has_key('crosscategory') and kwarg['crosscategory']
	root=emojiRoot(None,__version__,'Generated by SymbolConvert V' + __version__)
	for symsET in symsETs:
		for cat in symsET.xpath('./category'):
				categories=root.xpath('./category[@name="'+cat.attrib['name']+'"]')
				if categories==[]:
					#print('add new cat {} from {}'.format(cat.attrib['name'],id(symsET)))
					#category=copy(cat)
					category=deepcopy(cat)
					category.text=None
					if crosscategory:
						for symbol in category:
							symbol.text=symShrink(symbol.text)
							if root.xpath( './category/symbol/text()').count( symbol.text):
								category.remove(symbol)
								print('repeat symbo {} removed (crosscat) (add category)'.format(symbol.text))
					root.append(category)
				else:
					#print('merge cat {} from {}'.format(cat.attrib['name'],id(symsET)))
					category=categories[0]
					for sym in cat:
						#symx=ET.Element('symbol')
						sym.text=symShrink(sym.text)
						if  category.xpath('./symbol/text()').count( sym.text ) or crosscategory and root.xpath('./category/symbol/text()').count( sym.text ):
								print('repeat symbo {} removed (crosscat) (merge category)'.format(sym.text))
						else:
							category.append(deepcopy(sym))
							#category.append(copy(sym))

	for sym in root.xpath('//*'):
		sym.tail=None
	return ET.ElementTree(root)
