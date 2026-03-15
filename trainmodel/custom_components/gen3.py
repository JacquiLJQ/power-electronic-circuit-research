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
from factory import make_component


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
CLASSES2 = [  # no swi_real
    "ac_src",
    "battery",
    "cap",
    "curr_src",
    "diode",
    "inductor",
    "resistor",
    "swi_ideal",
    "volt_src",
    "xformer",
]
CLASS2ID = {c: i for i, c in enumerate(CLASSES)}

# Canvas in "drawing units" (schemdraw uses abstract units; export to px via figsize/dpi)
CANVAS_W = 32.0
CANVAS_H = 12.0

# Output image size control
FIGSIZE_INCH = (16, 6)  # affects resolution with DPI
DPI = 16

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
ORIENTS = [0, 45, 90, 135, 180, 225, 270]  # degrees


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


def bbox_to_rect(bbox):
    xmin, ymin, xmax, ymax = bbox
    return Rect(x=xmin, y=ymin, w=xmax - xmin, h=ymax - ymin)


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
    x = random.uniform(0, 200)  # random.uniform(free.x, free.right - w)
    y = random.uniform(0, 200)  # random.uniform(free.y, free.top - h)
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

    for _ in range(10):
        try:
            elem = make_component(cls)
            return elem
        except Exception as e:
            last_err = e
            # 可以在这里打印调试信息（可选）
            print(f"[WARN] retry make_component({cls}) due to: {e}")
            continue

    # 如果多次失败，才真正抛出错误
    raise RuntimeError(f"Failed to create element {cls} after 10 retries") from last_err


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


def get_world_anchor(elem, name: str):
    # # 有些版本叫 absanchors
    if hasattr(elem, "absanchors") and name in elem.absanchors:
        return elem.absanchors[name]
    # 有些版本可能有 _absanchors 或 anchors 已经是 world（不常见）
    if hasattr(elem, "_absanchors") and name in elem._absanchors:
        return elem._absanchors[name]
    if hasattr(elem, "anchors") and name in elem.anchors:
        return elem.anchors[name]
    return None


def rect_center_r(r):
    return (r.x + r.w / 2, r.y + r.h / 2)


def pick_port_on_r_towards(r, target_xy, rng, jitter=0.08):
    xmin, ymin = r.x, r.y
    xmax, ymax = r.x + r.w, r.y + r.h
    tx, ty = target_xy
    cx, cy = rect_center_r(r)

    dx, dy = tx - cx, ty - cy
    if abs(dx) >= abs(dy):
        x = xmax if dx >= 0 else xmin
        y = rng.uniform(ymin, ymax)
        y += rng.uniform(-jitter, jitter) * (ymax - ymin)
        y = max(ymin, min(y, ymax))
        return (x, y)
    else:
        y = ymax if dy >= 0 else ymin
        x = rng.uniform(xmin, xmax)
        x += rng.uniform(-jitter, jitter) * (xmax - xmin)
        x = max(xmin, min(x, xmax))
        return (x, y)


def draw_wire(d, path, lw):
    for i in range(len(path) - 1):
        d += elm.Line(lw=lw).at(path[i]).to(path[i + 1])


def simple_l_path(p1, p2, rng):
    x1, y1 = p1
    x2, y2 = p2
    if rng.random() < 0.5:
        return [p1, (x2, y1), p2]
    else:
        return [p1, (x1, y2), p2]


def yolo_no_overlap(yolo_lines):
    boxes = []

    # 先把 YOLO bbox 转成 xmin,ymin,xmax,ymax
    for line in yolo_lines:
        cls_id, xc, yc, w, h = map(float, line.split())

        xmin = xc - w / 2
        xmax = xc + w / 2
        ymin = yc - h / 2
        ymax = yc + h / 2

        boxes.append((xmin, ymin, xmax, ymax))

    # 两两检测
    n = len(boxes)
    for i in range(n):
        xmin1, ymin1, xmax1, ymax1 = boxes[i]

        for j in range(i + 1, n):
            xmin2, ymin2, xmax2, ymax2 = boxes[j]

            overlap = not (
                xmax1 < xmin2 or xmax2 < xmin1 or ymax1 < ymin2 or ymax2 < ymin1
            )

            if overlap:
                return False

    return True


