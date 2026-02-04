import json
import argparse
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import numpy as np
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox


# ----------------------------
# Data
# ----------------------------
@dataclass
class AutoNode:
    id: int
    area: int
    bbox_xywh: Tuple[int, int, int, int]
    centroid_xy: Tuple[float, float]


@dataclass
class ManualNode:
    id: int
    x: int
    y: int
    radius: int
    kind: str = "manual_circle"


@dataclass
class ComponentItem:
    id: int
    category_id: int
    category_name: str
    instance_name: str
    bbox_xywh: Tuple[int, int, int, int]


# ----------------------------
# COCO per-image helpers
# ----------------------------
def load_per_image_coco(json_path: Path) -> dict:
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_category_map(data: dict) -> Dict[int, str]:
    mp = {}
    for c in data.get("categories", []):
        cid = c.get("id")
        name = c.get("name")
        if cid is not None and name:
            mp[int(cid)] = str(name)
    return mp


def build_components(data: dict) -> List[ComponentItem]:
    cat_map = build_category_map(data)
    counter: Dict[str, int] = {}
    comps: List[ComponentItem] = []
    inst_id = 1
    for ann in data.get("annotations", []):
        bbox = ann.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        x, y, w, h = bbox
        cat_id = int(ann.get("category_id", -1))
        cat_name = cat_map.get(cat_id, f"cat{cat_id}")
        counter.setdefault(cat_name, 0)
        counter[cat_name] += 1
        inst_name = f"{cat_name}_{counter[cat_name]}"
        comps.append(
            ComponentItem(
                id=inst_id,
                category_id=cat_id,
                category_name=cat_name,
                instance_name=inst_name,
                bbox_xywh=(int(round(x)), int(round(y)), int(round(w)), int(round(h))),
            )
        )
        inst_id += 1
    return comps


def load_component_bboxes(data: dict) -> List[Tuple[int, int, int, int]]:
    bboxes = []
    for ann in data.get("annotations", []):
        bbox = ann.get("bbox", None)
        if bbox and len(bbox) == 4:
            x, y, w, h = bbox
            bboxes.append((int(round(x)), int(round(y)), int(round(w)), int(round(h))))
    return bboxes


# ----------------------------
# Wire blobs (auto nodes)
# ----------------------------
def mask_components_white(
    img_bgr: np.ndarray, bboxes_xywh: List[Tuple[int, int, int, int]], pad: int = 2
) -> np.ndarray:
    out = img_bgr.copy()
    H, W = out.shape[:2]
    for x, y, w, h in bboxes_xywh:
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(W, x + w + pad)
        y1 = min(H, y + h + pad)
        out[y0:y1, x0:x1] = 255
    return out


def make_wire_binary(
    masked_bgr: np.ndarray, blur_ksize: int = 3, open_iter: int = 1, close_iter: int = 2
) -> np.ndarray:
    gray = cv2.cvtColor(masked_bgr, cv2.COLOR_BGR2GRAY)
    if blur_ksize > 0:
        gray = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    if open_iter > 0:
        bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, k, iterations=open_iter)
    if close_iter > 0:
        bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, k, iterations=close_iter)
    return bw


def find_auto_nodes_from_bw(bw: np.ndarray, min_area: int = 80, connectivity: int = 8):
    num, labels, stats, centroids = cv2.connectedComponentsWithStats(
        (bw > 0).astype(np.uint8), connectivity=connectivity
    )

    auto_nodes: List[AutoNode] = []
    label_map = np.zeros_like(labels, dtype=np.int32)
    new_id = 1
    for lab in range(1, num):
        x, y, w, h, area = stats[lab].tolist()
        if area < min_area:
            continue
        cx, cy = centroids[lab].tolist()
        auto_nodes.append(
            AutoNode(new_id, int(area), (x, y, w, h), (float(cx), float(cy)))
        )
        label_map[labels == lab] = new_id
        new_id += 1
    return auto_nodes, label_map


