import json

def load_links(path):
    """Читает JSON-файл с сетью и возвращает список линков
    в том же виде, что LINKS в тесте: [("A", "B", "fo"), ...]"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)       # data — это словарь, как в JSON-файле

    links = []
    for link in data["links"]:
        links.append((link["u"], link["v"], link["kind"]))

    return links