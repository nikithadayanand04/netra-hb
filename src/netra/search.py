"""Cheapest screening protocol search. A state is (site, sorted feature indices); every site has its own dataset.
objective(state) = metric(3-fold grouped CV logistic regression) - photo cost - feature cost."""
import heapq
import math
import time
from dataclasses import dataclass, field

import numpy as np
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedGroupKFold

import config
from netra.tuning import sens_floor_threshold

FUSION = "palm+nail"
State = tuple[str, tuple[int, ...]]


@dataclass
class SiteData:
    X: np.ndarray
    y: np.ndarray
    groups: np.ndarray
    names: list[str]
    folds: list = field(default_factory=list)

    def __post_init__(self):
        if not self.folds:
            self.folds = inner_folds(self.y, self.groups)

    def subset(self, idx: np.ndarray) -> "SiteData":
        return SiteData(self.X[idx], self.y[idx], self.groups[idx], self.names)


def inner_folds(y: np.ndarray, groups: np.ndarray, n_folds: int = config.SEARCH_FOLDS,
                seed: int = config.SEED) -> list[tuple[np.ndarray, np.ndarray]]:
    cv = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    return list(cv.split(np.zeros(len(y)), y, groups))


def photo_cost(site: str) -> float:
    return sum(config.PHOTO_COST[s] for s in site.split("+"))


def penalty(site: str, n_features: int) -> float:
    return config.PHOTO_COST_WEIGHT * photo_cost(site) + config.FEATURE_COST * n_features


def _fit(X: np.ndarray, y: np.ndarray):
    mu, sd = X.mean(0), X.std(0) + 1e-12
    lr = LogisticRegression(class_weight="balanced", max_iter=1000).fit((X - mu) / sd, y)
    return lambda Z: lr.predict_proba((Z - mu) / sd)[:, 1]


def oof_proba(X: np.ndarray, y: np.ndarray, folds) -> np.ndarray:
    p = np.empty(len(y))
    for tr, te in folds:
        p[te] = _fit(X[tr], y[tr])(X[te])
    return p


def spec_at_sens(y: np.ndarray, p: np.ndarray, floor: float = config.SENS_FLOOR) -> float:
    fpr, tpr, _ = roc_curve(y, p)
    return float(1 - fpr[tpr >= floor].min())


def score(y: np.ndarray, p: np.ndarray, metric: str) -> float:
    return spec_at_sens(y, p) if metric == "spec_at_sens" else float(roc_auc_score(y, p))


def _score_chunk(X, y, folds, metric, feat_lists) -> list[float]:
    return [score(y, oof_proba(X[:, list(f)], y, folds), metric) for f in feat_lists]


def resub_upper(d: SiteData, metric: str) -> float:
    """Optimistic bound for A*: all of the site's features, fitted and scored on the same rows."""
    return score(d.y, _fit(d.X, d.y)(d.X), metric)


# ---------- state space ----------
class Space:
    def __init__(self, sites: dict[str, SiteData], max_features: int = config.SEARCH_MAX_FEATURES):
        self.sites = list(sites)
        self.n = {s: len(d.names) for s, d in sites.items()}
        self.d = min(self.n.values())          # single-site feature count; fusion = palm block then nail block
        self.k = max_features

    def map_to(self, feats: tuple[int, ...], src: str, dst: str, half: int = 0) -> tuple[int, ...]:
        base = {i % self.d for i in feats} if src == FUSION else set(feats)
        return tuple(sorted(i + half * self.d for i in base)) if dst == FUSION else tuple(sorted(base))

    def neighbours(self, state: State) -> list[State]:
        site, f = state
        fs, out = set(f), []
        if len(f) < self.k:
            out += [(site, tuple(sorted(fs | {j}))) for j in range(self.n[site]) if j not in fs]
        if len(f) > 1:
            out += [(site, tuple(sorted(fs - {i}))) for i in f]
        out += [(site, tuple(sorted(fs - {i} | {j}))) for i in f for j in range(self.n[site]) if j not in fs]
        for dst in self.sites:
            if dst != site:
                out += [(dst, self.map_to(f, site, dst, h)) for h in ((0, 1) if dst == FUSION else (0,))]
        return list(dict.fromkeys(s for s in out if s != state))

    def random_neighbour(self, state: State, rng) -> State:
        nb = self.neighbours(state)
        return nb[rng.integers(len(nb))]

    def random_state(self, rng) -> State:
        site = self.sites[rng.integers(len(self.sites))]
        k = int(rng.integers(1, self.k + 1))
        return site, tuple(sorted(rng.choice(self.n[site], k, replace=False).tolist()))

    def children(self, state: State) -> list[State]:
        """Canonical extensions (add a feature index above the current maximum): each subset generated once."""
        site, f = state
        if len(f) >= self.k:
            return []
        return [(site, f + (j,)) for j in range((f[-1] + 1) if f else 0, self.n[site])]

    def size(self) -> int:
        return sum(math.comb(n, r) for n in self.n.values() for r in range(1, self.k + 1))


