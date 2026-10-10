from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ptp.gm import gm_candidates, reach_table, choose_gm
from ptp.rating import rank_links, effect_within_budget

app = FastAPI(title="PTP Planner")


# ---------- Модели входных данных ----------
# Pydantic сам проверит JSON: если поле не того типа — вернёт ошибку 422.

class Site(BaseModel):
    id: str
    bs: int = 0               # число БС (для выбора GM)
    importance: float = 0     # важность (для рейтинга)


class Link(BaseModel):
    u: str
    v: str
    kind: str = "fo"          # "fo" или "rrl"
    id: str | None = None     # нужен для рейтинга
    cost: float = 0           # стоимость модернизации


class GMRequest(BaseModel):
    sites: list[Site]
    links: list[Link]
    t_max: int = 1500
    cap: int = 500


class RatingRequest(BaseModel):
    gm: str
    sites: list[Site]
    links: list[Link]
    budget: float | None = None


# ---------- Эндпоинты ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/gm")
def plan_gm(req: GMRequest):
    links = []
    for link in req.links:
        links.append((link.u, link.v, link.kind))

    bs = {}
    for site in req.sites:
        bs[site.id] = site.bs

    table = reach_table(links, gm_candidates(links), req.t_max)
    result = choose_gm(bs, table, req.cap)
    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Невозможно разместить GM: у части площадок нет резерва или не хватает ёмкости",
        )

    gms, assignment, load = result
    return {
        "gms": gms,
        "assignment": {site: {"primary": p, "backup": b}
                       for site, (p, b) in assignment.items()},
        "load": load,
    }


@app.post("/rating")
def plan_rating(req: RatingRequest):
    links = [link.model_dump() for link in req.links]       # объекты → словари
    importance = {site.id: site.importance for site in req.sites}

    ranking = rank_links(links, importance, req.gm)
    response = {"ranking": ranking}
    if req.budget is not None:
        response["effect"] = effect_within_budget(
            links, importance, req.gm, ranking, req.budget)
    return response