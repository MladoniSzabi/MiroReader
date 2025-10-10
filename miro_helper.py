import miro_api

from html.parser import HTMLParser


def extract_node_text(node) -> str:
    class NameExtractor(HTMLParser):
        def __init__(self, *, convert_charrefs: bool = True) -> None:
            super().__init__(convert_charrefs=convert_charrefs)
            self.collected = ""

        def handle_data(self, data):
            self.collected += data + " "

    html = node.data.actual_instance.content
    parser = NameExtractor()
    parser.feed(html)
    return parser.collected.strip()


def get_all_instances_page(func, *args, **kwargs) -> list:
    collection = []
    response = None
    while response == None or len(collection) < response.total:
        response = func(*args, **kwargs)
        for el in response.data:
            collection.append(el)
        kwargs["offset"] = str(response.offset + response.limit)
    return collection


def get_all_instances_cursor(func, *args, **kwargs) -> list:
    collection = []
    response = None
    while response == None or response.cursor != None:
        response = func(*args, **kwargs)
        for el in response.data:
            collection.append(el)
        kwargs["cursor"] = response.cursor
    return collection
