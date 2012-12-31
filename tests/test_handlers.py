from datetime import datetime

import unittest2
import webtest
from google.appengine.ext import testbed

import appenginejson
from appenginetest.utils import setCurrentUser, logoutCurrentUser

from appengineserene.tests.handlers import ProjectListOrCreateHandler
from appengineserene.tests.models import ProjectDummy, StoryDummy, ScrumStoryDummy
from appengineserene.tests.urls import app


class BaseTestHandler(unittest2.TestCase):

    def setUp(self):
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        setCurrentUser('mouse@lemur.com', 'Microcebus')

        self.project_apple_kwargs = {
            'number': 1,
            'name': 'Apple',
            'description': 'The round fruit of a tree of the rose family.',
        }
        self.project_apple_too_kwargs = {
            'number': 2,
            'name': 'Apple',
            'description': 'The round fruit of a tree of the rose family.',
            }
        self.project_banana_kwargs = {
            'number': 2,
            'name': 'Banana',
            'description': 'A long curved fruit.',
        }
        self.project_coconut_kwargs = {
            'number': 1,
            'name': 'Coconut',
            'description': 'The large, oval, brown seed of a tropical palm.',
        }
        self.project_dewberry_kwargs = {
            'number': 2,
            'name': 'Dewberry',
            'description': 'A trailing European bramble (Rubus caesius) with soft prickles and '
                           'edible, blackberrylike fruit, which has a dewy white bloom on the skin.',
        }

        self.story_eat_kwargs = {
            'number': 1,
            'title': 'Eat an apple a day',
        }
        self.story_grow_kwargs = {
            'number': 2,
            'title': 'Grow an apple a day',
        }
        self.story_throw_kwargs = {
            'number': 3,
            'title': 'Throw an apple a day',
        }

    def tearDown(self):
        logoutCurrentUser()
        self.testbed.deactivate()

    def assertEqualProjectAppleDict(self, project_dict):
        self.assertEqual(project_dict['number'], 1)
        self.assertEqual(project_dict['name'], 'Apple')
        self.assertEqual(project_dict['description'], 'The round fruit of a tree of the rose family.')
        self.assertEqualUserMouseDict(project_dict['owner'])

    def assertEqualProjectAppleTooDict(self, project_dict):
        self.assertEqual(project_dict['number'], 2)
        self.assertEqual(project_dict['name'], 'Apple')
        self.assertEqual(project_dict['description'], 'The round fruit of a tree of the rose family.')
        self.assertEqualUserMouseDict(project_dict['owner'])

    def assertEqualProjectBananaDict(self, project_dict):
        self.assertEqual(project_dict['number'], 2)
        self.assertEqual(project_dict['name'], 'Banana')
        self.assertEqual(project_dict['description'], 'A long curved fruit.')
        self.assertEqualUserMouseDict(project_dict['owner'])

    def assertEqualProjectCoconutDict(self, project_dict):
        self.assertEqual(project_dict['number'], 1)
        self.assertEqual(project_dict['name'], 'Coconut')
        self.assertEqual(project_dict['description'], 'The large, oval, brown seed of a tropical palm.')
        self.assertEqualUserMouseDict(project_dict['owner'])

    def assertEqualProjectDewberryDict(self, project_dict):
        self.assertEqual(project_dict['number'], 2)
        self.assertEqual(project_dict['name'], 'Dewberry')
        self.assertEqual(project_dict['description'],
            'A trailing European bramble (Rubus caesius) with soft prickles and '
            'edible, blackberrylike fruit, which has a dewy white bloom on the skin.')
        self.assertEqualUserMouseDict(project_dict['owner'])

    def assertEqualStoryEatDict(self, story_dict):
        self.assertEqual(story_dict['number'], 1)
        self.assertEqual(story_dict['title'], 'Eat an apple a day')

    def assertEqualStoryGrowDict(self, story_dict):
        self.assertEqual(story_dict['number'], 2)
        self.assertEqual(story_dict['title'], 'Grow an apple a day')

    def assertEqualStoryThrowDict(self, story_dict):
        self.assertEqual(story_dict['number'], 3)
        self.assertEqual(story_dict['title'], 'Throw an apple a day')

    def assertEqualUserMouseDict(self, user_dict):
        self.assertEqual(user_dict['nickname'], 'mouse@lemur.com')
        self.assertEqual(user_dict['email'], 'mouse@lemur.com')
        self.assertEqual(user_dict['user_id'], '114818323877301381352')
        self.assertEqual(user_dict['federated_identity'], None)
        self.assertEqual(user_dict['federated_provider'], None)

    def assertEqualStoryEat(self, story_dict):
        self.assertEqual(story_dict.number, 1)
        self.assertEqual(story_dict.title, 'Eat an apple a day')

    def assertEqualStoryGrow(self, story_dict):
        self.assertEqual(story_dict.number, 2)
        self.assertEqual(story_dict.title, 'Grow an apple a day')


