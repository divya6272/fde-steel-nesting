"""Tiny 2D rectangle packer (shelf first-fit) used by the prototype.
Deliberately simple: the point of the prototype is the REUSE LOGIC and the
MEASUREMENT HARNESS, not state-of-the-art nesting. Real nesting would use the
client's Strumis auto-nest and/or a proper irregular-shape nester."""

STEEL_T_PER_MM3 = 7.85e-9  # 7850 kg/m3 -> tonnes per mm^3


def shelf_pack(parts, W, H, allow_rotate=True, sort_key="height"):
    """parts: list of (pid, w, h). Returns (placed_ids, placed_area)."""
    def key(p):
        return -max(p[1], p[2]) if sort_key == "height" else -(p[1] * p[2])
    order = sorted(parts, key=key)
    shelves = []  # [y, shelf_h, x_used]
    placed, area = [], 0
    for pid, w, h in order:
        options = [(w, h)] + ([(h, w)] if allow_rotate and w != h else [])
        # prefer the orientation that keeps shelves short
        options.sort(key=lambda o: o[1])
        done = False
        for ow, oh in options:
            if ow > W:
                continue
            for s in shelves:
                if oh <= s[1] and s[2] + ow <= W:
                    s[2] += ow
                    done = True
                    break
            if done:
                break
            y = sum(s[1] for s in shelves)
            if y + oh <= H:
                shelves.append([y, oh, ow])
                done = True
                break
        if done:
            placed.append(pid)
            area += w * h
    return placed, area
