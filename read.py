from readability import ParserClient

PARSER_TOKEN = 'd63ca4dbe5bbadb1dfe244e9397d3f8bec58366c'

class ParsedArticle(object):

	def __init__(self, url):
		self.url = url
		self.response = self._get_article(url)

	def _get_article(self, url):
		parser_client = ParserClient(PARSER_TOKEN)
		return parser_client.get_article_content(url)

	def get_response(self):
		return self.response

	def get_content(self):
		if self.response.content['content'] is None:
			return ""
		return self.response.content['content']

	def get_author(self):
		if self.response.content['author'] is None:
			return ""
		return self.response.content['author']

	def get_url(self):
		if self.response.content['url'] is None:
			return ""
		return self.response.content['url']

	def get_title(self):
		if self.response.content['title'] is None:
			return ""
		return self.response.content['title']

	def get_excerpt(self):
		if self.response.content['excerpt'] is None:
			return ""
		return self.response.content['excerpt']

	def get_date(self):
		if self.response.content['date_published'] is None:
			return ""
		return self.response.content['date_published']

	def get_dek(self):
		if self.response.content['dek'] is None:
			return ""
		return self.response.content['dek']

	def get_lead_image(self):
		if self.response.content['lead_image_url'] is None:
			return ""
		return self.response.content['lead_image_url']