class TestProjectListHandler__OrderBy(BaseTestHandler):

    def setUp(self):
        super(TestProjectListHandler__OrderBy, self).setUp()
        self._order_by_orig = ProjectListOrCreateHandler.order_by

    def tearDown(self):
        ProjectListOrCreateHandler.order_by = self._order_by_orig
        super(TestProjectListHandler__OrderBy, self).tearDown()

    def test_list_projects__no_order_by(self):
        """
        Test that returned projects are order by default (i.e. creation time).
        """
        ProjectListOrCreateHandler.order_by = ()

        project_dewberry = ProjectDummy(**self.project_dewberry_kwargs)
        project_dewberry.put()
        project_coconut = ProjectDummy(**self.project_coconut_kwargs)
        project_coconut.put()
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        project_banana = ProjectDummy(**self.project_banana_kwargs)
        project_banana.put()

        response = self.testapp.get('/projects')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        project_dicts = appenginejson.loads(response.normal_body)
        self.assertEqual(len(project_dicts), 4)

        self.assertEqual(project_dicts[0]['key'], str(project_dewberry.key()))
        self.assertEqualProjectDewberryDict(project_dicts[0])
        self.assertEqual(project_dicts[1]['key'], str(project_coconut.key()))
        self.assertEqualProjectCoconutDict(project_dicts[1])
        self.assertEqual(project_dicts[2]['key'], str(project_apple.key()))
        self.assertEqualProjectAppleDict(project_dicts[2])
        self.assertEqual(project_dicts[3]['key'], str(project_banana.key()))
        self.assertEqualProjectBananaDict(project_dicts[3])

    def test_list_projects__order_by_number(self):
        """
        Test that returned projects are order by number.
        """
        ProjectListOrCreateHandler.order_by = ('number',)

        project_dewberry = ProjectDummy(**self.project_dewberry_kwargs)
        project_dewberry.put()
        project_coconut = ProjectDummy(**self.project_coconut_kwargs)
        project_coconut.put()
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        project_banana = ProjectDummy(**self.project_banana_kwargs)
        project_banana.put()

        response = self.testapp.get('/projects')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        project_dicts = appenginejson.loads(response.normal_body)
        self.assertEqual(len(project_dicts), 4)

        self.assertEqual(project_dicts[0]['key'], str(project_coconut.key()))
        self.assertEqualProjectCoconutDict(project_dicts[0])
        self.assertEqual(project_dicts[1]['key'], str(project_apple.key()))
        self.assertEqualProjectAppleDict(project_dicts[1])
        self.assertEqual(project_dicts[2]['key'], str(project_dewberry.key()))
        self.assertEqualProjectDewberryDict(project_dicts[2])
        self.assertEqual(project_dicts[3]['key'], str(project_banana.key()))
        self.assertEqualProjectBananaDict(project_dicts[3])

    def test_list_projects__order_by_name(self):
        """
        Test that returned projects are order by name.
        """
        ProjectListOrCreateHandler.order_by = ('name',)

        project_dewberry = ProjectDummy(**self.project_dewberry_kwargs)
        project_dewberry.put()
        project_coconut = ProjectDummy(**self.project_coconut_kwargs)
        project_coconut.put()
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        project_banana = ProjectDummy(**self.project_banana_kwargs)
        project_banana.put()

        response = self.testapp.get('/projects')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        project_dicts = appenginejson.loads(response.normal_body)
        self.assertEqual(len(project_dicts), 4)

        self.assertEqual(project_dicts[0]['key'], str(project_apple.key()))
        self.assertEqualProjectAppleDict(project_dicts[0])
        self.assertEqual(project_dicts[1]['key'], str(project_banana.key()))
        self.assertEqualProjectBananaDict(project_dicts[1])
        self.assertEqual(project_dicts[2]['key'], str(project_coconut.key()))
        self.assertEqualProjectCoconutDict(project_dicts[2])
        self.assertEqual(project_dicts[3]['key'], str(project_dewberry.key()))
        self.assertEqualProjectDewberryDict(project_dicts[3])

    def test_list_projects__order_by_number_name(self):
        """
        Test that returned projects are order by number and then name.
        """
        ProjectListOrCreateHandler.order_by = ('number', 'name')

        project_dewberry = ProjectDummy(**self.project_dewberry_kwargs)
        project_dewberry.put()
        project_coconut = ProjectDummy(**self.project_coconut_kwargs)
        project_coconut.put()
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        project_banana = ProjectDummy(**self.project_banana_kwargs)
        project_banana.put()

        response = self.testapp.get('/projects')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        project_dicts = appenginejson.loads(response.normal_body)
        self.assertEqual(len(project_dicts), 4)

        self.assertEqual(project_dicts[0]['key'], str(project_apple.key()))
        self.assertEqualProjectAppleDict(project_dicts[0])
        self.assertEqual(project_dicts[1]['key'], str(project_coconut.key()))
        self.assertEqualProjectCoconutDict(project_dicts[1])
        self.assertEqual(project_dicts[2]['key'], str(project_banana.key()))
        self.assertEqualProjectBananaDict(project_dicts[2])
        self.assertEqual(project_dicts[3]['key'], str(project_dewberry.key()))
        self.assertEqualProjectDewberryDict(project_dicts[3])

    def test_list_projects__order_by_name_number(self):
        """
        Test that returned projects are order by name and then number.
        """
        ProjectListOrCreateHandler.order_by = ('name', 'number')

        project_apple_too = ProjectDummy(**self.project_apple_too_kwargs)
        project_apple_too.put()
        project_dewberry = ProjectDummy(**self.project_dewberry_kwargs)
        project_dewberry.put()
        project_coconut = ProjectDummy(**self.project_coconut_kwargs)
        project_coconut.put()
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        project_banana = ProjectDummy(**self.project_banana_kwargs)
        project_banana.put()

        response = self.testapp.get('/projects')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        project_dicts = appenginejson.loads(response.normal_body)
        self.assertEqual(len(project_dicts), 5)

        self.assertEqual(project_dicts[0]['key'], str(project_apple.key()))
        self.assertEqualProjectAppleDict(project_dicts[0])
        self.assertEqual(project_dicts[1]['key'], str(project_apple_too.key()))
        self.assertEqualProjectAppleTooDict(project_dicts[1])
        self.assertEqual(project_dicts[2]['key'], str(project_banana.key()))
        self.assertEqualProjectBananaDict(project_dicts[2])
        self.assertEqual(project_dicts[3]['key'], str(project_coconut.key()))
        self.assertEqualProjectCoconutDict(project_dicts[3])
        self.assertEqual(project_dicts[4]['key'], str(project_dewberry.key()))
        self.assertEqualProjectDewberryDict(project_dicts[4])


