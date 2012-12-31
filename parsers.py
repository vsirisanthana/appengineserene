import json
from urlparse import parse_qsl
from webob.multidict import MultiDict

from serene.errors import ContentTypeNotSupportedError


parsers = {}


def parse(request):
    content_type = request.content_type
    parser = parsers.get(content_type)
    if not parser:
        raise ContentTypeNotSupportedError
    parser.parse(request)

def register(parser):
    parsers[parser.content_type] = parser

def deregister(parser):
    del parsers[parser.parser.content_type]


class Parser:

    @classmethod
    def parse(cls, request):
        raise NotImplementedError


class JsonParser(Parser):
    content_type = 'application/json'

    @classmethod
    def parse(cls, request):
        request.CONTENT = json.loads(request.body)


class FormURLEncodedParser(Parser):
    content_type = 'application/x-www-form-urlencoded'

    @classmethod
    def parse(cls, request):
        request.CONTENT = MultiDict(parse_qsl(request.body))


register(JsonParser)
register(FormURLEncodedParser)