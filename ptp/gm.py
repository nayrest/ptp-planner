from ptp.paths import build_graph, dijkstra

import math
import itertools


def gm_candidates(links):
    """Узлы, у которых есть хотя бы один оптический линк ("fo")."""
    result = set()
    for u, v, kind in links:
        if kind == "fo":
            result.add(u)
            result.add(v)
    return result


def reach_table(links, candidates, t_max):
    """Для каждого кандидата — до каких площадок он дотягивается в пределах t_max.
    Результат: {кандидат: {площадка: задержка, ...}, ...}"""
    graph = build_graph(links)
    table = {}
    for g in candidates:
        dist, prev = dijkstra(graph, g)
        reach = {}
        for site, d in dist.items():
            if d <= t_max:
                reach[site] = d
        table[g] = reach
    return table

def assign(bs, table, chosen, cap):
    """Распределяет площадки по выбранным GM.
    Возвращает (назначения, нагрузки) или None, если распределить нельзя.
    назначения: {площадка: (основной, резервный)}, нагрузки: {GM: число БС}"""
    load = {g: 0 for g in chosen}         # у каждого GM пока 0 БС
    result = {}

    # Сначала крупные площадки: их сложнее всего куда-то впихнуть
    for site in sorted(bs, key=lambda s: -bs[s]):

        options = [g for g in chosen if site in table[g]]

        if len(options) < 2:              # нет резерва — набор не подходит
            return None

        free = [g for g in options if load[g]+bs[site]<=cap]

        if not free:
            return None

        # Основной: наименее загруженный, при равенстве — ближайший
        primary = min(free, key=lambda g: (load[g], table[g][site], g))
        # Резервный: ближайший из остальных
        backup = min([g for g in options if g != primary],
                     key=lambda g: (table[g][site], g))

        load[primary] += bs[site]
        result[site] = (primary, backup)

    return result, load


def choose_gm(bs, table, cap=500, gm_min=2):
    """Минимальный набор GM. Возвращает (список GM, назначения, нагрузки) или None."""
    lb = max(gm_min, math.ceil(sum(bs.values()) / cap))

    cands = sorted(table)
    for k in range(lb, len(cands) + 1):
        for chosen in itertools.combinations(cands, k):
            r = assign(bs, table, chosen, cap)
            if r is not None:
                return list(chosen), r[0], r[1]
    return None