import miro_api
import dotenv
from flask import Flask, request, redirect, make_response, render_template, Response

import json
from functools import wraps
from html.parser import HTMLParser

dotenv.load_dotenv()
app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="static",
    template_folder="templates"
)


def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if request.cookies.get("miro_token") == None:
            if "text/json" in request.headers.get("Accept", ""):
                return json.dumps({"error": 403})
            miro = miro_api.Miro()
            return redirect(miro.auth_url)
        try:
            result = func(*args, **kwargs)
            return result
        except miro_api.exceptions.UnauthorizedException:
            miro = miro_api.Miro()
            return redirect(miro.auth_url)
    return inner


@app.route("/")
@auth_required
def index() -> str:
    return render_template("index.html")


@app.route("/miro/redirect/url")
def miro_redirect() -> Response:
    code = request.args.get("code")
    miro = miro_api.Miro()
    access_token = miro.exchange_code_for_access_token(code)
    response = make_response(
        "<html><body><h1>Hello, world!</h1></body></html>")
    response.set_cookie("miro_token", access_token, secure=True)
    return response


@app.route("/get/boards")
@auth_required
def get_boards() -> Response:
    miro = miro_api.MiroApi(request.cookies.get("miro_token"))
    boards = miro.get_boards()
    retval = []
    for board in boards.data:
        retval.append({
            "name": board.name,
            "id": board.id
        })
    response = Response(json.dumps(retval), mimetype="text/json")
    return response


@app.route("/get/board/<string:board_id>/frames")
@auth_required
def get_frames(board_id: str) -> Response:
    miro = miro_api.MiroApi(request.cookies.get("miro_token"))
    frames = miro.get_items(board_id, type="frame")
    retval = []
    for frame in frames.data:
        retval.append({
            "name": frame.data.actual_instance.title,
            "id": frame.id
        })
    response = Response(json.dumps(retval), mimetype="text/json")
    return response


def extract_data(html: str) -> str:
    class NameExtractor(HTMLParser):
        def handle_starttag(self, tag, attrs):
            pass

        def handle_endtag(self, tag):
            pass

        def handle_data(self, data):
            self.collected += data + " "

    parser = NameExtractor()
    parser.collected = ""
    parser.feed(html)
    return parser.collected.strip()


@app.route("/get/board/<string:board_id>/frame/<string:frame_id>/objects")
def get_objects(board_id: str, frame_id: str) -> Response:
    miro = miro_api.MiroApi(request.cookies.get("miro_token"))
    objects = miro.get_items_within_frame(board_id, frame_id)
    retval = []
    for obj in objects.data:
        retval.append({
            "name": extract_data(obj.data.actual_instance.content),
            "id": obj.id
        })
    response = Response(json.dumps(retval), mimetype="text/json")
    return response


@app.route("/get/board/<string:board_id>/frame/<string:frame_id>/object/<string:object_id>/excel")
def get_excel(board_id: str, frame_id: str, object_id: str) -> Response:
    pass


@app.route("/get/connectors")
@auth_required
def get_connectors():
    miro = miro_api.MiroApi(request.cookies.get("miro_token"))
    boards = miro.get_boards()
    board_id = boards.data[0].id
    connectors = miro.get_connectors(board_id)
    return str(connectors)


app.run()
