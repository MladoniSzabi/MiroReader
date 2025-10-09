import miro_api
import dotenv
from flask import Flask, request, redirect, make_response

from functools import wraps

dotenv.load_dotenv()
app = Flask(__name__)


def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if request.cookies.get("miro_token") == None:
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
def index():
    return ""


@app.route("/miro/redirect/url")
def miro_redirect():
    code = request.args.get("code")
    miro = miro_api.Miro()
    access_token = miro.exchange_code_for_access_token(code)
    response = make_response(
        "<html><body><h1>Hello, world!</h1></body></html>")
    response.set_cookie("miro_token", access_token, secure=True)
    return response


@app.route("/get/board")
@auth_required
def get_board_frames():
    miro = miro_api.MiroApi(request.cookies.get("miro_token"))
    boards = miro.get_boards()
    board_id = boards.data[0].id
    frame_id = miro.get_items(board_id, type="frame").data[0].id
    objects = miro.get_items_within_frame(board_id, frame_id)
    return str(objects.data)


@app.route("/get/connectors")
@auth_required
def get_connectors():
    miro = miro_api.MiroApi(request.cookies.get("miro_token"))
    boards = miro.get_boards()
    board_id = boards.data[0].id
    connectors = miro.get_connectors(board_id)
    return str(connectors)


app.run()
