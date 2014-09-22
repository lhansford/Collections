from flask import Flask, jsonify, make_response, request, abort
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)

from read import ParsedArticle
import models

@app.route('/')
def index():
	return "Wrong way, go back."

@app.route('/api/v1.0/categories', methods=['GET'])
def categories():
	"""	URL - /api/v1.0/categories
		Method - GET

		Returns a list of all available categories.
	"""
	categories = [
		'News',
		'Technology',
		'Music',
		'Sports'
	]
	response = { 'response': categories }
	return jsonify(response)

@app.route('/api/v1.0/collections', methods=['GET'])
def collections():
	"""	URL - /api/v1.0/collections
		Method - GET

		Returns a list of all collections
	"""
	collections = models.Collection.query.all()
	if not collections:
		abort(404)
	response = { 'collections': [{'id': c.id, 'title': c.title} for c in collections] }
	return jsonify(response)

@app.route('/api/v1.0/collection', methods=['POST'])
def post_collection():
	"""	URL - /api/v1.0/collection
		Method - POST

		Creates a new collection and returns a ID that represents it.
	"""
	post_json = request.get_json()
	if not post_json:
		abort(400)
	title = post_json['title']
	description = post_json['description']
	category = post_json['category']
	user_id = post_json['user_id']

	if None in [title, description, category, user_id]:
		abort(400)

	collection = models.Collection(
		user_id = user_id,
		title = title,
		category = category,
		published = False,
		publish_date = None,
		thumbnail = None,
	)
	db.session.add(collection)
	db.session.commit()
	return jsonify({'collection_id':collection.id}), 201

@app.route('/api/v1.0/collection/<int:collection_id>', methods=['GET'])
def collection(collection_id):
	"""	URL - /api/v1.0/collection/[id]
		Method - GET

		Returns the collection the given ID represents.
	"""
	collection = models.Collection.query.get(collection_id)
	if not collection:
		abort(404)
	response = {'id': collection.id, 'title': collection.title, 'items': collection.items_dict()}
	return jsonify(response)

@app.route('/api/v1.0/collection/<int:collection_id>', methods=['POST'])
def add_to_collection(collection_id):
	"""	URL - /api/v1.0/collection/[id]
		Method - POST

		Adds an article to a collection.
	"""
	post_json = request.get_json()
	collection = models.Collection.query.get(collection_id)
	if not post_json or not collection or not 'article_id' in post_json:
		abort(400)
	item = models.CollectionItem(
		collection_id = collection_id,
		article_id = post_json['article_id'],
		order = len(collection.items()) + 1
	)
	db.session.add(item)
	db.session.commit()
	return jsonify({})

@app.route('/api/v1.0/user/<int:user_id>/collections', methods=['GET'])
def user_collections(user_id):
	"""	URL - /api/v1.0/user/[id]/collections
		Method - GET

		Returns the all the collecitons of the user the given ID represents.
	"""
	user = models.User.query.get(user_id)
	if not user:
		abort(404)
	response = { 'collections': 
		[{'id': c.id, 'title': c.title, 'items': c.items_dict()} for c in user.collections]
	}
	return jsonify(response)

@app.route('/api/v1.0/article/<int:article_id>', methods=['GET'])
def article(article_id):
	"""	URL - /api/v1.0/article/[id]
		Method - GET

		Returns the article the given ID represents.
	"""
	article = models.Article.query.get(article_id)
	if not article:
		abort(404)
	article_dict = {
		'url': article.url,
		'title': article.title,
		'content': article.content,
		'author': article.author,
		'excerpt': article.excerpt,
		'date': article.date,
		'dek': article.dek,
		'lead_image': article.lead_image,
	}
	return jsonify(article_dict)

@app.route('/api/v1.0/article', methods=['POST'])
def post_article():
	"""	URL - /api/v1.0/article
		Method - POST

		Creates a new article from a URL and returns a ID that represents it.
	"""
	post_json = request.get_json()
	if not post_json or not 'url' in post_json:
		abort(400)
	url = post_json['url']

	# Check if the article is already in database
	query = models.Article.query.filter_by(url=url).first()
	if query:
		return jsonify({'article_id':query.id}), 201

	# If not in DB, get article from web
	parsedArticle = ParsedArticle(url)
	article = models.Article(
		url = url,
		title = parsedArticle.get_title(),
		content = parsedArticle.get_content(),
		author = parsedArticle.get_author(),
		excerpt = parsedArticle.get_excerpt(),
		date = parsedArticle.get_date(),
		dek = parsedArticle.get_dek(),
		lead_image = parsedArticle.get_lead_image(),
	)
	db.session.add(article)
	db.session.commit()
	return jsonify({'article_id':article.id}), 201


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
	app.run(debug=True)