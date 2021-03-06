from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(128), index = True, unique = True)
	password = db.Column(db.String(64))
	collections = db.relationship('Collection', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % (self.username)

	def dictionary(self):
		return {
			'id': str(self.id),
			'username': self.username,
			'email': self.email,
		}

class Article(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	url = db.Column(db.Text())
	title = db.Column(db.Text())
	content = db.Column(db.Text())
	author = db.Column(db.Text())
	excerpt = db.Column(db.Text())
	date = db.Column(db.String(64))
	dek = db.Column(db.Text())
	lead_image = db.Column(db.Text())

	def dictionary(self):
		return {
			'id': str(self.id),
			'url': self.url,
			'title': self.title,
			'content': self.content,
			'author': self.author,
			'excerpt': self.excerpt,
			'date': self.date,
			'dek': self.dek,
			'lead_image': self.lead_image,
		}

class Image(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.Text())
	caption = db.Column(db.Text())
	image = db.Column(db.Text())

	def dictionary(self):
		return {
			'id': str(self.id),
			'image': self.image,
			'title': self.title,
			'caption': self.caption,
		}

class Collection(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.String(128))
	description = db.Column(db.Text())
	category = db.Column(db.String(64))
	published = db.Column(db.Boolean())
	publish_date = db.Column(db.DateTime())
	thumbnail = db.Column(db.Text())
	articles = db.relationship('CollectionArticle', backref='collection', lazy='dynamic')
	images = db.relationship('CollectionImage', backref='collection', lazy='dynamic')

	def get_thumbnail(self):
		if self.thumbnail and self.thumbnail != "":
			return self.thumbnail
		else:
			if self.get_num_images > 0:
				for i in self.images:
					a = Image.query.get(i.image_id)
					return a.image
			for i in self.articles:
				a = Article.query.get(i.article_id)
				if a.lead_image:
					return a.lead_image
		return "http://ruon.tv/wp-content/uploads/2014/02/default-image.png" # TODO, get real placeholder image

	def dictionary(self):
		return {
			'id': str(self.id),
			'title': self.title,
			'description': self.description,
			'category': self.category,
			'published': self.published,
			'publish_date': self.publish_date,
			'thumbnail': self.get_thumbnail(),
			'items': self.items_dict(),
			'creator': self.get_user(),
			'user_id': self.user_id,
		}

	def items_dict(self):
		items = [None for i in xrange(self.get_num_items())]
		for article in self.articles:
			d = { 'id': str(article.article_id), 'type': 'article' }
			items[article.order] = d
		for image in self.images:
			d = { 'id': str(image.image_id), 'type': 'image' }
			items[image.order] = d

		return items

	def get_num_items(self):
		a = [None for _ in self.articles]
		i = [None for _ in self.images]
		return len(a) + len(i)

	def get_num_images(self):
		return len([None for _ in self.images])

	def get_user(self):
		return User.query.get(self.user_id).username

class CollectionArticle(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
	article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
	order = db.Column(db.Integer)

class CollectionImage(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
	image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
	order = db.Column(db.Integer)