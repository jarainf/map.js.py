#!/usr/bin/env python3
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError

class Linker(HTMLParser):
	global parsed_sites

	def __init__(self, url, maxdepth=5, node=None, depth=-1, nonhtml=False):
		if not url == '':
			self._node = LinkTree(self._handle_url(url))
		else:
			self._node = node
		self._depth = depth
		self._maxdepth = maxdepth
		self._nonhtml = nonhtml
		self._level = []

		HTMLParser.__init__(self)
	
		self._feed_link(self._node)

	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			for (x, y) in attrs:
				if x.lower() == 'href':
					link = self._handle_url(y)
					if link:
						self._decide_usage(link)

	def _handle_url(self, url):
		if '://' in url:
			if url.startswith('http://') or url.startswith('https://'):
				return urlparse(url)
		else:
			if url.startswith('//'):
				return urlparse('http:' + url)

	def _decide_usage(self, url):
		if url[1] in parsed_sites:
			return
		else:
			parsed_sites.append(url[1])
		req = Request(url.geturl(), method="HEAD")
		try:
			resp = urlopen(req)
		except URLError as e:
			return
		if 'Content-Type' in resp:
			if 'text/html' in resp[Content-Type]:
				self._level.append(url)
		else:
			if url[2] == '' or url[2].endswith('.html') or url[2].endswith('.php') or '.' in url[2] or url[2].endswith('.htm'):
				self._level.append(url)
			elif self._nonhtml:
				self._node.add(LinkTree(url))

	def _feed_link(self, node):
		content = self._retrieve_url(node.data.geturl())
		if content is None:
			return
		self.feed(content)
		for x in self._level:
			nxtnode = LinkTree(x)
			self._node.add(nxtnode)
			if not (self._depth + 1) >= self._maxdepth:
				nxtlevel = Linker('', self._maxdepth, nxtnode, self._depth + 1, self._nonhtml)
				self._node.add(nxtlevel.get_tree())

	def _retrieve_url(self, url):
		data = None
		if not self._check_robots(url):
			return None
		try:
			data = urlopen(url)
		except URLError as e:
			return None
		encoding = data.headers.get_content_charset()
		if encoding:
			return data.read().decode(encoding)
		else:
			return data.read().decode('utf-8')

	def _check_robots(self, url):
		return True

	def get_tree(self):
		return self._node

class LinkTree(object):
	def __init__(self, data):
		self.data = data
		self._children = []

	def add(self, tree):
		self._children.append(tree)

	def print_self(self):
		print(self.data.geturl())
		for x in self._children:
			x.print_self()

def  main():
	global parsed_sites
	parsed_sites = []
	a = Linker('http://vehk.de/blag/')
	a.get_tree().print_self()

if __name__ == '__main__':
	main()
