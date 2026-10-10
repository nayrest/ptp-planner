from ptp.paths import build_graph, dijkstra, restore_path, path_delay

LINKS = [
    ("A", "B", "fo"), ("A", "C", "fo"), ("B", "D", "rrl"),
    ("C", "D", "fo"), ("D", "E", "fo"), ("C", "E", "rrl"),
    ("E", "F", "rrl"),
]

def test_delay_to_F():
    dist, prev = dijkstra(build_graph(LINKS), "A")
    assert dist["F"] == 440

def test_best_path():
    dist, prev = dijkstra(build_graph(LINKS), "A")
    assert restore_path(prev, "F") == ["A", "C", "D", "E", "F"]

def test_fewer_links_is_slower():
    assert path_delay(["A", "C", "E", "F"], LINKS) == 510