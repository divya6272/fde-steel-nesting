"""Prototype 3 - profiles (beams/columns) are a 1D cutting-stock problem.
Do cut-length offcuts get reused if we check stock before buying a 12 m bar?
SYNTHETIC DATA. Mechanism only."""
import random, statistics

BAR = 12000          # mm stock length
KG_PER_M = 50.0      # normalisation only
MIN_OFFCUT = 1500    # mm - shorter leftovers are scrap


def run(parts, offcuts, reuse, accuracy, rng):
    stock = sorted([o for o in offcuts if rng.random() < accuracy], reverse=True) if reuse else []
    bars, used_off = 0, 0
    for p in sorted(parts, reverse=True):
        # best fit among offcuts, else open/continue a fresh bar
        fit = [i for i, o in enumerate(stock) if o >= p]
        if fit:
            i = min(fit, key=lambda i: stock[i])
            stock[i] -= p
            used_off += 1
            continue
        bars += 1
        stock.append(BAR - p)  # remainder of a fresh bar becomes usable stock (same project)
    return bars * BAR / 1000 * KG_PER_M / 1000  # tonnes of fresh bars bought


def experiment(n_seeds=30, accuracy=0.7):
    red = []
    for s in range(n_seeds):
        rng = random.Random(500 + s)
        parts = [rng.randint(900, 7500) for _ in range(300)]
        offcuts = [rng.randint(MIN_OFFCUT, 6000) for _ in range(40)]
        a = run(parts, offcuts, False, 1.0, random.Random(s))
        b = run(parts, offcuts, True, accuracy, random.Random(s))
        red.append(100 * (a - b) / a)
    return {"stock_accuracy": accuracy, "mean_purchase_reduction_pct": round(statistics.mean(red), 1),
            "min": round(min(red), 1), "max": round(max(red), 1)}


if __name__ == "__main__":
    print("Synthetic: 300 cut lengths, 40 stock offcuts (1.5-6 m), 30 runs")
    for acc in (1.0, 0.7, 0.4):
        print(experiment(accuracy=acc))
