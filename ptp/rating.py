"""Рейтинг модернизации линков: жадный выбор «пакетов» по эффекту на рубль."""
import heapq


def reachable(links, ready, start):
    """Множество узлов, до которых можно дойти от start только по готовым линкам.
    links — список словарей {"id", "u", "v", "cost"}, ready — множество id готовых линков."""
    adj = {}
    for link in links:
        if link["id"] in ready:
            adj.setdefault(link["u"], []).append(link["v"])
            adj.setdefault(link["v"], []).append(link["u"])
    seen = {start}
    stack = [start]
    while stack:                      # обход графа «в глубину»
        v = stack.pop()
        for u in adj.get(v, []):
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return seen


def package_to(links, ready, start, target):
    """Самый дешёвый набор НЕготовых линков, чтобы дойти от start до target.
    Это твоя Дейкстра, только вес линка — не задержка, а стоимость:
    готовый линк стоит 0, неготовый — свою цену. Возвращает список id в порядке от GM."""
    adj = {}
    for link in links:
        w = 0 if link["id"] in ready else link["cost"]
        adj.setdefault(link["u"], []).append((link["v"], w, link["id"]))
        adj.setdefault(link["v"], []).append((link["u"], w, link["id"]))

    dist = {start: 0}
    prev = {start: None}
    heap = [(0, start)]
    done = set()
    while heap:
        d, v = heapq.heappop(heap)
        if v in done:
            continue
        done.add(v)
        for u, w, link_id in adj.get(v, []):
            if d + w < dist.get(u, float("inf")):      # та же релаксация
                dist[u] = d + w
                prev[u] = (v, link_id)
                heapq.heappush(heap, (dist[u], u))

    if target not in dist:
        return None
    path = []
    node = target
    while prev[node] is not None:                       # тот же обратный ход
        v, link_id = prev[node]
        path.append(link_id)
        node = v
    path.reverse()
    return [link_id for link_id in path if link_id not in ready]


def rank_links(links, importance, gm):
    """Рейтинг: список id линков в порядке модернизации."""
    cost = {link["id"]: link["cost"] for link in links}
    ready = set()
    ranking = []

    while True:
        connected = reachable(links, ready, gm)        # уже подключённые площадки
        best = None                                     # (эффективность, польза, пакет)

        for site in sorted(importance):
            if site in connected:
                continue
            package = package_to(links, ready, gm, site)
            if not package:
                continue

            # что станет подключено, если модернизировать пакет
            new_connected = reachable(links, ready | set(package), gm)

            gain = sum(importance.get(s, 0) for s in new_connected - connected)

            price = sum(cost[l] for l in package)

            eff = gain / price

            if best is None or eff > best[0]:
                best = (eff, gain, package)

        if best is None:                                # подключать больше нечего
            break
        ranking.extend(best[2])                         # линки пакета — в рейтинг
        ready |= set(best[2])                           # и считаем их готовыми

    return ranking


def effect_within_budget(links, importance, gm, ranking, budget):
    """Идём по рейтингу сверху вниз, пока хватает денег.
    Возвращает суммарную важность подключённых площадок."""
    cost = {link["id"]: link["cost"] for link in links}
    spent = 0
    ready = set()
    for link_id in ranking:
        if spent + cost[link_id] > budget: break
        spent += cost[link_id]
        ready.add(link_id)
    connected = reachable(links, ready, gm)
    return sum(importance.get(s, 0) for s in connected)