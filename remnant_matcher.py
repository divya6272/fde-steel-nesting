"""Prototype 1 - does an offcut/remnant check at drawing release reduce fresh
plate purchases?  SYNTHETIC DATA. Proves the mechanism and shows sensitivity to
stock-record accuracy. It does NOT estimate the client's real saving."""
import random, statistics, json, sys
from packer import shelf_pack, STEEL_T_PER_MM3

PLATE_W, PLATE_H = 6000, 2000
THICKNESSES = [10, 12, 16, 20, 25]
MIN_FILL = 0.40  # do not burn a usable offcut on a couple of tiny parts


def make_parts(rng, n):
    parts = []
    for i in range(n):
        t = rng.choices(THICKNESSES, weights=[3, 3, 2, 2, 1])[0]
        w = int(min(2400, max(150, rng.lognormvariate(6.2, 0.55))))
        h = int(min(1200, max(100, rng.lognormvariate(5.7, 0.50))))
        parts.append((i, t, w, h))
    return parts


def make_offcuts(rng, per_thickness):
    out = []
    for t in THICKNESSES:
        for _ in range(per_thickness):
            out.append({"t": t, "w": rng.randint(500, 2800), "h": rng.randint(300, 1300)})
    return out


def run(parts, offcuts, use_remnants, stock_accuracy, rng):
    """Returns (fresh_plate_tonnes, offcut_tonnes_used, part_tonnes)."""
    fresh_area_t = 0.0   # sum(area*thickness) of fresh plates, mm^3
    off_used_t = 0.0
    part_t = sum(w * h * t for _, t, w, h in parts)
    for t in THICKNESSES:
        todo = [(pid, w, h) for pid, tt, w, h in parts if tt == t]
        if use_remnants:
            # only stock that physically exists / can be found is usable
            stock = [o for o in offcuts if o["t"] == t and rng.random() < stock_accuracy]
            stock.sort(key=lambda o: -(o["w"] * o["h"]))
            for o in stock:
                if not todo:
                    break
                placed, area = shelf_pack(todo, o["w"], o["h"])
                if placed and area / (o["w"] * o["h"]) >= MIN_FILL:
                    off_used_t += o["w"] * o["h"] * t
                    todo = [p for p in todo if p[0] not in set(placed)]
        while todo:
            placed, _ = shelf_pack(todo, PLATE_W, PLATE_H)
            if not placed:  # part larger than plate - skip (synthetic guard)
                break
            fresh_area_t += PLATE_W * PLATE_H * t
            todo = [p for p in todo if p[0] not in set(placed)]
    f = STEEL_T_PER_MM3
    return fresh_area_t * f, off_used_t * f, part_t * f


def experiment(n_seeds=30, n_parts=600, per_thickness=3, accuracy=0.7):
    reductions, base_t, new_t = [], [], []
    for s in range(n_seeds):
        rng = random.Random(1000 + s)
        parts, offcuts = make_parts(rng, n_parts), make_offcuts(rng, per_thickness)
        a, _, _ = run(parts, offcuts, False, 1.0, random.Random(s))
        b, used, _ = run(parts, offcuts, True, accuracy, random.Random(s))
        reductions.append(100 * (a - b) / a)
        base_t.append(a); new_t.append(b)
    return {
        "stock_accuracy": accuracy,
        "mean_fresh_t_no_reuse": round(statistics.mean(base_t), 1),
        "mean_fresh_t_with_reuse": round(statistics.mean(new_t), 1),
        "mean_purchase_reduction_pct": round(statistics.mean(reductions), 1),
        "min_pct": round(min(reductions), 1), "max_pct": round(max(reductions), 1),
    }


if __name__ == "__main__":
    print("Synthetic: 600 parts across 5 thicknesses, 3 offcuts per thickness, 30 runs")
    for acc in (1.0, 0.7, 0.4):
        print(json.dumps(experiment(accuracy=acc)))
