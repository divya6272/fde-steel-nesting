"""Prototype 2 - the evaluation harness we would run on the client's REAL data:
paired comparison of plate yield, manual nest vs auto/optimiser nest, with a
pre-registered decision rule. Demo below uses two toy packers on synthetic jobs
purely to show the harness works; it says nothing about the client's nesters."""
import random, statistics
from packer import shelf_pack

W, H = 6000, 2000


def decision(diffs_pts, n_boot=5000, seed=7):
    """diffs_pts: per-job (auto yield - manual yield) in percentage points."""
    rng = random.Random(seed)
    n = len(diffs_pts)
    boots = sorted(statistics.mean(rng.choices(diffs_pts, k=n)) for _ in range(n_boot))
    lo, hi = boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot)]
    mean = statistics.mean(diffs_pts)
    if mean >= 2.0 and lo > 0:
        verdict = "GO: build the optimiser (gain >= 2 pts, CI above 0)"
    elif mean < 1.0:
        verdict = "STOP optimiser: manual nesting is as good (gain < 1 pt). Keep remnant matching."
    else:
        verdict = "EXTEND: inconclusive - add more plates before deciding"
    return {"n": n, "mean_gain_pts": round(mean, 2), "ci95": (round(lo, 2), round(hi, 2)), "verdict": verdict}


def job_yield(parts, allow_rotate, sort_key):
    todo, plates, area = list(parts), 0, sum(w * h for _, w, h in parts)
    while todo:
        placed, _ = shelf_pack(todo, W, H, allow_rotate, sort_key)
        if not placed:
            break
        plates += 1
        todo = [p for p in todo if p[0] not in set(placed)]
    return 100 * area / (plates * W * H)


if __name__ == "__main__":
    rng = random.Random(3)
    diffs = []
    for j in range(30):  # 30 historical "jobs" (client rule: stratified by thickness)
        parts = [(i, int(min(2400, max(150, rng.lognormvariate(6.2, .55)))),
                     int(min(1200, max(100, rng.lognormvariate(5.7, .5))))) for i in range(40)]
        manual_proxy = job_yield(parts, False, "area")
        auto_proxy = job_yield(parts, True, "height")
        diffs.append(auto_proxy - manual_proxy)
    print(decision(diffs))