def choose_position(placed_elms: List[elm.Element]):
    if len(placed_elms) < 1:
        x = random.uniform(0, 25)
        y = random.uniform(0, 25)
        return x, y
    else:

        candidates = [(x, y) for x in range(26) for y in range(26)]
        bboxes = []
        margin = 0
        for elem in placed_elms:
            xmin, ymin, xmax, ymax = elem.get_bbox(transform=True)
            bboxes.append((xmin, ymin, xmax, ymax))

        remaining = []
        for x, y in candidates:
            blocked = False
            for xmin, ymin, xmax, ymax in bboxes:
                if (xmin - margin) <= x <= (xmax + margin) and (ymin - margin) <= y <= (
                    ymax + margin
                ):
                    blocked = True
                    break
            if not blocked:
                remaining.append((x, y))

        # 5. 从剩余点中随机选一个
        if remaining:
            return random.choice(remaining)
        print("no reasonable x and y found, returning (0,0)")
        return 0, 0


# -----------------------------
# Main generator per image
# -----------------------------
def generate_one(image_path: str, label_path: str, seed: int = None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    placed_elements: List[elm.Element] = []

    # Build component list: at least 1 per class, plus extras
    comps = CLASSES2.copy()
    extra_n = random.randint(*EXTRA_COMPONENTS_RANGE)
    comps += random.choices(CLASSES, k=extra_n)
    random.shuffle(comps)
    comps.append("swi_real")

    d = schemdraw.Drawing(
        file=image_path,
        show=False,
        # canvas=[0, CANVAS_W, 0, CANVAS_H],
        canvas="matplotlib",
        transparent=False,
    )

    drawn_elements = []
    # rng = random.Random()

    for cls in comps:
        angle = random.choice(ORIENTS)
        cx, cy = choose_position(placed_elements)
        elem = make_element(cls, angle).at((cx, cy)).theta(angle)
        d += elem

        cur = {"cls": cls, "elem": elem}

        drawn_elements.append(cur)
        placed_elements.append(elem)

    # Draw wires
    # if needWire:

    need_wire = True  # rng.random() < 0.5
    if need_wire:
        wires_n = random.randint(*WIRES_RANGE)
        for _ in range(wires_n):
            a, b = random.sample(placed_elements, 2)
            abbox = a.get_bbox(transform=True)
            bbox = b.get_bbox(transform=True)
            a_rect = bbox_to_rect(abbox)
            b_rect = bbox_to_rect(bbox)
            p1 = random_point_on_rect_edge(a_rect)
            p2 = random_point_on_rect_edge(b_rect)
            path = l_shaped_path(p1, p2)

            for s in range(len(path) - 1):
                (x1, y1), (x2, y2) = path[s], path[s + 1]
                lw = 0.5
                d += elm.Line(lw=lw).at((x1, y1)).to((x2, y2))

    # fig = d.draw(show=False)
    dxmin, dymin, dxmax, dymax = d.get_bbox()
    spanx = dxmax - dxmin
    spany = dymax - dymin

    d.save(image_path, transparent=False)  # , dpi=DPI, transparent=False)
    matplotlib.pyplot.close()

    # -----------------------------
    # Read saved image size (pixels)
    # -----------------------------
    with Image.open(image_path) as im:
        W, H = im.size  # PIL uses (W,H)

    yolo_lines = []

    for item in drawn_elements:
        cls = item["cls"]
        elem = item["elem"]
        # r = item["rect"]
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

    if not yolo_no_overlap(yolo_lines):
        print("overlap detected")
        os.remove(image_path)
        return
    os.makedirs(os.path.dirname(label_path), exist_ok=True)
    with open(label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_lines))


# -----------------------------
# Dataset loop + split
# -----------------------------
def generate_dataset(
    out_dir: str,
    n_images: int = 200,
    val_ratio: float = 0.2,
    seed: int = 0,
    needWire: bool = True,
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
        img_path = os.path.join(out_dir, "images", split, f"s{i}.png")
        lab_path = os.path.join(out_dir, "labels", split, f"s{i}.txt")

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
    generate_dataset("a6b6", n_images=2000, val_ratio=0.1, seed=7)
