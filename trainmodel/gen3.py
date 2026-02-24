import os
import matplotlib

import random
from dataclasses import dataclass
from typing import List, Tuple, Dict

import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
from PIL import Image


# -----------------------------
# Config
# -----------------------------
CLASSES = [
    "ac_src",
    "battery",
    "cap",
    "curr_src",
    "diode",
    "inductor",
    "resistor",
    "swi_ideal",
    "swi_real",
    "volt_src",
    "xformer",
]
CLASS2ID = {c: i for i, c in enumerate(CLASSES)}

# Canvas in "drawing units" (schemdraw uses abstract units; export to px via figsize/dpi)
CANVAS_W = 32.0
CANVAS_H = 12.0

# Output image size control
FIGSIZE_INCH = (16, 6)  # affects resolution with DPI
DPI = 200

# Each class bounding box sizes (in drawing units). You can tune these.
# Keep them a bit larger than the symbol itself to be safe.
BOX_SIZES = {
    "ac_src": (2.4, 2.4),
    "battery": (2.0, 3.0),
    "cap": (2.0, 2.0),
    "curr_src": (2.4, 2.4),
    "diode": (2.2, 1.6),
    "inductor": (3.0, 1.6),
    "resistor": (3.0, 1.6),
    "swi_ideal": (2.2, 1.8),
    "swi_real": (2.6, 2.2),
    "volt_src": (2.4, 2.4),
    "xformer": (3.4, 2.4),
}

# How many extra random components beyond "one per class"
EXTRA_COMPONENTS_RANGE = (0, 8)

# Number of wires to draw
WIRES_RANGE = (5, 10)

# Placement margin inside canvas
MARGIN = 0.4

# Random orientations
ORIENTS = [0, 90, 180, 270]  # degrees


# -----------------------------
# Geometry helpers
# -----------------------------
@dataclass
class Rect:
    x: float  # left
    y: float  # bottom
    w: float
    h: float

    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y + self.h


@dataclass
class Placed:
    cls: str
    rect: Rect  # bbox in drawing units (axis-aligned)
    angle: int  # 0/90/180/270


def rect_intersect(a: Rect, b: Rect) -> bool:
    return not (a.right <= b.x or b.right <= a.x or a.top <= b.y or b.top <= a.y)


def split_free_rect(free: Rect, used: Rect) -> List[Rect]:
    """
    Guillotine-like split: return up to 4 rectangles around 'used' inside 'free'.
    """
    out = []
    # left
    if used.x > free.x:
        out.append(Rect(free.x, free.y, used.x - free.x, free.h))
    # right
    if used.right < free.right:
        out.append(Rect(used.right, free.y, free.right - used.right, free.h))
    # bottom
    if used.y > free.y:
        out.append(Rect(free.x, free.y, free.w, used.y - free.y))
    # top
    if used.top < free.top:
        out.append(Rect(free.x, used.top, free.w, free.top - used.top))

    # Remove any degenerate rectangles
    out = [r for r in out if r.w > 0.2 and r.h > 0.2]
    return out


def prune_free_rects(free_rects: List[Rect]) -> List[Rect]:
    """
    Remove rectangles fully contained in another rectangle.
    """
    pruned = []
    for i, r in enumerate(free_rects):
        contained = False
        for j, s in enumerate(free_rects):
            if i == j:
                continue
            if r.x >= s.x and r.y >= s.y and r.right <= s.right and r.top <= s.top:
                contained = True
                break
        if not contained:
            pruned.append(r)
    return pruned


def choose_position_in_free(free: Rect, w: float, h: float) -> Tuple[float, float]:
    """
    Randomly choose bottom-left (x,y) inside free rect for a w*h rect.
    """
    x = random.uniform(free.x, free.right - w)
    y = random.uniform(free.y, free.top - h)
    return x, y


def rotated_box_size(base_w: float, base_h: float, angle: int) -> Tuple[float, float]:
    if angle in (0, 180):
        return base_w, base_h
    return base_h, base_w


