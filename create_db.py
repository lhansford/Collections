from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import db
import os.path
db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

import models
from read import ParsedArticle

#For Testing

u = models.User(username="test", email="test@test.com", password='test')
db.session.add(u)
db.session.commit()

c = models.Collection(user_id=u.id, title="A test collection")
db.session.add(c)
db.session.commit()

parsedArticle = ParsedArticle('http://www.nytimes.com/2014/09/20/world/africa/ebola-outbreak.html')
a1 = models.Article(
	url = parsedArticle.get_url(),
	title = parsedArticle.get_title(),
	content = parsedArticle.get_content(),
	author = parsedArticle.get_author(),
	excerpt = parsedArticle.get_excerpt(),
	date = parsedArticle.get_date(),
	dek = parsedArticle.get_dek(),
	lead_image = parsedArticle.get_lead_image(),
)

parsedArticle = ParsedArticle('http://www.theguardian.com/world/2014/sep/20/terrorism-laws-to-be-strengthened-and-modernised-says-justice-minister')
a2 = models.Article(
	url = parsedArticle.get_url(),
	title = parsedArticle.get_title(),
	content = parsedArticle.get_content(),
	author = parsedArticle.get_author(),
	excerpt = parsedArticle.get_excerpt(),
	date = parsedArticle.get_date(),
	dek = parsedArticle.get_dek(),
	lead_image = parsedArticle.get_lead_image(),
)

parsedArticle = ParsedArticle('http://www.wired.com/2014/09/gondolas-brooklyn/')
a3 = models.Article(
	url = parsedArticle.get_url(),
	title = parsedArticle.get_title(),
	content = parsedArticle.get_content(),
	author = parsedArticle.get_author(),
	excerpt = parsedArticle.get_excerpt(),
	date = parsedArticle.get_date(),
	dek = parsedArticle.get_dek(),
	lead_image = parsedArticle.get_lead_image(),
)

db.session.add(a1)
db.session.add(a2)
db.session.add(a3)
db.session.commit()

ci1 = models.CollectionItem(collection_id=c.id, article_id=a1.id, order=1)
ci2 = models.CollectionItem(collection_id=c.id, article_id=a2.id, order=2)
ci3 = models.CollectionItem(collection_id=c.id, article_id=a3.id, order=3)

db.session.add(ci1)
db.session.add(ci2)
db.session.add(ci3)
db.session.commit()