class TestStoryListHandler(BaseTestHandler):

    def test_list_stories(self):
        """
        Test that returned stories are order by number.
        """
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        story_throw = StoryDummy(parent=project_apple, **self.story_throw_kwargs)
        story_throw.put()
        story_eat = StoryDummy(parent=project_apple, **self.story_eat_kwargs)
        story_eat.put()
        story_grow = StoryDummy(parent=project_apple, **self.story_grow_kwargs)
        story_grow.put()

        response = self.testapp.get('/projects/%s/stories' % str(project_apple.key()))
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        story_dicts = appenginejson.loads(response.normal_body)
        self.assertEqual(len(story_dicts), 3)

        self.assertEqual(story_dicts[0]['key'], str(story_eat.key()))
        self.assertEqualStoryEatDict(story_dicts[0])
        self.assertEqual(story_dicts[1]['key'], str(story_grow.key()))
        self.assertEqualStoryGrowDict(story_dicts[1])
        self.assertEqual(story_dicts[2]['key'], str(story_throw.key()))
        self.assertEqualStoryThrowDict(story_dicts[2])


class TestStoryCreateHandler(BaseTestHandler):

    def test_create_story(self):
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()

        response = self.testapp.post_json('/projects/%s/stories' % str(project_apple.key()), self.story_eat_kwargs)
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        story_dict = appenginejson.loads(response.normal_body)
        self.assertEqualStoryEatDict(story_dict)

        story = StoryDummy.get(story_dict['key'])
        self.assertEqualStoryEat(story)

    def test_create_story__blank_number(self):
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        self.story_eat_kwargs['number'] = ''

        response = self.testapp.post_json('/projects/%s/stories' % str(project_apple.key()), self.story_eat_kwargs)
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        story_dict = appenginejson.loads(response.normal_body)
        self.assertEqual(story_dict['number'], None)
        self.assertEqual(story_dict['title'], 'Eat an apple a day')

        story = StoryDummy.get(story_dict['key'])
        self.assertEqual(story.number, None)
        self.assertEqual(story.title, 'Eat an apple a day')

    def test_create_story__none_number(self):
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        self.story_eat_kwargs['number'] = None

        response = self.testapp.post_json('/projects/%s/stories' % str(project_apple.key()), self.story_eat_kwargs)
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        story_dict = appenginejson.loads(response.normal_body)
        self.assertEqual(story_dict['number'], None)
        self.assertEqual(story_dict['title'], 'Eat an apple a day')

        story = StoryDummy.get(story_dict['key'])
        self.assertEqual(story.number, None)
        self.assertEqual(story.title, 'Eat an apple a day')

    def test_create_story__missing_number(self):
        project_apple = ProjectDummy(**self.project_apple_kwargs)
        project_apple.put()
        del self.story_eat_kwargs['number']

        response = self.testapp.post_json('/projects/%s/stories' % str(project_apple.key()), self.story_eat_kwargs)
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        story_dict = appenginejson.loads(response.normal_body)
        self.assertEqual(story_dict['number'], None)
        self.assertEqual(story_dict['title'], 'Eat an apple a day')

        story = StoryDummy.get(story_dict['key'])
        self.assertEqual(story.number, None)
        self.assertEqual(story.title, 'Eat an apple a day')


