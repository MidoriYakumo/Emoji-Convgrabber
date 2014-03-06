#! /usr/bin/python
# -*- coding: utf-8 -*-

__ld__ = '131230'
__td__ = '140218'

#import lxml.etree as ET
from symbolConvert import *


#a=ET.ElementTree(file='default.emoji.xml')
a=ET.ElementTree(file='../'+__ld__+'.xml')
#b=ET.ElementTree(file='default.baiduTemplate.xml')
#b=txtSymbolElementTree(file='out.txt',category="New")
b=txtSymbolElementTree(file='../new.txt',category="New")
#b=txtSymbolElementTree(file='Emoji.131101.txt',category="long name makes good!")
#merge(a,b,crosscategory=True).write(file='test.xml',encoding='utf-8',pretty_print=True, xml_declaration=True)
c=merge(a,b, crosscategory = True)



c.write(file='../'+__td__+'.xml',encoding='utf-8',pretty_print=True)
#b.write(file='test.xml',encoding='utf-8',pretty_print=True)

txtSymbolWrite(c,'../'+__td__+'.txt',note=False)
KTSymbolWrite(c,file='../KT.'+__td__+'.xml')

d=ET.ElementTree(file='../default2.baiduTemplate.xml')
c=merge(d,c, crosscategory = True)
baiduSymbolWrite(c,'../'+__td__+'.ini')
'''

a=ET.ElementTree(file='../default.baiduTemplate.xml')
b=txtSymbolElementTree(file='../baidu_sym2.txt',category="New")
c=merge(a,b, crosscategory = True)
c.write(file='../default2.baiduTemplate.xml',encoding='utf-8',pretty_print=True)
'''