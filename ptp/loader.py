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

def load_network(path):
    """Возвращает (links, bs): список линков и словарь {площадка: число БС}."""
    links = load_links(path)          # линки читаем уже готовой функцией

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    bs = {}
    for site in data["sites"]:
        bs[site["id"]] = site["bs"]

    return links, bs