class BaseTestScrumStoryHandler(BaseTestHandler):

    def setUp(self):
        super(BaseTestScrumStoryHandler, self).setUp()

        self.scrum_story_eat_kwargs = {
            'status': 'ToDo'
        }
        self.scrum_story_grow_kwargs = {
            'status': 'Complete'
        }
        self.scrum_story_throw_kwargs = {
            'status': 'InProgress'
        }

    def assertEqualScrumStoryEatDict(self, scrum_story_dict):
        self.assertEqual(scrum_story_dict['status'], 'ToDo')

    def assertEqualScrumStoryGrowDict(self, scrum_story_dict):
        self.assertEqual(scrum_story_dict['status'], 'Complete')

    def assertEqualScrumStoryThrowDict(self, scrum_story_dict):
        self.assertEqual(scrum_story_dict['status'], 'InProgress')

    def assertEqualScrumStoryEat(self, scrum_story):
        self.assertEqual(scrum_story.status, 'ToDo')

    def assertEqualScrumStoryGrow(self, scrum_story):
        self.assertEqual(scrum_story.status, 'Complete')


class TestScrumStoryListHandler(BaseTestScrumStoryHandler):

    def test_list_scrum_stories(self):
        story_eat = StoryDummy(**self.story_eat_kwargs)
        story_eat.put()
        scrum_story_eat = ScrumStoryDummy(story=story_eat, **self.scrum_story_eat_kwargs)
        scrum_story_eat.put()

        story_grow = StoryDummy(**self.story_grow_kwargs)
        story_grow.put()
        scrum_story_grow = ScrumStoryDummy(story=story_grow, **self.scrum_story_grow_kwargs)
        scrum_story_grow.put()

        story_throw = StoryDummy(**self.story_throw_kwargs)
        story_throw.put()
        scrum_story_throw = ScrumStoryDummy(story=story_throw, **self.scrum_story_throw_kwargs)
        scrum_story_throw.put()

        response = self.testapp.get('/scrum/stories')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        scrum_story_dicts = appenginejson.loads(response.normal_body)
        self.assertEqual(len(scrum_story_dicts), 3)

        self.assertEqual(scrum_story_dicts[0]['key'], str(scrum_story_eat.key()))
        self.assertEqualScrumStoryEatDict(scrum_story_dicts[0])
        self.assertEqualStoryEatDict(scrum_story_dicts[0])
        self.assertEqual(scrum_story_dicts[1]['key'], str(scrum_story_grow.key()))
        self.assertEqualScrumStoryGrowDict(scrum_story_dicts[1])
        self.assertEqualStoryGrowDict(scrum_story_dicts[1])
        self.assertEqual(scrum_story_dicts[2]['key'], str(scrum_story_throw.key()))
        self.assertEqualScrumStoryThrowDict(scrum_story_dicts[2])
        self.assertEqualStoryThrowDict(scrum_story_dicts[2])


