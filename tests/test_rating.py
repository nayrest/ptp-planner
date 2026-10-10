import json
from ptp.rating import rank_links, effect_within_budget


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    importance = {s["id"]: s["importance"] for s in data["sites"]}
    return data["links"], importance, data["gm"]


def test_ranking_by_packages():
    links, imp, gm = load("examples/lesson3.json")
    assert rank_links(links, imp, gm) == ["e1", "e2", "e3", "e5", "e4"]


def test_budget_50_packages_vs_single():
    links, imp, gm = load("examples/lesson3.json")
    packages = rank_links(links, imp, gm)
    single = ["e4", "e1", "e5", "e2", "e3"]       # поштучный рейтинг, ты считал его руками
    assert effect_within_budget(links, imp, gm, packages, 50) == 120
    assert effect_within_budget(links, imp, gm, single, 50) == 55