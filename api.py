from webob import Request, Response
from parse import parse
import inspect
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
import os
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise
from middleware import Middleware

from static import cut_static_root, request_for_static


class API:
    def __init__(self, templates_dir="templates", static_dir="static"):
        self.routes = {}
        self.templates_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))
        self.exception_handler = None
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)
        self.static_dir = os.path.abspath(static_dir)
        self._static_root = "/static"

        self.middleware = Middleware(self)


    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)

        return response(environ, start_response)


    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]

        if request_for_static(path_info, self._static_root):
            environ["PATH_INFO"] = cut_static_root(path_info, self._static_root)
            return self.whitenoise(environ, start_response)

        return self.middleware(environ, start_response)

    
    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)


    def route(self, path):

        def wrapper(handler):
            self.add_route(path, handler)
            return handler
        
        return wrapper

    
    def add_route(self, path, handler):
        assert path not in self.routes, f"{path} already exists."

        self.routes[path] = handler

    
    def test_session(self,base_url="http:''testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session


    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method in not allowed", request.method)
                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)

        return response

    
    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found"

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named

        return None, None


    def template(self, template_name, context=None):
        if context is None:
            context = {}

        return self.templates_env.get_template(template_name).render(**context)


    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler
        

