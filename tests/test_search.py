import numpy as np
import pytest

from netra.search import (ALGORITHMS, FUSION, Evaluator, SiteData, Space, load_trace, nested_search, run_search,
                          save_trace, spec_at_sens)


def _sites(n: int = 90, d: int = 5) -> dict[str, SiteData]:
    rng = np.random.default_rng(0)
    out = {}
    for k, s in enumerate(("eye", "palm", "nail")):
        X = rng.normal(size=(n, d))
        y = (X[:, k] + rng.normal(0, 1.0, n) > 0).astype(int)
        out[s] = SiteData(X, y, np.repeat(np.arange(n // 2), 2).astype(str), [f"f{i}" for i in range(d)])
    p, nl = out["palm"], out["nail"]
    out[FUSION] = SiteData(np.hstack([p.X, nl.X]), p.y, p.groups, [f"palm:{c}" for c in p.names] +
                           [f"nail:{c}" for c in nl.names])
    return out


def test_spec_at_sens():
    y = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0])
    p = np.array([0.9, 0.8, 0.7, 0.6, 0.1, 0.65, 0.5, 0.3, 0.2])
    assert spec_at_sens(y, p, 0.8) == 0.75


def test_neighbours_stay_in_space():
    sp = Space(_sites())
    for st in [("eye", (0,)), ("palm", (1, 2, 3)), (FUSION, (0, 7)), (FUSION, (1, 6, 9))]:
        for s, f in sp.neighbours(st):
            assert 1 <= len(f) <= sp.k and len(set(f)) == len(f) and max(f) < sp.n[s] and (s, f) != st
    assert (FUSION, (5, 6)) in sp.neighbours(("eye", (0, 1)))
    assert ("nail", (1, 2)) in sp.neighbours((FUSION, (1, 7)))


def test_cache_counts_distinct_states():
    ev = Evaluator(_sites(), n_jobs=1)
    ev.many([("eye", (0,)), ("eye", (0,)), ("palm", (1, 2))])
    ev.objective(("eye", (0,)))
    assert len(ev.evals) == 2 and ev.requests == 4


@pytest.fixture(scope="module")
def results():
    sites = _sites()
    return {a: run_search(a, sites, n_jobs=1)[0] for a in ALGORITHMS}, sites


def test_exhaustive_and_astar_agree(results):
    res, sites = results
    opt = res["bfs"]["best_objective"]
    assert res["bfs"]["evaluations"] == Space(sites).size()
    assert res["iddfs"]["best_objective"] == pytest.approx(opt)
    assert res["iddfs"]["requests"] > res["iddfs"]["evaluations"]
    assert res["astar"]["best_objective"] == pytest.approx(opt)
    assert res["astar_resub"]["best_objective"] <= opt + 1e-12


def test_local_searches_never_beat_exhaustive(results):
    res, _ = results
    for a in ("hill_climbing", "simulated_annealing", "local_beam", "genetic"):
        assert res[a]["best_objective"] <= res["bfs"]["best_objective"] + 1e-12


def test_nested_search_keeps_test_rows_out():
    sites = _sites()
    outer = {s: np.array([int(g) % 3 for g in d.groups]) for s, d in sites.items()}
    folds = nested_search("hill_climbing", sites, outer, n_jobs=1, restarts=2)
    assert len(folds) == 3
    for f in folds:
        assert f["n_test"] == 30 and 0 <= f["outer_metric"] <= 1


def test_trace_thinning_round_trip(tmp_path):
    res, ev = run_search("simulated_annealing", _sites(), n_jobs=1, n_steps=300)
    full = [b for *_, b, _ in ev.evals]
    n_improve = sum(i == 0 or full[i] > full[i - 1] for i in range(len(full)))
    only = ev.trace(None)
    assert len(only["evaluations"]) <= n_improve + 1
    assert only["evaluations"][-1][5] == round(res["best_objective"], 4)
    save_trace(tmp_path / "search_trace_sa.json.gz", res, ev.trace(20))
    tr = load_trace("sa", tmp_path)
    assert n_improve <= len(tr["evaluations"]) < len(ev.evals)
    assert tr["summary"]["n_evaluations"] == len(ev.evals) and tr["meta"]["algo"] == "simulated_annealing"
    assert len(tr["steps"]) < 300 / 20 + n_improve + 3