# -----------------------------
# schemdraw element factory
# -----------------------------
def make_element(cls: str, angle: int):
    """
    Return a schemdraw element instance. We'll place it with .at((x,y)) and .theta(angle).
    """
    if cls == "ac_src":
        # AC source symbol
        return elm.SourceSin()
    if cls == "volt_src":
        return elm.SourceV()
    if cls == "curr_src":
        return elm.SourceI()
    if cls == "battery":
        return elm.Battery()
    if cls == "cap":
        return elm.Capacitor()
    if cls == "diode":
        return elm.Diode()
    if cls == "inductor":
        return elm.Inductor()
    if cls == "resistor":
        return elm.Resistor()
    if cls == "swi_ideal":
        return elm.Switch()
    if cls == "swi_real":
        # "real" switch: use MOSFET symbol as a proxy (common in power electronics)
        return elm.NMos()
    if cls == "xformer":
        return elm.Transformer()
    raise ValueError(f"Unknown class: {cls}")


# -----------------------------
# Wire helpers
# -----------------------------
def random_point_on_rect_edge(r: Rect) -> Tuple[float, float]:
    """
    Pick a random point on the perimeter of a rectangle.
    """
    side = random.choice(["l", "r", "b", "t"])
    if side == "l":
        return (r.x, random.uniform(r.y, r.top))
    if side == "r":
        return (r.right, random.uniform(r.y, r.top))
    if side == "b":
        return (random.uniform(r.x, r.right), r.y)
    return (random.uniform(r.x, r.right), r.top)


def l_shaped_path(p1, p2) -> List[Tuple[float, float]]:
    """
    Create an L-shaped polyline path with one bend.
    Randomly choose bend orientation.
    """
    x1, y1 = p1
    x2, y2 = p2
    if random.random() < 0.5:
        return [(x1, y1), (x2, y1), (x2, y2)]
    else:
        return [(x1, y1), (x1, y2), (x2, y2)]


# -----------------------------
# Main generator per image
# -----------------------------
def generate_one(image_path: str, label_path: str, seed: int = None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # Start with one big free rect
    free_rects = [Rect(MARGIN, MARGIN, CANVAS_W - 2 * MARGIN, CANVAS_H - 2 * MARGIN)]
    placed: List[Placed] = []

    # Build component list: at least 1 per class, plus extras
    comps = CLASSES.copy()
    extra_n = random.randint(*EXTRA_COMPONENTS_RANGE)
    comps += random.choices(CLASSES, k=extra_n)
    random.shuffle(comps)

    # Place components (no overlap) by consuming free rectangles
    for cls in comps:
        base_w, base_h = BOX_SIZES[cls]
        success = False

        for _try in range(250):
            angle = random.choice(ORIENTS)
            w, h = rotated_box_size(base_w, base_h, angle)

            candidates = [fr for fr in free_rects if fr.w >= w and fr.h >= h]
            if not candidates:
                break
            fr = random.choice(candidates)

            x, y = choose_position_in_free(fr, w, h)
            new_rect = Rect(x, y, w, h)

            if any(rect_intersect(new_rect, p.rect) for p in placed):
                continue

            placed.append(Placed(cls=cls, rect=new_rect, angle=angle))

            free_rects.remove(fr)
            free_rects.extend(split_free_rect(fr, new_rect))
            free_rects = prune_free_rects(free_rects)

            success = True
            break

        if not success:
            # Must ensure each class exists at least once
            if cls in CLASSES and sum(1 for p in placed if p.cls == cls) == 0:
                raise RuntimeError(
                    f"Failed to place required class {cls}. Try bigger canvas or smaller boxes."
                )

    # Guarantee each class at least 1 (double-check)
    for cls in CLASSES:
        if not any(p.cls == cls for p in placed):
            raise RuntimeError(
                f"Missing required class {cls} after placement. Increase canvas or reduce BOX_SIZES."
            )

    # -----------------------------
    # Draw + auto-save using schemdraw official method
    # -----------------------------
    # IMPORTANT:
    # - image_path extension determines output type (.png/.jpg/.pdf/.svg...)
    # - canvas fixes coordinate system so our unit->pixel mapping is linear
    #
    # Some schemdraw versions accept "dpi=" in Drawing(); some don't.
    # So we avoid passing dpi here, and instead rely on default dpi.
    # If you want a specific dpi reliably across versions, we can post-process resize.

    d = schemdraw.Drawing(
        file=image_path,
        show=False,
        # canvas=[0, CANVAS_W, 0, CANVAS_H],
        canvas="matplotlib",
        transparent=False,
    )

    drawn_elements = []
    # Draw components at bbox centers
    for p in placed:
        r = p.rect
        cx = r.x + r.w / 2
        cy = r.y + r.h / 2

        elem = make_element(p.cls, p.angle).at((cx, cy)).theta(p.angle)
        d += elem
        drawn_elements.append((p.cls, elem))

    # Draw wires
    wires_n = random.randint(*WIRES_RANGE)
    for _ in range(wires_n):
        a, b = random.sample(placed, 2)
        p1 = random_point_on_rect_edge(a.rect)
        p2 = random_point_on_rect_edge(b.rect)
        path = l_shaped_path(p1, p2)

        for s in range(len(path) - 1):
            (x1, y1), (x2, y2) = path[s], path[s + 1]
            d += elm.Line().at((x1, y1)).to((x2, y2))

    # fig = d.draw(show=False)
    dxmin, dymin, dxmax, dymax = d.get_bbox()
    spanx = dxmax - dxmin
    spany = dymax - dymin
    d.save(image_path, transparent=False)  # , dpi=DPI, transparent=False)

    # -----------------------------
    # Read saved image size (pixels)
    # -----------------------------
    with Image.open(image_path) as im:
        W, H = im.size  # PIL uses (W,H)

    yolo_lines = []

    for cls, elem in drawn_elements:
        xmin, ymin, xmax, ymax = elem.get_bbox(transform=True)

        xc = ((xmin + xmax) / 2 - dxmin) / spanx
        yc = 1.0 - ((ymin + ymax) / 2 - dymin) / spany
        ww = (xmax - xmin) / spanx
        hh = (ymax - ymin) / spany

        # clamp
        xc = min(max(xc, 0.0), 1.0)
        yc = min(max(yc, 0.0), 1.0)
        ww = min(max(ww, 0.0), 1.0)
        hh = min(max(hh, 0.0), 1.0)

        cls_id = CLASS2ID[cls]
        yolo_lines.append(f"{cls_id} {xc:.6f} {yc:.6f} {ww:.6f} {hh:.6f}")

    os.makedirs(os.path.dirname(label_path), exist_ok=True)
    with open(label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_lines))