# ----------------------------
# Tk GUI
# ----------------------------
class App:
    def __init__(
        self,
        root,
        img_bgr,
        auto_nodes,
        label_map,
        components,
        out_path,
        image_path,
        comp_json_path,
        params,
    ):
        self.root = root
        self.root.title("Wire Nodes Annotator (Tkinter)")

        self.img_bgr = img_bgr
        self.H, self.W = img_bgr.shape[:2]

        self.auto_nodes = auto_nodes
        self.label_map = label_map
        self.components = components

        self.manual_nodes: List[ManualNode] = []
        self.next_node_id = (max([n.id for n in auto_nodes]) + 1) if auto_nodes else 1

        self.selected: Optional[Tuple[str, int]] = (
            None  # ("node", id) or ("component", id)
        )

        self.out_path = out_path
        self.image_path = image_path
        self.comp_json_path = comp_json_path
        self.params = params

        # --- layout: left canvas, right panel ---
        self.main = ttk.Frame(root)
        self.main.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main, width=self.W, height=self.H, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        right = ttk.Frame(self.main)
        right.grid(row=0, column=1, sticky="ns")
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(0, weight=1)

        # right: two listboxes
        ttk.Label(right, text="Nodes").grid(row=0, column=0, padx=6, pady=(6, 0))
        ttk.Label(right, text="Components").grid(row=0, column=1, padx=6, pady=(6, 0))

        self.nodes_list = tk.Listbox(right, width=22, height=30, exportselection=False)
        self.comps_list = tk.Listbox(right, width=28, height=30, exportselection=False)
        self.nodes_list.grid(row=1, column=0, padx=6, pady=6)
        self.comps_list.grid(row=1, column=1, padx=6, pady=6)

        # buttons
        btns = ttk.Frame(right)
        btns.grid(row=2, column=0, columnspan=2, pady=(0, 8))
        ttk.Button(btns, text="Save", command=self.on_save).grid(
            row=0, column=0, padx=6
        )
        ttk.Button(btns, text="Undo", command=self.on_undo).grid(
            row=0, column=1, padx=6
        )
        ttk.Button(btns, text="Reset", command=self.on_reset).grid(
            row=0, column=2, padx=6
        )

        # bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.nodes_list.bind("<<ListboxSelect>>", self.on_select_node)
        self.comps_list.bind("<<ListboxSelect>>", self.on_select_comp)
        self.root.bind("<KeyPress-u>", lambda e: self.on_undo())
        self.root.bind("<KeyPress-s>", lambda e: self.on_save())
        self.root.bind("<Escape>", lambda e: self.on_reset())

        self.populate_lists()
        self.redraw()

    def populate_lists(self):
        self.nodes_list.delete(0, tk.END)
        for nid in self.get_all_node_ids():
            self.nodes_list.insert(tk.END, f"node{nid}")

        self.comps_list.delete(0, tk.END)
        for c in self.components:
            self.comps_list.insert(tk.END, c.instance_name)

    def get_all_node_ids(self) -> List[int]:
        return [n.id for n in self.auto_nodes] + [m.id for m in self.manual_nodes]

    def get_auto_node(self, nid: int) -> Optional[AutoNode]:
        return next((n for n in self.auto_nodes if n.id == nid), None)

    def get_manual_node(self, nid: int) -> Optional[ManualNode]:
        return next((m for m in self.manual_nodes if m.id == nid), None)

    def get_component_by_index(self, idx: int) -> Optional[ComponentItem]:
        if 0 <= idx < len(self.components):
            return self.components[idx]
        return None

    def darken(self, img, alpha=0.25):
        return (img.astype(np.float32) * alpha).clip(0, 255).astype(np.uint8)

    def draw_auto_node_contour(self, vis, node: AutoNode):
        mask = (self.label_map == node.id).astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            cv2.drawContours(vis, contours, -1, (0, 255, 0), 1)
        x, y, w, h = node.bbox_xywh
        cv2.putText(
            vis,
            str(node.id),
            (x + 2, max(10, y + 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.28,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

    def draw_manual_node(self, vis, node: ManualNode):
        cv2.circle(vis, (node.x, node.y), node.radius, (0, 255, 255), -1)
        cv2.putText(
            vis,
            str(node.id),
            (node.x + node.radius + 2, node.y + 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.28,
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )

    def draw_component(self, vis, comp: ComponentItem):
        x, y, w, h = comp.bbox_xywh
        cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 255), 1)
        cv2.putText(
            vis,
            comp.instance_name,
            (x + 2, max(10, y - 4)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.28,
            (255, 0, 255),
            1,
            cv2.LINE_AA,
        )

    def render(self) -> np.ndarray:
        if self.selected is None:
            vis = self.img_bgr.copy()
            for n in self.auto_nodes:
                self.draw_auto_node_contour(vis, n)
            for m in self.manual_nodes:
                self.draw_manual_node(vis, m)
            return vis

        kind, sid = self.selected
        vis = self.darken(self.img_bgr, alpha=0.25)

        if kind == "node":
            an = self.get_auto_node(sid)
            if an is not None:
                self.draw_auto_node_contour(vis, an)
            mn = self.get_manual_node(sid)
            if mn is not None:
                self.draw_manual_node(vis, mn)
        elif kind == "component":
            comp = next((c for c in self.components if c.id == sid), None)
            if comp is not None:
                self.draw_component(vis, comp)

        return vis

    def redraw(self):
        vis_bgr = self.render()
        vis_rgb = cv2.cvtColor(vis_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(vis_rgb)
        self.tk_img = ImageTk.PhotoImage(pil)  # keep reference!
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    # -------- event handlers --------
    def on_canvas_click(self, event):
        # click canvas: if focused -> reset, else add manual node
        if self.selected is not None:
            self.on_reset()
            return

        x, y = int(event.x), int(event.y)
        self.manual_nodes.append(ManualNode(self.next_node_id, x, y, radius=6))
        self.next_node_id += 1
        self.populate_lists()
        self.redraw()

    def on_select_node(self, event):
        sel = self.nodes_list.curselection()
        if not sel:
            return
        text = self.nodes_list.get(sel[0])
        # parse "node{id}"
        nid = int(text.replace("node", ""))
        self.selected = ("node", nid)
        self.redraw()

    def on_select_comp(self, event):
        sel = self.comps_list.curselection()
        if not sel:
            return
        comp = self.get_component_by_index(sel[0])
        if comp is None:
            return
        self.selected = ("component", comp.id)
        self.redraw()

    def on_reset(self):
        self.selected = None
        self.nodes_list.selection_clear(0, tk.END)
        self.comps_list.selection_clear(0, tk.END)
        self.redraw()

    def on_undo(self):
        if not self.manual_nodes:
            return
        rm = self.manual_nodes.pop()
        if (
            self.selected is not None
            and self.selected[0] == "node"
            and self.selected[1] == rm.id
        ):
            self.selected = None
        self.populate_lists()
        self.redraw()

    def on_save(self):
        payload = {
            "image": self.image_path.name,
            "source_component_json": self.comp_json_path.name,
            "params": self.params,
            "nodes_auto": [asdict(n) for n in self.auto_nodes],
            "nodes_manual": [asdict(m) for m in self.manual_nodes],
            "components": [asdict(c) for c in self.components],
            "nodes_all": (
                [{"id": n.id, "kind": "auto_blob"} for n in self.auto_nodes]
                + [{"id": m.id, "kind": m.kind} for m in self.manual_nodes]
            ),
        }
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        with self.out_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Saved", f"Saved to:\n{self.out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--mask_pad", type=int, default=2)
    ap.add_argument("--blur", type=int, default=3)
    ap.add_argument("--open_iter", type=int, default=1)
    ap.add_argument("--close_iter", type=int, default=2)
    ap.add_argument("--min_area", type=int, default=80)
    ap.add_argument("--connectivity", type=int, default=8)
    args = ap.parse_args()

    image_path = Path(args.image)
    comp_json_path = Path(args.json)
    out_path = (
        Path(args.out)
        if args.out
        else comp_json_path.with_name(f"{image_path.stem}_nodes.json")
    )

    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"Failed to read image: {image_path}")

    data = load_per_image_coco(comp_json_path)
    comps = build_components(data)
    comp_bboxes = load_component_bboxes(data)

    masked = mask_components_white(img, comp_bboxes, pad=args.mask_pad)
    bw = make_wire_binary(
        masked,
        blur_ksize=args.blur,
        open_iter=args.open_iter,
        close_iter=args.close_iter,
    )
    auto_nodes, label_map = find_auto_nodes_from_bw(
        bw, min_area=args.min_area, connectivity=args.connectivity
    )

    params = {
        "mask_pad": args.mask_pad,
        "blur": args.blur,
        "open_iter": args.open_iter,
        "close_iter": args.close_iter,
        "min_area": args.min_area,
        "connectivity": args.connectivity,
    }

    root = tk.Tk()
    App(
        root,
        img,
        auto_nodes,
        label_map,
        comps,
        out_path,
        image_path,
        comp_json_path,
        params,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