class TestScrumStoryCreateHandler(BaseTestScrumStoryHandler):

    def test_create_scrum_story(self):
        scrum_story_eat_kwargs = dict(self.story_eat_kwargs.items() + self.scrum_story_eat_kwargs.items())

        response = self.testapp.post_json('/scrum/stories', scrum_story_eat_kwargs)
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        scrum_story_dict = appenginejson.loads(response.normal_body)
        self.assertEqualScrumStoryEatDict(scrum_story_dict)
        self.assertEqualStoryEatDict(scrum_story_dict)

        scrum_story = ScrumStoryDummy.get(scrum_story_dict['key'])
        self.assertEqualScrumStoryEat(scrum_story)
        self.assertEqualStoryEat(scrum_story.story)


class TestScrumStoryGetHandler(BaseTestScrumStoryHandler):

    def test_get_scrum_story(self):
        story_eat = StoryDummy(**self.story_eat_kwargs)
        story_eat.put()
        scrum_story_eat = ScrumStoryDummy(story=story_eat, **self.scrum_story_eat_kwargs)
        scrum_story_eat.put()

        response = self.testapp.get('/scrum/stories/%s' % str(scrum_story_eat.key()))
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        scrum_story_dict = appenginejson.loads(response.normal_body)
        self.assertEqual(scrum_story_dict['key'], str(scrum_story_eat.key()))
        self.assertEqualScrumStoryEatDict(scrum_story_dict)
        self.assertEqualStoryEatDict(scrum_story_dict)


class TestScrumStoryPutHandler(BaseTestScrumStoryHandler):

    def test_put_scrum_story(self):
        story_eat = StoryDummy(**self.story_eat_kwargs)
        story_eat.put()
        scrum_story_eat = ScrumStoryDummy(story=story_eat, **self.scrum_story_eat_kwargs)
        scrum_story_eat.put()

        scrum_story_grow_kwargs = dict(self.story_grow_kwargs.items() + self.scrum_story_grow_kwargs.items())

        response = self.testapp.put_json('/scrum/stories/%s' % str(scrum_story_eat.key()), scrum_story_grow_kwargs)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        scrum_story_dict = appenginejson.loads(response.normal_body)
        self.assertEqualScrumStoryGrowDict(scrum_story_dict)
        self.assertEqualStoryGrowDict(scrum_story_dict)

        scrum_story = ScrumStoryDummy.get(scrum_story_dict['key'])
        self.assertEqualScrumStoryGrow(scrum_story)
        self.assertEqualStoryGrow(scrum_story.story)

        self.assertEqual(ScrumStoryDummy.all().count(), 1)
        self.assertEqual(StoryDummy.all().count(), 1)


class TestScrumStoryDeleteHandler(BaseTestScrumStoryHandler):

    def test_delete_scrum_story(self):
        story_eat = StoryDummy(**self.story_eat_kwargs)
        story_eat.put()
        scrum_story_eat = ScrumStoryDummy(story=story_eat, **self.scrum_story_eat_kwargs)
        scrum_story_eat.put()

        response = self.testapp.delete('/scrum/stories/%s' % str(scrum_story_eat.key()))
        self.assertEqual(response.status_int, 204)
        self.assertEqual(response.content_type, None)
        self.assertEqual(response.normal_body, '')

        self.assertEqual(ScrumStoryDummy.all().count(), 0)
        self.assertEqual(StoryDummy.all().count(), 0)
