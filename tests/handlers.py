from appengineserene.handlers import ListOrCreateHandler, InstanceHandler
from appengineserene.tests.models import ProjectDummy, StoryDummy, ScrumStoryDummy


class ProjectListOrCreateHandler(ListOrCreateHandler):
    model = ProjectDummy
    order_by = ('number', 'name')


class StoryListOrCreateHandler(ListOrCreateHandler):
    model = StoryDummy
    order_by = ('number',)
    parent_model = ProjectDummy


class ScrumStoryListOrCreateHandler(ListOrCreateHandler):
    model = ScrumStoryDummy
    expanded_properties = ('story',)


class ScrumStoryInstanceHandler(InstanceHandler):
    model = ScrumStoryDummy
    expanded_properties = ('story',)