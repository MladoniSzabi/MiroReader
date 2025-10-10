import miro_helper
import miro_excel_extractor

import miro_api
import dotenv
from flask import Flask, request, redirect, make_response, render_template
from werkzeug import Response

import json
from functools import wraps

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
        except miro_api.exceptions.UnauthorizedException:  # type: ignore
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
    response = redirect("/")
    response.set_cookie("miro_token", access_token, secure=True)
    return response


@app.route("/get/boards")
@auth_required
def get_boards() -> Response:
    miro = miro_api.MiroApi(request.cookies.get("miro_token", ""))
    boards = miro_helper.get_all_instances_page(miro.get_boards, limit="2")
    retval = []
    for board in boards:
        retval.append({
            "name": board.name,
            "id": board.id
        })
    response = Response(json.dumps(retval), mimetype="text/json")
    return response


@app.route("/get/board/<string:board_id>/frames")
@auth_required
def get_frames(board_id: str) -> Response:
    miro = miro_api.MiroApi(request.cookies.get("miro_token", ""))
    frames = miro_helper.get_all_instances_cursor(
        miro.get_items, board_id, type="frame")
    retval = []
    for frame in frames:
        retval.append({
            "name": frame.data.actual_instance.title,
            "id": frame.id
        })
    response = Response(json.dumps(retval), mimetype="text/json")
    return response


@app.route("/get/board/<string:board_id>/frame/<string:frame_id>/objects")
def get_objects(board_id: str, frame_id: str) -> Response:
    miro = miro_api.MiroApi(request.cookies.get("miro_token", ""))
    objects = miro_helper.get_all_instances_cursor(
        miro.get_items_within_frame, board_id, frame_id)
    retval = []
    for obj in objects:
        retval.append({
            "name": miro_helper.extract_node_text(obj),
            "id": obj.id
        })
    response = Response(json.dumps(retval), mimetype="text/json")
    return response


@app.route("/get/board/<string:board_id>/frame/<string:frame_id>/object/<string:object_id>/excel")
def get_excel(board_id: str, frame_id: str, object_id: str) -> Response:
    access_token = request.cookies.get("miro_token", "")
    bytes = miro_excel_extractor.extract_excel(
        access_token, board_id, frame_id, object_id)
    response = Response(bytes, mimetype="application/vnd.ms-excel")
    response.headers.add("Content-Disposition",
                         "attachment; filename=\"schema.xlsx\"")
    return response
