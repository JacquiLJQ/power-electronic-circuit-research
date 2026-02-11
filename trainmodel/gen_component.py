#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import random
from pathlib import Path
import numpy as np
import cv2


# ----------------------------
# Asset indexing
# ----------------------------
def list_assets(root: Path):
    """Scan root/class/*.png -> (class_names sorted, assets_by_class dict)."""
    class_dirs = [p for p in root.iterdir() if p.is_dir()]
    class_names = sorted([p.name for p in class_dirs])
    assets = {}
    for cls in class_names:
        files = list((root / cls).glob("*.png"))
        if files:
            assets[cls] = files
    class_names = [c for c in class_names if c in assets]
    return class_names, assets


# ----------------------------
# Image IO + preprocessing
# ----------------------------
def read_gray(path: Path) -> np.ndarray:
    im = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if im is None:
        raise RuntimeError(f"Failed to read: {path}")
    if im.ndim == 2:
        return im
    if im.shape[2] == 4:
        # drop alpha for now (we'll do robust crop on intensity)
        bgr = im[:, :, :3]
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)


def invert_component(gray: np.ndarray) -> np.ndarray:
    """Your requirement: invert after reading."""
    return 255 - gray


def crop_to_content(gray: np.ndarray):
    """
    Crop component to its 'content' region.
    Robust approach: infer background from border pixels, then keep pixels that differ.
    Works for various exported PNG backgrounds.
    """
    border = np.concatenate([gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]])
    bg = int(np.median(border))
    diff = np.abs(gray.astype(np.int16) - bg)

    # threshold for "content"
    mask = (diff > 12).astype(np.uint8)

    ys, xs = np.where(mask > 0)
    if len(xs) == 0 or len(ys) == 0:
        return None  # no content

    x1, x2 = int(xs.min()), int(xs.max())
    y1, y2 = int(ys.min()), int(ys.max())
    cropped = gray[y1 : y2 + 1, x1 : x2 + 1]
    return cropped


def paste_on_white_bg(bg: np.ndarray, comp: np.ndarray, x: int, y: int):
    """
    bg: white canvas (uint8)
    comp: component image (uint8) where strokes should be darker than background.
    Blend: darken (min) so comp background doesn't overwrite bg.
    """
    h, w = comp.shape[:2]
    roi = bg[y : y + h, x : x + w]
    bg[y : y + h, x : x + w] = np.minimum(roi, comp)


def resize_keep_aspect(img: np.ndarray, target_long_side: int, jitter: float = 0.0):
    """
    Resize img so that its longer side becomes target_long_side (with optional jitter),
    keeping aspect ratio.
    """
    h, w = img.shape[:2]
    if h <= 0 or w <= 0:
        return img

    # jitter: e.g. 0.25 -> scale in [0.75, 1.25]
    if jitter > 0:
        t = target_long_side * random.uniform(1.0 - jitter, 1.0 + jitter)
    else:
        t = float(target_long_side)

    long_side = max(h, w)
    if long_side == 0:
        return img

    scale = t / long_side
    new_w = max(6, int(round(w * scale)))
    new_h = max(6, int(round(h * scale)))

    # use INTER_AREA when downscale, INTER_LINEAR when upscale
    interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
    return cv2.resize(img, (new_w, new_h), interpolation=interp)


# ----------------------------
# Free-rectangle packing (no overlap by construction)
# Rect is (x1,y1,x2,y2) inclusive
# ----------------------------
def rect_w(r):
    return r[2] - r[0] + 1


def rect_h(r):
    return r[3] - r[1] + 1


