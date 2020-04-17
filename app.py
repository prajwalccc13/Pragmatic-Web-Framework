from api import API
from middleware import Middleware

app = API()

@app.route('/')
@app.route("/home")
def home(request, response):
    response.body = app.template("index.html").encode()


@app.route("/about")
def about(request, response):
    response.text = "Hello from the about page"


@app.route("/hello/{age:d}")
def greeting(request, response, name):
    response.text = f"Hello, {d}"


@app.route("/book")
class BookResource:
    def get(self, request, response):
        response.text = "Books Page"


@app.route("/template")
def template_handler(request, response):
    response.body = app.template("template.html", context={"name": "Pragmatic", "title": "Framework"}).encode()


def custom_exception_handler(request, response, exception_cls):
    response.text = "Ooops! Something went wrong, plese contact our customer service"

app.add_exception_handler(custom_exception_handler)


# @app.route('/home')
# def exception_throwing_handler(request, response):
#     raise AssertionError("This handler should not be user")


class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Processing Request", req.url)

    def process_respose(self, req, res):
        print("Processing Respose", req.url)

app.add_middleware(SimpleCustomMiddleware)