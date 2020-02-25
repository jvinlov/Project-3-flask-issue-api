import os ##new for heroku
import datetime
from peewee import *
from flask_login import UserMixin
from playhouse.db_url import connect
# from playhouse.migrate import * # not working for me


if 'ON_HEROKU' in os.environ:
	DATABASE = connect(os.environ.get('DATABASE_URL')) 

else:
	DATABASE = SqliteDatabase('issues.sqlite')
	# migrator = SqliteMigrator(DATABASE) # not working for me


class User(UserMixin, Model): #User must come before Issue or you get a "NameError: name 'User' is not defined"
	name = CharField()
	department = CharField()
	email = CharField(unique=True)
	password = CharField()

	def __str__(self):
		return '<User: {}, id: {}>'.format(self.email, self.id)

	def __repr__(self):
		return '<User: {}, id: {}>'.format(self.email, self.id)

	class Meta:
		db_table = 'users'
		database = DATABASE


class Issue(Model):
	subject = CharField()
	created_at = DateTimeField(default=datetime.datetime.now)
	# added created_by to relate an issue to the person creating the issue
	created_by = ForeignKeyField(User, backref='issues')# Represents One-to-Many

	class Meta:
		db_table = 'issues'
		database = DATABASE


class Comment(Model):
	body = CharField()
	created_at = DateTimeField(default=datetime.datetime.now)
	# added created_by to relate a comment to the person creating the comment
	created_by = ForeignKeyField(User, backref='comments')# Represents One-to-Many
	assoc_issue_id = IntegerField()
	# test = CharField()


	class Meta:
		db_table = 'comments'
		database = DATABASE

# migrate( # only use this if you make a change to the schema
# *** DOES NOT WORK FOR ME...Have to DROP TABLE instead ***
#     migrator.drop_column('comments', 'assoc_issue_id'),
# )



def initialize():
	DATABASE.connect()
	DATABASE.create_tables([Issue, User, Comment], safe=True) 
	print("TABLES CREATED")
	DATABASE.close()