def rect_contains(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return ax1 <= bx1 and ay1 <= by1 and ax2 >= bx2 and ay2 >= by2


def expand_box(box, pad, W, H):
    x1, y1, x2, y2 = box
    return (
        max(0, x1 - pad),
        max(0, y1 - pad),
        min(W - 1, x2 + pad),
        min(H - 1, y2 + pad),
    )


def split_free_rect(free_r, used_r):
    """
    Cut free_r by used_r (assumed to be inside free_r). Return remaining free rectangles.
    """
    fx1, fy1, fx2, fy2 = free_r
    ux1, uy1, ux2, uy2 = used_r
    out = []

    # top
    if uy1 > fy1:
        out.append((fx1, fy1, fx2, uy1 - 1))
    # bottom
    if uy2 < fy2:
        out.append((fx1, uy2 + 1, fx2, fy2))
    # left band
    if ux1 > fx1:
        out.append((fx1, max(fy1, uy1), ux1 - 1, min(fy2, uy2)))
    # right band
    if ux2 < fx2:
        out.append((ux2 + 1, max(fy1, uy1), fx2, min(fy2, uy2)))

    out = [r for r in out if rect_w(r) > 0 and rect_h(r) > 0]
    return out


def prune_free_rects(rects):
    """
    Remove rectangles fully contained in others (simple pruning to control growth).
    """
    rects = sorted(rects, key=lambda r: rect_w(r) * rect_h(r), reverse=True)
    kept = []
    for r in rects:
        if any(rect_contains(k, r) for k in kept):
            continue
        kept.append(r)
    return kept


# ----------------------------
# YOLO label line
# ----------------------------
def yolo_line(cls_id, box, W, H):
    x1, y1, x2, y2 = box
    cx = ((x1 + x2) / 2) / W
    cy = ((y1 + y2) / 2) / H
    bw = (x2 - x1 + 1) / W
    bh = (y2 - y1 + 1) / H
    return f"{cls_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}"


# ----------------------------
# Generate one image
# ----------------------------
def generate_one(
    W,
    H,
    k,
    pad,
    class_names,
    assets_by_class,
    target_long_side=90,
    size_jitter=0.25,
    choose_free="largest",
    max_free_rects=2000,
):

    canvas = np.full((H, W), 255, dtype=np.uint8)  # white bg
    labels = []
    comp_boxes = []

    free_rects = [(0, 0, W - 1, H - 1)]

    for _ in range(k):
        cls = random.choice(class_names)
        cls_id = class_names.index(cls)
        asset = random.choice(assets_by_class[cls])

        gray = read_gray(asset)
        inv = invert_component(gray)  # your requirement
        comp = crop_to_content(inv)  # must crop, otherwise huge box
        if comp is None:
            continue

        # >>> NEW: normalize size
        comp = resize_keep_aspect(
            comp, target_long_side=target_long_side, jitter=size_jitter
        )

        ch, cw = comp.shape[:2]
        if ch < 6 or cw < 6:
            continue

        need_w = cw + 2 * pad
        need_h = ch + 2 * pad

        candidates = [
            r for r in free_rects if rect_w(r) >= need_w and rect_h(r) >= need_h
        ]
        if not candidates:
            # no remaining space
            continue

        if choose_free == "largest":
            fr = max(candidates, key=lambda r: rect_w(r) * rect_h(r))
        else:
            fr = random.choice(candidates)

        fx1, fy1, fx2, fy2 = fr

        # sample a position inside free rect with padding
        x = random.randint(fx1 + pad, fx2 - pad - cw + 1)
        y = random.randint(fy1 + pad, fy2 - pad - ch + 1)

        box = (x, y, x + cw - 1, y + ch - 1)
        used = expand_box(box, pad, W, H)

        # paste
        paste_on_white_bg(canvas, comp, x, y)
        labels.append((cls_id, box))
        comp_boxes.append(box)

        # update free space
        free_rects.remove(fr)
        free_rects.extend(split_free_rect(fr, used))
        if len(free_rects) > max_free_rects:
            free_rects = prune_free_rects(free_rects)

        # === draw simple wires (visual only) ===
    if len(comp_boxes) >= 2:
        draw_simple_wires(
            canvas,
            comp_boxes,
            n_wires=random.randint(4, 8),
            thickness=random.choice([1, 2]),
        )

    return canvas, labels


# ----------------------------
# Write dataset structure
# ----------------------------
def write_data_yaml(out_root: Path, class_names):
    yaml = f"""path: "{out_root.as_posix()}"
train: images/train
val: images/val
test: images/test
nc: {len(class_names)}
names:
"""
    for i, n in enumerate(class_names):
        yaml += f"  {i}: {n}\n"
    (out_root / "data.yaml").write_text(yaml, encoding="utf-8")


def draw_simple_wires(canvas, boxes, n_wires=6, thickness=2):
    """
    canvas: HxW uint8 (white bg)
    boxes: list of component bboxes [(x1,y1,x2,y2), ...]
    n_wires: number of random wires
    """

    H, W = canvas.shape[:2]

    # 收集已有线段，用于判断交叉
    segments = []  # each: ((x1,y1),(x2,y2))
    junctions = []  # list of (x,y)
    jumps = []  # list of (x,y)

    def rand_point_near_box(b):
        x1, y1, x2, y2 = b
        side = random.choice(["L", "R", "T", "B"])
        if side == "L":
            return (x1, random.randint(y1, y2))
        if side == "R":
            return (x2, random.randint(y1, y2))
        if side == "T":
            return (random.randint(x1, x2), y1)
        return (random.randint(x1, x2), y2)

    def intersect(a1, a2, b1, b2):
        # only axis-aligned
        if a1[0] == a2[0] and b1[1] == b2[1]:  # a vertical, b horizontal
            x = a1[0]
            y = b1[1]
            if min(a1[1], a2[1]) <= y <= max(a1[1], a2[1]) and min(
                b1[0], b2[0]
            ) <= x <= max(b1[0], b2[0]):
                return (x, y)
        if a1[1] == a2[1] and b1[0] == b2[0]:  # a horizontal, b vertical
            x = b1[0]
            y = a1[1]
            if min(a1[0], a2[0]) <= x <= max(a1[0], a2[0]) and min(
                b1[1], b2[1]
            ) <= y <= max(b1[1], b2[1]):
                return (x, y)
        return None

    for _ in range(n_wires):
        if len(boxes) < 2:
            break

        b1, b2 = random.sample(boxes, 2)
        p1 = rand_point_near_box(b1)
        p2 = rand_point_near_box(b2)

        # Manhattan L-shape
        if random.random() < 0.5:
            mid = (p2[0], p1[1])
        else:
            mid = (p1[0], p2[1])

        path = [p1, mid, p2]

        # collect segments
        new_segs = [(path[0], path[1]), (path[1], path[2])]

        # check intersections
        for s1, s2 in new_segs:
            for e1, e2 in segments:
                ip = intersect(s1, s2, e1, e2)
                if ip:
                    if random.random() < 0.7:
                        junctions.append(ip)
                    else:
                        jumps.append(ip)

        # draw wire
        for a, b in new_segs:
            cv2.line(canvas, a, b, 0, thickness, cv2.LINE_AA)

        segments.extend(new_segs)
        junctions.append(p1)
        junctions.append(p2)

    # draw junctions
    for x, y in junctions:
        cv2.circle(canvas, (int(x), int(y)), 3, 0, -1)

    # draw jumps
    for x, y in jumps:
        cv2.ellipse(canvas, (int(x), int(y)), (8, 8), 0, 0, 180, 0, thickness)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--component_root",
        type=str,
        required=True,
        help="Root dir containing class subfolders of PNGs",
    )
    ap.add_argument(
        "--out", type=str, default="component_dataset", help="Output dataset root"
    )
    ap.add_argument("--n", type=int, default=1, help="Number of images to generate")
    ap.add_argument("--W", type=int, default=1024)
    ap.add_argument("--H", type=int, default=1024)
    ap.add_argument("--k", type=int, default=10, help="Components per image")
    ap.add_argument(
        "--pad", type=int, default=4, help="Padding around bbox to keep spacing"
    )
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument(
        "--split",
        type=float,
        nargs=3,
        default=(0.8, 0.1, 0.1),
        help="train/val/test ratios",
    )
    ap.add_argument(
        "--choose_free", type=str, default="largest", choices=["largest", "random"]
    )
    ap.add_argument(
        "--target",
        type=int,
        default=90,
        help="Target long-side size (pixels) for each component after crop",
    )
    ap.add_argument(
        "--jitter",
        type=float,
        default=0.25,
        help="Size jitter ratio around target (0.25 -> 75%~125%)",
    )

    args = ap.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    component_root = Path(args.component_root)
    out_root = Path(args.out)

    class_names, assets_by_class = list_assets(component_root)
    if not class_names:
        raise RuntimeError(f"No assets found under {component_root}")

    # prepare dirs
    for sp in ["train", "val", "test"]:
        (out_root / "images" / sp).mkdir(parents=True, exist_ok=True)
        (out_root / "labels" / sp).mkdir(parents=True, exist_ok=True)

    write_data_yaml(out_root, class_names)

    n = args.n
    n_train = int(n * args.split[0])
    n_val = int(n * args.split[1])
    n_test = n - n_train - n_val
    split_plan = (["train"] * n_train) + (["val"] * n_val) + (["test"] * n_test)
    if not split_plan:  # if n=1 and split rounds to 0
        split_plan = ["train"]
    random.shuffle(split_plan)

    for i, sp in enumerate(split_plan):
        img, labels = generate_one(
            W=args.W,
            H=args.H,
            k=args.k,
            pad=args.pad,
            class_names=class_names,
            assets_by_class=assets_by_class,
            target_long_side=args.target,
            size_jitter=args.jitter,
            choose_free=args.choose_free,
        )

        stem = f"{i:06d}"
        img_path = out_root / "images" / sp / f"{stem}.png"
        lbl_path = out_root / "labels" / sp / f"{stem}.txt"

        cv2.imwrite(str(img_path), img)

        lines = [yolo_line(cls_id, box, args.W, args.H) for cls_id, box in labels]
        lbl_path.write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )

        if (i + 1) % 50 == 0 or i == 0:
            print(f"[{i+1}/{len(split_plan)}] {sp}/{stem}.png objs={len(labels)}")

    print("[DONE] out:", out_root.resolve())
    print("[DONE] classes:", class_names)
    print("[DONE] data.yaml:", (out_root / "data.yaml").resolve())


if __name__ == "__main__":
    main()
