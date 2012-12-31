import webapp2

from appengineserene.tests.handlers import (ProjectListOrCreateHandler, StoryListOrCreateHandler,
                                   ScrumStoryListOrCreateHandler, ScrumStoryInstanceHandler)


app = webapp2.WSGIApplication([
    webapp2.Route(r'/projects<:/?>', handler=ProjectListOrCreateHandler),
    webapp2.Route(r'/projects/<parent_key>/stories<:/?>', handler=StoryListOrCreateHandler),
    webapp2.Route(r'/scrum/stories<:/?>', handler=ScrumStoryListOrCreateHandler),
    webapp2.Route(r'/scrum/stories/<key><:/?>', handler=ScrumStoryInstanceHandler),
], debug=True)