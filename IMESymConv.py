#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on %(date)
Project	:Python-Project
Version	:0.0.1
@author	:Macrobull
"""

#import lxml.etree as ET
from symbolConvert import *
from datetime import date
import os, sys



'''
fn = date.today().strftime("%y%m%d")
fin = sys.argv[1]

a=ET.ElementTree(file=fin)
b=txtSymbolElementTree(file='new.txt',category="G+ Post")
c=merge(a,b)

c.write(file = fn + '.xml',encoding='utf-8',pretty_print=True)
KTSymbolWrite(c,file = 'KT.' + fn + '.xml')
txtSymbolWrite(c, fn + '.txt',note=False)

os.popen('rm _Current.xml')
os.popen('ln -s ' + fn+'.xml _Current.xml')
os.popen('rm _KT_Current.xml')
os.popen('ln -s KT.' + fn+'.xml _KT_Current.xml')
'''


a=ET.ElementTree(file='default.baiduTemplate.xml')
b=ET.ElementTree(file='131230.xml')
c=merge(a,b,crosscategory=True)
baiduSymbolWrite(c,'131230.ini')


#b=txtSymbolElementTree(file='131205.txt',category="G+ Post")
#b=txtSymbolElementTree(file='Emoji.131101.txt',category="long name makes good!")
#merge(a,b,crosscategory=True).write(file='test.xml',encoding='utf-8',pretty_print=True, xml_declaration=True)

#baiduSymbolWrite(c,'131205.ini')

#c.write(file='131205.xml',encoding='utf-8',pretty_print=True)
#b.write(file='test.xml',encoding='utf-8',pretty_print=True)

#txtSymbolWrite(c,'test.txt',note=False)
#KTSymbolWrite(c,file='KT.131205.xml')

