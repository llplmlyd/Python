import urllib.request #url的请求库
from urllib.error import URLError,HTTPError,ContentTooShortError

def download(url, num_retries=2):
	print('（+）开始下载：%s' % url)
	try: 
		html=urllib.request.urlopen(url).read() #尝试下载网页并返回其HTML
	except HTTPError as e: #将HTTP的404错误存储到e值中
		html=None
		if num_retries > 0:# 默认最大的下载次数为2次，失败后可以重新再下载两次
			if hasattr(e, 'code') and 500<=e.code<=600: 
				print('服务器下载出错,尝试再次下载：', e.code)
			#hasattr 用来检查e值是否带有code属性，并且检查code值是否在500-600之间的URLError
			#如果满足条件则尝试再次下载
				return download(url,num_retries-1)
			else:
				print('请求下载出错：', e.code)
			 #循环函数，下载次数减一
		#不满足条件以上这两个条件的均以html=None输出返回
	except URLError as e:  #将HTTP的5xx错误存储到e值中
		print('URLError下载出错,尝试再次下载：', e.reason)
		html=None
	return html

##测试 初步下载爬虫可用性
if __name__ == '__main__':
	print(download('http://httpstat.us/500'))