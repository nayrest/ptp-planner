from ptp.loader import load_network
from ptp.gm import gm_candidates, reach_table, choose_gm

T = 520   # бюджет из задачи


def test_bs_total():
    links, bs = load_network("examples/lesson2.json")
    assert sum(bs.values()) == 1100


def test_candidates():
    links, bs = load_network("examples/lesson2.json")
    assert gm_candidates(links) == {"1", "2", "3", "4"}


def test_gm4_cannot_reach_6():
    links, bs = load_network("examples/lesson2.json")
    table = reach_table(links, gm_candidates(links), T)
    assert "6" not in table["4"]      # 580 > 520, ты считал это руками
    assert table["2"]["6"] == 440
    assert table["1"]["6"] == 510

def test_choose_gm():
    links, bs = load_network("examples/lesson2.json")
    table = reach_table(links, gm_candidates(links), T)
    gms, assignment, load = choose_gm(bs, table)

    assert gms == ["1", "2", "3"]              # как ты получил руками
    assert sum(load.values()) == 1100           # все БС распределены
    assert all(x <= 500 for x in load.values()) # лимит 500 соблюдён
    for site, (primary, backup) in assignment.items():
        assert primary != backup                # резерв на другой площадке
        assert site in table[primary] and site in table[backup]


def test_no_backup_with_budget_500():
    # при бюджете 500 до площадки 6 дотягивается только GM 2 — резерва нет
    links, bs = load_network("examples/lesson2.json")
    table = reach_table(links, gm_candidates(links), 500)
    assert choose_gm(bs, table) is None