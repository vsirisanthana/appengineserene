from google.appengine.ext import db

def to_dict(model_instance, recursive=False):
    dictionary = {'key': unicode(model_instance.key())}
    for key, prop in model_instance.properties().items():
        value = getattr(model_instance, key)
        if isinstance(prop, db.ReferenceProperty):
            dictionary[key] = to_dict(value) if recursive else value
        else:
            dictionary[key] = value
    return dictionary

def flatten_to_dict(model_instance, flatten_keys):
    model_instance_dict = to_dict(model_instance)
    dictionary = {}
    for key in reversed(flatten_keys):
        dictionary.update(to_dict(model_instance_dict.pop(key)))
    dictionary.update(model_instance_dict)
    return dictionary