# -----------------------------
# Dataset loop + split
# -----------------------------
def generate_dataset(
    out_dir: str, n_images: int = 200, val_ratio: float = 0.2, seed: int = 0
):
    random.seed(seed)
    np.random.seed(seed)

    img_train = os.path.join(out_dir, "images", "train")
    img_val = os.path.join(out_dir, "images", "val")
    lab_train = os.path.join(out_dir, "labels", "train")
    lab_val = os.path.join(out_dir, "labels", "val")
    # os.makedirs(img_train, exist_ok=True)
    # os.makedirs(img_val, exist_ok=True)
    # os.makedirs(lab_train, exist_ok=True)
    # os.makedirs(lab_val, exist_ok=True)

    for p in [img_train, img_val, lab_train, lab_val]:
        os.makedirs(p, exist_ok=True)

    n_val = int(round(n_images * val_ratio))
    indices = list(range(n_images))
    random.shuffle(indices)
    val_set = set(indices[:n_val])

    for i in range(n_images):
        split = "val" if i in val_set else "train"
        img_path = os.path.join(out_dir, "images", split, f"{i:06d}.png")
        lab_path = os.path.join(out_dir, "labels", split, f"{i:06d}.txt")

        # Different seed per image for reproducibility
        generate_one(img_path, lab_path, seed=seed + i)

        if (i + 1) % 20 == 0:
            print(f"Generated {i+1}/{n_images}")

    # Write a sample data.yaml
    yaml_path = os.path.join(out_dir, "data.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(
            f"path: {os.path.abspath(out_dir)}\n"
            f"train: images/train\n"
            f"val: images/val\n"
            f"names:\n"
        )
        for i, c in enumerate(CLASSES):
            f.write(f"  {i}: {c}\n")

    print("Done.")
    print("data.yaml saved to:", yaml_path)


if __name__ == "__main__":
    # Example:
    # generate_dataset("synthetic_schemdraw_dataset", n_images=500, val_ratio=0.2, seed=42)
    generate_dataset(
        "synthetic_schemdraw_dataset",
        n_images=10,
        val_ratio=0.2,
        seed=42,
    )
