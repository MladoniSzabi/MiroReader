import miro_api
import dotenv
from flask import Flask, request, redirect

dotenv.load_dotenv()
app = Flask(__name__)

miro = miro_api.Miro()

access_token = None


@app.route("/")
def index():
    if not miro.is_authorized:
        return redirect(miro.auth_url)
    return ""


@app.route("/miro/redirect/url")
def miro_redirect():
    code = request.args.get("code")
    state = request.args.get("state")
    client_id = request.args.get("client_id")
    team_id = request.args.get("team_id")
    access_token = miro.exchange_code_for_access_token(code)
    return f"<html><body><h1>Hello, world!</h1><p>Your access token is {access_token}</p></body></html>"


@app.route("/get/board")
def get_board_frames():
    if not miro.is_authorized:
        return redirect(miro.auth_url)
    boards = miro.api.get_boards()
    board_id = boards.data[0].id
    frame_id = miro.api.get_items(board_id, type="frame").data[0].id
    objects = miro.api.get_items_within_frame(board_id, frame_id)
    return str(objects.data)


@app.route("/get/connectors")
def get_connectors():
    if not miro.is_authorized:
        return redirect(miro.auth_url)
    boards = miro.api.get_boards()
    board_id = boards.data[0].id
    connectors = miro.api.get_connectors(board_id)
    return str(connectors)


app.run()
