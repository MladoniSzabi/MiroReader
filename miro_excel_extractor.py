import miro_api
import pandas as pd

import miro_helper

from typing import TypedDict, Any
import io


class Node(TypedDict):
    id: str
    ypos: float
    text: str
    numbering: str
    children: list["Node"]


class Edge(TypedDict):
    source: str
    target: str


def connectors_to_edge_list(connectors, nodes: dict[str, Any]) -> list[Edge]:
    retval: list[Edge] = []
    for conn in connectors:
        if conn.start_item.id not in nodes or conn.end_item.id not in nodes:
            continue
        else:
            retval.append({
                "source": conn.start_item.id,
                "target": conn.end_item.id
            })

    return retval


def construct_tree(nodes: dict[str, Any], edges: list[Edge], start) -> Node:
    node: Node = {
        "id": start.id,
        "ypos": start.position.y,
        "text": miro_helper.extract_node_text(start),
        "numbering": "",
        "children": [],
    }

    for edge in edges:
        if edge['source'] == start.id:
            node["children"].append(
                construct_tree(nodes, edges, nodes[edge['target']]))

    node["children"].sort(key=lambda x: x["ypos"])
    return node


def update_numbering(tree: Node, numbering: str = ""):
    tree["numbering"] = numbering
    for index, next in enumerate(tree["children"]):
        if numbering == "":
            update_numbering(next, str(index+1))
        else:
            update_numbering(next, numbering + "." + str(index+1))


def tree_to_table(tree: Node) -> list:
    retval = []
    retval.append([tree["id"], tree["numbering"], tree['text']])
    for child in tree["children"]:
        retval += tree_to_table(child)
    return retval


def extract_tree(access_token: str, board_id: str, frame_id: str, start_node_id: str) -> Node:
    miro = miro_api.MiroApi(access_token)
    nodes = miro_helper.get_all_instances_cursor(
        miro.get_items_within_frame, board_id, frame_id)
    connectors = connectors = miro_helper.get_all_instances_cursor(
        miro.get_connectors, board_id)

    nodes_dict = {}
    for node in nodes:
        nodes_dict[node.id] = node

    edges = connectors_to_edge_list(connectors, nodes_dict)
    # print(start_node_id, nodes_dict.keys())
    if start_node_id not in nodes_dict:
        raise Exception("Start node not found")

    tree = construct_tree(nodes_dict, edges, nodes_dict[start_node_id])
    update_numbering(tree)
    return tree


def extract_excel(access_token: str, board_id: str, frame_id: str, start_node_id: str) -> bytes:
    tree = extract_tree(access_token, board_id, frame_id, start_node_id)

    tree_rows = []
    for child in tree["children"]:
        tree_rows += tree_to_table(child)

    extra_excel_columns = [
        "Type",
        "Subtype",
        "Format",
        "Req",
        "DependentReq",
        "Depend on",
        "Description",
        "Reference",
        "Recommended schema links",
        "Example data"
    ]

    rows = []
    for row in tree_rows:
        rows.append(row + ["" for _ in extra_excel_columns])

    df = pd.DataFrame(
        rows, columns=["Miro node id", "Numbering", "Property"] + extra_excel_columns)

    bytesobj = io.BytesIO()
    with pd.ExcelWriter(bytesobj) as writer:
        df.to_excel(writer, index=False)
    bytesobj.seek(0)
    return bytesobj.read()
