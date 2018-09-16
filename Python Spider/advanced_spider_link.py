'''@高级爬虫版本：解析robot.txt；支持代理；下载限速；避免爬虫陷阱
	@调用spider2_user_agent_v0.1版本的download函数
'''

import urllib.request #url的请求库
from urllib.error import URLError,HTTPError,ContentTooShortError
import itertools
import re
import codecs #将获取到的html 字节型文件编码成字符串
import urllib.parse #url解析库
import urllib.robotparser #robots.txt的解析器模块
from datetime import datetime
import time


def link_spider(seed_url,user_agent:'wswp',link_regex, delay=5,max_depth=2):
	"""Crawl from the given seed URL following links matchesd by link_regex
	"""
	spider_queue=[seed_url]
	seen={seed_url: 0}#将url设置成一个不可重复元素的集合
	rp = get_robots(seed_url)#robot.txt的解析
	throttle = Throttle(delay)
	while spider_queue:
		#del url中末尾的元素并将其值返回给url
		url=spider_queue.pop()
		#check url passes robots.txt restrictions
		if rp.can_fetch(user_agent,url):
			throttle.wait(url)
			html=download(url,user_agent)
			html=html.decode()
			#避免爬虫陷阱，设置爬取的链接深度
			depth=seen[url]
			if depth!=max_depth:
			#filter for links matching our regular expression
				for link in get_links(html): # 在主站下返回的HTML文档文件中getlinks
					if re.match(link_regex,link):# 此时匹配成功的link可能是绝对链接也可能是相对链接
						link=urllib.parse.urljoin(seed_url,link)#将link的格式与seed_url相对应
						# print(link) 如果在这里打印可以查看每一页的链接页面
						if link not in seen:
							seen[link]=depth+1
							spider_queue.append(link)			
		else:
			print('Blocked by robots.txt:%s' % url)
				 #当前页面抓取的链接如果如何要求，则放入爬取的队列中去

def download(url, user_agent:'wswp',proxy=None, num_retries=2): 	
#添加了proxy
	print('（+）开始下载：' , url)
	headers={'User Agent':user_agent} #http请求头可以人为输入，用户代理用字典值存储
	req=urllib.request.Request(url, headers=headers)
	#添加支持代理功能
	opener = urllib.request.build_opener()
	if proxy:
		proxy_params = {urllib.parse(url).scheme: proxy}
		opener.add_handler(urllib.request.ProxyHandler(proxy_params))
	try: 
		# html=opener.open(req).read()原版本
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

def get_links(html):
	"""Return a list of links from html
	"""
	#a regular expression to extract all links from the webpage
	# html=html.decode()
	# print(html)#测试html是什么类型对象
	webpage_regex=re.compile('<a[^>]+href=["\'](.*?)["\']',re.IGNORECASE)
	#取出该页面下所有的a标签，即链接，以字符串的形式表示
	# list of all links from the webpage
	return webpage_regex.findall(html) #返回字符串中所有非重叠模式匹配的列表,去重

#对robot.txt进行解析读取
def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urllib.parse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp

class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """
    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}
        
    def wait(self, url):
        domain = urllib.parse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()

#测试
user_agent='wswp'
seed_url='http://example.webscraping.com'
link_regex='/(places/default/index)'#index这个页面只有25个，下载完则完成
link_spider(seed_url,user_agent,link_regex,max_depth=2) #注意，参数的位置仍然是会导致下载失败的

