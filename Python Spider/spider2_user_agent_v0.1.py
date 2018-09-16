
import urllib.request #url的请求库
from urllib.error import URLError,HTTPError,ContentTooShortError
import codecs
def download(url, user_agent:'wswp', num_retries=2): 	
#在spider1的基础上添加了user_agent,这里设置为web spider with python的缩写
	print('（+）开始下载：' , url)
	headers={'User Agent':user_agent} #http请求头可以人为输入，用户代理用字典值存储
	req=urllib.request.Request(url, headers=headers)
	try: 
		html=urllib.request.urlopen(req).read()
	except HTTPError as e: #将HTTP的错误存储到e值中
		html=None
		if num_retries > 0:# 默认最大的下载次数为2次，失败后可以重新再下载两次
			if hasattr(e, 'code') and 500<=e.code<=600: 
				print('服务器下载出错,尝试再次下载：', e.code)
			#hasattr 用来检查e值是否带有code属性，并且检查code值是否在500-600之间的URLError
			#如果满足条件则尝试再次下载
				return download(url,user_agent, num_retries-1)
			else:
				print('请求下载出错：', e.code)
			 #循环函数，下载次数减一
		#不满足条件以上这两个条件的均以html=None输出返回
	return html

##测试 初步下载爬虫可用性
if __name__ == '__main__':
	print(download('http://httpstat.us/400', user_agent='wswp', num_retries=2))

#### 注意事项  
# 2018.09.15 SyntaxError: non-default argument follows default argument
# 出错原因：把含有默认值的参数放在了不含默认值的参数的前面
# download(url, num_retries=2, user_agent:'wswp')
# num_retries为含默认值参数，user_agent为不含默认值参数，故报错，调整顺序即可
# 调整后如上所示
#  遗留问题
#2018.09.15  1下载循环 不可停止 
# 			 2 HTTP请求错误和服务器请求错误未分离
#2018.09.16 修改了原return download函数中的各参数位置 对应 def中顺序 问题解决
#			修改循环结构和打印结构