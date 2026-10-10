"""Поиск PTP-путей и расчёт задержек (алгоритм Дейкстры)."""
import heapq

# ---------- Параметры (мкс) ----------
D_NODE = 20          # каждый маршрутизатор / блок РРЛ на пути
D_LINK = {
    "fo": 50,        # оптика между площадками
    "rrl": 190,      # пролёт РРЛ (150) + два блока РРЛ (2 × 20)
}
T_MAX = 1500         # бюджет задержки


def build_graph(links):
    """Список смежности: {узел: [(сосед, тип_линка), ...]}. Линки двунаправленные."""
    graph = {}
    for u, v, kind in links:
        graph.setdefault(u, []).append((v, kind))
        graph.setdefault(v, []).append((u, kind))
    return graph


def dijkstra(graph, start):
    """dist[v] — минимальная задержка от start до v (с учётом всех узлов на пути),
    prev[v] — предыдущий узел на лучшем пути."""
    dist = {v: float("inf") for v in graph}
    prev = {v: None for v in graph}
    dist[start] = D_NODE                    # маршрутизатор с GM уже вносит задержку

    heap = [(dist[start], start)]
    visited = set()

    while heap:
        d, v = heapq.heappop(heap)
        if v in visited:
            continue
        visited.add(v)

        for u, kind in graph[v]:
            step = D_LINK[kind] + D_NODE    # линк + маршрутизатор, в который пришли
            if d + step < dist[u]:          # релаксация
                dist[u] = d + step
                prev[u] = v
                heapq.heappush(heap, (dist[u], u))

    return dist, prev


def restore_path(prev, target):
    """Восстанавливает путь от старта до target по словарю prev (обратный ход)."""
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    path.reverse()
    return path


def path_delay(path, links):
    """Задержка заданного пути: 20 × число узлов + сумма задержек линков."""
    kinds = {}
    for u, v, kind in links:
        kinds[(u, v)] = kind
        kinds[(v, u)] = kind
    total = D_NODE * len(path)
    for a, b in zip(path, path[1:]):
        total += D_LINK[kinds[(a, b)]]
    return total