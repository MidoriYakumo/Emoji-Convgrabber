Emoji-Convgrabber
=================================================================================
a conversion/grab tool for Baidu IME and https://github.com/KTachibanaM/cloudemoji

symbolConvert.py
	这个库,提供 txt,KT的xml,窝的xml(SymbolElementTree),百度输入法符号ini的转换功能.
	说明:
		导入与合并操作中将忽略颜文字右侧的 RSTRIP_CHAR_SET 字符
		颜文字判重时将忽视 REMOVABLE_CHAR_SET
	格式说明:
		SymbolElementTree xml结构:
			<symbols>
				[<info>[<version>][<created_timestamp>][<note>]</info>]
				<category name="Yuan Liu" continuous="0" split="1">
					<symbol [name="不愉快"]>,,Ծ‸Ծ,,﻿</symbol>
				</category>
			</symbols>
			其中continuous与split作用于百度输入法,参见百度输入法ini结构.
			
		KT的xml结构:
			<emoji>
				<infoos>(不可忽略)</infoos>
				<category name="Yuan Liu">
					<entry>
						<string>( &#9684; &#1724; &#9684; )</string>
						[<note>&#21653;&#22079;&#22079;</note>]
					</entry>
				</category>
			</emoji>
			
		txt结构:
			单行颜文字:
				一行一个,若有注释,读取' : '前的部分为注释,起后为颜文字.
				空行被忽略.
			多行颜文字:
				1)满足re.match('_{4,}',line)的两行之间视为一个长颜文字,若有注释,加在下划线以前,读取' : '前的部分为注释.
				2)<mul>开始,若有注释,读取' : '前的部分为注释,起后为颜文字.
				3)下划线结束上一个多行颜文字,开始下一个多行颜文字,直到文件结尾无长下划线则会自动完结.</mul>仅结束一个多行颜文字.
			bug很多,小心可能会玩脱.
			
		百度输入法ini结构:
			个人以baiduIME.template为基本模版,插入颜文字.
			百度里每个分类由[(名称),(空格分隔),(默认锁定符号输入状态)]开始.
	
	
	baiduSymbolElementTree(rootElement=None,file=None) : 从百度ini读取到SymbolElementTree
	
	txtSymbolElementTree(rootElement=None,file=None,category='New') : 从txt读取到SymbolElementTree, 分类为category.
	
	KTSymbolWrite(tree,file,**kwarg) : 将SymbolElementTree写入到KT xml文件里, 使用lxml.tree.write的参数
	
	baiduSymbolWrite(tree,file,hint=False) : 将SymbolElementTree写入到百度输入法ini里, hint为是否在ini内提示多行颜文字失效.
	
	txtSymbolWrite(tree,file,note=True) : 将SymbolElementTree写入到txt中, note为是否写出注释.
	
	merge(*symsETs,**kwarg) : 将一系列SymbolElementTree合并, 若crosscategory = True, 则跨分类查找重复内容, 否则仅在同一分类中查找.
	
	IMESymConv.py包含日用示例.
	
IMESymGrabber.py
	python IMESymGrabber.py Template(txt/xml) Source(txt/xml/URL(elementree是个废,其实不能用...)) Dest(txt/xml) [mode]
	xml是SymbolElementTree
	mode 0比1快而差, 默认1, 渣慢...
