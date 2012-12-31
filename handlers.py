import webapp2
from google.appengine.ext import db

import appenginejson
from appenginevalidation import clean

from appengineserene.errors import Http4xx
from appengineserene.parsers import parse
from appengineserene.utils import flatten_to_dict


class BaseHandler(webapp2.RequestHandler):
    model = None
    parent_model = None
    group_property = None
    expanded_properties = ()

    def _method(self, do_method, success_status=None, parse_method=None, *args, **kwargs):
        if parse_method:
            parse_method(self.request)
        try:
            result = do_method(*args, **kwargs)
        except db.BadKeyError:
            self.error(404)
            self.response.out.write(appenginejson.dumps('Error 404 Not Found'))
        except Http4xx as e:
            self.error(e.status_code)
            self.response.out.write(appenginejson.dumps(e.message))
        else:
            if success_status:
                self.response.set_status(success_status)
            self.response.out.write(appenginejson.dumps(result))
        self.response.headers['Content-Type'] = 'application/json'

    def get(self, *args, **kwargs):
        self._method(self.do_get, *args, **kwargs)

    def post(self, *args, **kwargs):
        self._method(self.do_post, 201, parse, *args, **kwargs)

    def put(self, *args, **kwargs):
        self._method(self.do_put, None, parse, *args, **kwargs)

    def delete(self, *args, **kwargs):
        self._method(self.do_delete, 204, *args, **kwargs)
        if self.response.status_int == 204:
            del self.response.headers['Content-Type']
            self.response.clear()

    def do_get(self, *args, **kwargs):
        raise NotImplementedError

    def do_post(self, *args, **kwargs):
        raise NotImplementedError

    def do_put(self, *args, **kwargs):
        raise NotImplementedError

    def do_delete(self, *args, **kwargs):
        raise NotImplementedError



class ListHandler(BaseHandler):
    order_by = ()

    def do_get(self, parent_key=None, **kwargs):
        query_str = '' if not self.order_by else 'ORDER BY ' + ', '.join(self.order_by)
        if self.group_property:
            group_model_instance = self.model.properties()[self.group_property].reference_class.get(parent_key)
            query_str = 'WHERE %s = :1 ' % self.group_property + query_str
            model_instances = [model_instance for model_instance in
                               self.model.gql(query_str, group_model_instance)]
        elif self.parent_model:
            parent_model_instance = self.parent_model.get(parent_key)
            query_str = 'WHERE ANCESTOR IS :1 ' + query_str
            model_instances = [model_instance for model_instance in
                               self.model.gql(query_str, parent_model_instance)]
        else:
            model_instances = [model_instance for model_instance in self.model.gql(query_str)]

        if self.expanded_properties:
            model_instances = [flatten_to_dict(model_instance, self.expanded_properties) for model_instance in model_instances]
        return model_instances


class CreateHandler(BaseHandler):

    def do_post(self, parent_key=None, **kwargs):
        content = clean(self.request.CONTENT, self.model)
        if self.parent_model:
            parent_model_instance = self.parent_model.get(parent_key)
            content['parent'] = parent_model_instance

        if self.group_property:
            group_model_instance = self.model.properties()[self.group_property].reference_class.get(parent_key)
            content[self.group_property] = group_model_instance

        if self.expanded_properties:
            for prop_name in self.expanded_properties:
                expanded_model = getattr(self.model, prop_name).reference_class
                expanded_content = clean(self.request.CONTENT, expanded_model)
                expanded_model_instance = expanded_model(**expanded_content)
                expanded_model_instance.put()
                content[prop_name] = expanded_model_instance

        model_instance = self.model(**content)
        model_instance.put()
        if self.expanded_properties:
            return flatten_to_dict(model_instance, self.expanded_properties)
        else:
            return model_instance


class ListOrCreateHandler(ListHandler, CreateHandler):
    pass


class GetHandler(BaseHandler):

    def do_get(self, key, **kwargs):
        model_instance = self.model.get(key)
        if self.expanded_properties:
            return flatten_to_dict(model_instance, self.expanded_properties)
        else:
            return model_instance


class PutHandler(BaseHandler):

    def do_put(self, key, **kwargs):
        model_instance = self.model.get(key)
        content = clean(self.request.CONTENT, self.model)

        if self.expanded_properties:
            for prop_name in self.expanded_properties:
                prop = getattr(model_instance, prop_name)
                expanded_model = getattr(self.model, prop_name).reference_class
                expanded_content = clean(self.request.CONTENT, expanded_model)
                for k, v in expanded_content.items():
                    # TODO: Move 'key' check somewhere else
                    if k != 'key':
                        setattr(prop, k, v)
                prop.put()
                content[prop_name] = prop

        for k, v in content.items():
            # TODO: Move 'key' check somewhere else
            if k != 'key':
                setattr(model_instance, k, v)
        model_instance.put()
        if self.expanded_properties:
            return flatten_to_dict(model_instance, self.expanded_properties)
        else:
            return model_instance


class DeleteHandler(BaseHandler):

    def do_delete(self, key, **kwargs):
        model_instance = self.model.get(key)
        if self.expanded_properties:
            for prop_name in self.expanded_properties:
                prop = getattr(model_instance, prop_name)
                prop.delete()
        model_instance.delete()
        return None


class InstanceHandler(GetHandler, PutHandler, DeleteHandler):
    pass