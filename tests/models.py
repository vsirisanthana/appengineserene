from google.appengine.ext import db


class ProjectDummy(db.Model):
    number = db.IntegerProperty(required=True)
    name = db.StringProperty(required=True)
    description = db.TextProperty()
    owner = db.UserProperty(auto_current_user_add=True)


class StoryDummy(db.Model):
    number = db.IntegerProperty()
    title = db.StringProperty(required=True)


class ScrumStoryDummy(db.Model):
    story = db.ReferenceProperty(StoryDummy, required=True)
    status = db.StringProperty()