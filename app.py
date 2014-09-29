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

@app.route('/api/v1.0/user', methods=['POST'])
def find_user():
	"""	URL - /api/v1.0/user
		Method - POST

		Receives a post containing a user email, authenticated by Google, and 
		returns the user if associated with that email. Creates a new user if 
		that user doesn't already exist.
	"""
	post_json = request.get_json()
	if not post_json:
		abort(400)
	email = post_json['email']
	username = email.split("@")[0]
	same_username = models.User.query.filter_by(username=username)
	if len(same_username) > 0:
		username += len(same_username)
	print username
	if not email:
		abort(400)

	user = models.User.query.filter_by(email=email)
	if len(user) == 0:
		user = models.User(
			username = username,
			email = email,
			password = ""
		)
		db.session.add(user)
		db.session.commit()
	else:
		user = user[0]
	return jsonify({'user_id':user.id}), 201

@app.route('/api/v1.0/collections', methods=['GET'])
def collections():
	"""	URL - /api/v1.0/collections
		Method - GET

		Returns a list of all collections
	"""
	collections = models.Collection.query.all()
	if not collections:
		abort(404)
	response = { 'collections': [c.dictionary() for c in collections] }
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
		description = description,
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
	return jsonify(collection.dictionary())

@app.route('/api/v1.0/collection/<int:collection_id>', methods=['POST'])
def add_to_collection(collection_id):
	"""	URL - /api/v1.0/collection/[id]
		Method - POST

		Adds an article to a collection.
	"""
	post_json = request.get_json()
	collection = models.Collection.query.get(collection_id)
	article = models.Article.query.get(post_json['article_id'])
	if not collection or not article:
		abort(400)
	item = models.CollectionItem(
		collection_id = collection.id,
		article_id = article.id,
		order = len(collection.items_dict()) + 1
	)
	db.session.add(item)
	db.session.commit()
	return jsonify({'message': 'Success'}), 201

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
		[c.dictionary() for c in user.collections]
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
	return jsonify(article.dictionary())

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
		return jsonify(query.dictionary()), 201

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
	return jsonify(article.dictionary()), 201


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
	app.run(debug=True)