# ---------- cached evaluator ----------
class Evaluator:
    def __init__(self, sites: dict[str, SiteData], metric: str = config.SEARCH_METRIC, n_jobs: int = -1,
                 parallel_min: int = 64):
        self.sites, self.metric, self.n_jobs, self.parallel_min = sites, metric, n_jobs, parallel_min
        self.cache: dict[State, tuple[float, float]] = {}
        self.evals: list[tuple] = []          # (state, metric, objective, best objective so far, seconds)
        self.steps: list[dict] = []
        self.requests = 0
        self.best: tuple[float, State] | None = None
        self.t0 = time.perf_counter()

    def many(self, states: list[State]) -> list[float]:
        self.requests += len(states)
        todo = list(dict.fromkeys(s for s in states if s not in self.cache))
        if todo:
            self._evaluate(todo)
        return [self.cache[s][1] for s in states]

    def objective(self, state: State) -> float:
        return self.many([state])[0]

    def metric_of(self, state: State) -> float:
        self.many([state])
        return self.cache[state][0]

    def _evaluate(self, todo: list[State]) -> None:
        by_site: dict[str, list[State]] = {}
        for s in todo:
            by_site.setdefault(s[0], []).append(s)
        jobs = []
        for site, sts in by_site.items():
            d = self.sites[site]
            n_chunks = max(1, min(len(sts) // 16, 64)) if len(todo) >= self.parallel_min and self.n_jobs != 1 else 1
            jobs += [(site, part) for part in np.array_split(np.arange(len(sts)), n_chunks)
                     if len(part)]
        if len(jobs) > 1:
            res = Parallel(n_jobs=self.n_jobs)(
                delayed(_score_chunk)(self.sites[s].X, self.sites[s].y, self.sites[s].folds, self.metric,
                                      [by_site[s][i][1] for i in part]) for s, part in jobs)
        else:
            res = [_score_chunk(self.sites[s].X, self.sites[s].y, self.sites[s].folds, self.metric,
                                [by_site[s][i][1] for i in part]) for s, part in jobs]
        for (site, part), metrics in zip(jobs, res):
            for i, m in zip(part, metrics):
                st = by_site[site][i]
                obj = m - penalty(site, len(st[1]))
                self.cache[st] = (m, obj)
                if self.best is None or obj > self.best[0]:
                    self.best = (obj, st)
                self.evals.append((st, m, obj, self.best[0], time.perf_counter() - self.t0))

    def step(self, **info) -> None:
        self.steps.append({"eval": len(self.evals), **info})

    def label(self, state: State) -> list[str]:
        return [self.sites[state[0]].names[i] for i in state[1]]

    def trace(self) -> dict:
        return {"feature_names": {s: d.names for s, d in self.sites.items()},
                "columns": ["eval", "site", "features", "metric", "objective", "best_objective", "seconds"],
                "evaluations": [[i, s[0], list(s[1]), round(m, 4), round(o, 4), round(b, 4), round(t, 2)]
                                for i, (s, m, o, b, t) in enumerate(self.evals)],
                "steps": [{k: (self._state_json(v) if k in ("state", "states") else v) for k, v in st.items()}
                          for st in self.steps]}

    def _state_json(self, v):
        if isinstance(v, list):
            return [self._state_json(s) for s in v]
        return {"site": v[0], "features": self.label(v)}


# ---------- algorithms (each maximises ev.objective over space) ----------
def bfs(space: Space, ev: Evaluator, rng=None) -> None:
    frontier = [(s, ()) for s in space.sites]
    for depth in range(1, space.k + 1):
        frontier = [c for st in frontier for c in space.children(st)]
        ev.many(frontier)
        ev.step(depth=depth, n_states=len(frontier), best=ev.best[0], state=ev.best[1])


def iddfs(space: Space, ev: Evaluator, rng=None) -> None:
    def dls(state: State, depth: int, limit: int) -> None:
        kids = space.children(state)
        ev.many(kids)
        if depth + 1 < limit:
            for c in kids:
                dls(c, depth + 1, limit)

    for limit in range(1, space.k + 1):
        for s in space.sites:
            dls((s, ()), 0, limit)
        ev.step(limit=limit, best=ev.best[0], state=ev.best[1])


def hill_climbing(space: Space, ev: Evaluator, rng, restarts: int = 10) -> None:
    for r in range(restarts):
        cur = space.random_state(rng)
        cur_s = ev.objective(cur)
        ev.step(restart=r, state=cur, score=cur_s)
        while True:
            nb = space.neighbours(cur)
            sc = ev.many(nb)
            i = int(np.argmax(sc))
            if sc[i] <= cur_s + 1e-12:
                break
            cur, cur_s = nb[i], sc[i]
            ev.step(restart=r, state=cur, score=cur_s)


def simulated_annealing(space: Space, ev: Evaluator, rng, n_steps: int = 3000, t0: float = 0.05,
                        t1: float = 5e-4) -> None:
    cur = space.random_state(rng)
    cur_s = ev.objective(cur)
    for k in range(n_steps):
        temp = t0 * (t1 / t0) ** (k / (n_steps - 1))
        nxt = space.random_neighbour(cur, rng)
        s = ev.objective(nxt)
        accept = s >= cur_s or rng.random() < math.exp((s - cur_s) / temp)
        if accept:
            cur, cur_s = nxt, s
        ev.step(k=k, temp=round(temp, 6), state=cur, score=cur_s, accepted=bool(accept))


def local_beam(space: Space, ev: Evaluator, rng, k: int = 8, max_iter: int = 50) -> None:
    beam = list(dict.fromkeys(space.random_state(rng) for _ in range(k)))
    sc = ev.many(beam)
    best = max(sc)
    ev.step(it=0, states=beam, scores=sc)
    for it in range(1, max_iter + 1):
        pool = list(dict.fromkeys(n for b in beam for n in space.neighbours(b)))
        ps = ev.many(pool)
        order = np.argsort(ps)[::-1][:k]
        beam, sc = [pool[i] for i in order], [ps[i] for i in order]
        ev.step(it=it, states=beam, scores=sc)
        if sc[0] <= best + 1e-12:
            break
        best = sc[0]


def genetic(space: Space, ev: Evaluator, rng, pop: int = 40, gens: int = 40, p_cx: float = 0.8,
            p_mut: float = 0.3, elite: int = 2, tour: int = 3) -> None:
    def crossover(a: State, b: State) -> State:
        site = (a, b)[rng.integers(2)][0]
        genes = set(space.map_to(a[1], a[0], site, int(rng.integers(2))))
        genes |= set(space.map_to(b[1], b[0], site, int(rng.integers(2))))
        k = int(rng.integers(1, min(space.k, len(genes)) + 1))
        return site, tuple(sorted(rng.choice(sorted(genes), k, replace=False).tolist()))

    P = [space.random_state(rng) for _ in range(pop)]
    for g in range(gens):
        sc = np.array(ev.many(P))
        order = np.argsort(sc)[::-1]
        ev.step(gen=g, state=P[order[0]], score=float(sc[order[0]]), mean=float(sc.mean()))
        nxt = [P[i] for i in order[:elite]]
        while len(nxt) < pop:
            a, b = (P[max(rng.choice(pop, tour, replace=False), key=lambda i: sc[i])] for _ in range(2))
            c = crossover(a, b) if rng.random() < p_cx else a
            nxt.append(space.random_neighbour(c, rng) if rng.random() < p_mut else c)
        P = nxt
    ev.many(P)


def astar(space: Space, ev: Evaluator, rng=None, heuristic: str = "perfect") -> None:
    """Minimise path cost = photo cost + feature cost (+ 1 - metric on the final 'stop' edge) = 1 - objective.
    h = cost still unavoidable (one feature if none chosen) + 1 - an optimistic metric bound for the site. Goal
    nodes are pushed lazily at the bound and only evaluated when popped, so a better protocol already found prunes
    every node whose optimistic f is worse. "perfect" (bound 1) is provably admissible; "resub" (all features,
    scored on the training rows) is tighter but NOT admissible for specificity at a sensitivity floor."""
    ub = {s: resub_upper(d, ev.metric) if heuristic == "resub" else 1.0 for s, d in ev.sites.items()}
    ev.step(upper_bounds=ub)
    heap, tick = [], 0

    def push(f: float, rank: int, state: State) -> None:
        nonlocal tick
        heapq.heappush(heap, (f, rank, tick, state))
        tick += 1

    for s in space.sites:
        push(penalty(s, 1) + 1 - ub[s], 2, (s, ()))
    while heap:
        f, rank, _, st = heapq.heappop(heap)
        if rank == 0:                                   # evaluated goal: optimal
            ev.step(goal=True, state=st, f=f)
            return
        if rank == 1:                                   # lazy goal: evaluate, re-push at its true cost
            push(1 - ev.objective(st), 0, st)
            ev.step(state=st, f_bound=round(f, 5), f_true=round(1 - ev.cache[st][1], 5))
            continue
        if st[1]:
            push(penalty(st[0], len(st[1])) + 1 - ub[st[0]], 1, st)
        for c in space.children(st):
            push(penalty(c[0], len(c[1])) + 1 - ub[c[0]], 2, c)


def astar_resub(space: Space, ev: Evaluator, rng=None) -> None:
    astar(space, ev, rng, heuristic="resub")


ALGORITHMS = {"bfs": bfs, "iddfs": iddfs, "hill_climbing": hill_climbing,
              "simulated_annealing": simulated_annealing, "local_beam": local_beam, "genetic": genetic,
              "astar": astar, "astar_resub": astar_resub}
STOCHASTIC = ("hill_climbing", "simulated_annealing", "local_beam", "genetic")


def run_search(algo: str, sites: dict[str, SiteData], metric: str = config.SEARCH_METRIC,
               seed: int = config.SEED, n_jobs: int = -1, **params) -> tuple[dict, Evaluator]:
    space = Space(sites)
    ev = Evaluator(sites, metric, n_jobs)
    t0 = time.perf_counter()
    ALGORITHMS[algo](space, ev, np.random.default_rng(seed), **params)
    obj, st = ev.best
    return {"algo": algo, "best_objective": obj, "best_metric": ev.cache[st][0], "best_site": st[0],
            "best_features": ev.label(st), "best_state": [st[0], list(st[1])], "evaluations": len(ev.evals),
            "requests": ev.requests, "runtime_s": time.perf_counter() - t0}, ev


# ---------- honest re-evaluation: the search inside each outer training fold ----------
def nested_search(algo: str, sites: dict[str, SiteData], outer: dict[str, np.ndarray],
                  metric: str = config.SEARCH_METRIC, **params) -> list[dict]:
    """outer[site] = outer fold index per row. Rows sharing a patient (and, for palm/nail/fusion, a linked
    palm-nail pair) must share a fold. The search, the inner threshold and the final fit only see training rows."""
    out = []
    for k in range(int(max(v.max() for v in outer.values())) + 1):
        train = {s: d.subset(np.flatnonzero(outer[s] != k)) for s, d in sites.items()}
        res, _ = run_search(algo, train, metric, **params)
        site, feats = res["best_state"][0], res["best_state"][1]
        tr, te = train[site], sites[site].subset(np.flatnonzero(outer[site] == k))
        thr = sens_floor_threshold(tr.y, oof_proba(tr.X[:, feats], tr.y, tr.folds))
        p = _fit(tr.X[:, feats], tr.y)(te.X[:, feats])
        pred = p >= thr
        m_out = score(te.y, p, metric)
        out.append({"fold": k, "site": site, "features": res["best_features"], "n_test": int(len(te.y)),
                    "inner_metric": res["best_metric"], "inner_objective": res["best_objective"],
                    "outer_metric": m_out, "outer_objective": m_out - penalty(site, len(feats)),
                    "outer_roc_auc": float(roc_auc_score(te.y, p)),
                    "outer_sensitivity": float(pred[te.y == 1].mean()),
                    "outer_specificity": float((~pred[te.y == 0]).mean()),
                    "evaluations": res["evaluations"], "runtime_s": res["runtime_s"]})
    return out
