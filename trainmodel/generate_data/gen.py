#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen.py (wire-topology -> random components on edges)
- Build many wire-only topology templates (graphs)
- For each wire edge: split by density and randomly place bipoles (to[]) or node components (node[]) along segments
- Add explicit junction dots (circ) and wire-jump crossings (to[crossing])
- Save:
  - circuit.tex / circuit.pdf / circuit.png
  - ground_truth.json (includes graph + per-component geometric GT)

Windows notes:
- PDF->PNG: tries pdftocairo, then mutool, then ImageMagick.
- If pdftocairo fails on Windows, install MuPDF and put `mutool` in PATH.

Usage:
  python gen.py --out out_circuits --n 50 --seed 42 --density 2 --p_node 0.55 --p_crossing 0.3 --p_junction 0.5
"""

import os
import json
import math
import random
import shutil
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional, Any


# ----------------------------
# Data structures
# ----------------------------
Pt = Tuple[float, float]

COMP_SIZE = 2.0  # cm，保守估计
CELL_W = 4.0 * COMP_SIZE  # 比一个子拓扑宽
CELL_H = 3.0 * COMP_SIZE
CELL_PAD = 1.5 * COMP_SIZE


YOLO_CLASSES = [
    "ac_src",
    "battery",  # 电压源（battery/battery1/vsourceAM）
    "cap",  # C / cC
    "curr_src",  # isourceAM
    "diode",  # D* / sD*
    "inductor",  # L
    "resistor",  # R
    "swi_ideal",  # spst
    "swi_real",  # nigfete / nigbt
    "volt_src",  # （如果你坚持和 battery 分开，就把 vsourceAM 放这里）
    "xformer",  # transformer core
]
CLASS_ID = {c: i for i, c in enumerate(YOLO_CLASSES)}


def map_ctype_to_yolo(ctype: str) -> str:
    # bipoles
    if ctype == "R":
        return "resistor"
    if ctype in ("C", "cC"):
        return "cap"
    if ctype == "L":
        return "inductor"
    if ctype in ("D*", "sD*"):
        return "diode"

    # sources
    if ctype in ("battery", "battery1"):
        return "battery"
    if ctype == "vsourceAM":
        return "volt_src"
    if ctype == "isourceAM":
        return "curr_src"

    # switches
    if ctype == "spst":
        return "swi_ideal"
    if ctype in ("nigfete", "nigbt"):
        return "swi_real"

    # transformer
    if ctype == "transformer core":
        return "xformer"
    if ctype == "sV":
        return "ac_src"

    # things you probably DON'T want to detect as objects in YOLO
    # (wires / topology artifacts)
    if ctype in ("junction", "crossing", "ground", "tlground"):
        return ""  # skip

    return ""  # unknown -> skip


def cell_origin(i, cols):
    r = i // cols
    c = i % cols
    ox = c * (CELL_W + CELL_PAD)
    oy = r * (CELL_H + CELL_PAD)
    return ox, oy


@dataclass
class ComponentGT:
    name: str
    ctype: str  # e.g., "R", "C", "L", "D*", "nigbt", "junction", "crossing"
    kind: str  # "to" or "node"
    start: Optional[Pt] = None
    end: Optional[Pt] = None
    mid: Optional[Pt] = None
    at: Optional[Pt] = None
    extra: Optional[Dict[str, Any]] = None


@dataclass
class WireTemplate:
    """
    Wire-only topology template:
      nodes: name -> (x,y)
      edges: (u,v) list, undirected-ish (we draw u->v)
      junctions: node names to explicitly draw node[circ]
      crossings: list of vertical/horizontal jump segments drawn with to[crossing]
      terminals: optional port node names for future composition (not required)
    """

    name: str
    nodes: Dict[str, Pt]
    edges: List[Tuple[str, str]]
    junctions: List[str]
    crossings: List[Tuple[Pt, Pt]]
    terminals: List[str]


# ----------------------------
# Helpers
# ----------------------------
def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def which(bin_name: str) -> Optional[str]:
    return shutil.which(bin_name)


def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> None:
    proc = subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n\n{proc.stdout}")


def fmt_pt(p: Pt) -> str:
    return f"({p[0]:.3f},{p[1]:.3f})"


def _p(x: float, y: float) -> str:
    return f"({x:.3f},{y:.3f})"


def midpoint(a: Pt, b: Pt) -> Pt:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


# ----------------------------
# Component catalog
# ----------------------------
def build_component_catalog() -> List[Dict[str, Any]]:
    """
    kind="to": used in to[<element>, l=...]
    kind="node": used as node[<node>]{text}
    """
    return [
        # Bipoles / sources
        {
            "kind": "node",
            "ctype": "R",
            "node": "resistorshape",
            # "element": "R",
            # "label": r"$R_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "sV",
            "node": "vsourcesinshape",
            # "element": "R",
            # "label": r"$R_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "C",
            "node": "capacitorshape",
            # "element": "C",
            # "label": r"$C_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "cC",
            "node": "ccapacitorshape",
            # "element": "cC",
            # "label": r"$C_{%d}$",
            "text": "",
        },  # polarized curved
        {
            "kind": "node",
            "ctype": "L",
            "node": "cuteinductorshape",
            # "element": "L",
            # "label": r"$L_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "D*",
            "node": "emptydiodeshape",
            # "element": "D*",
            # "label": r"$D_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "sD*",
            "node": "emptysdiodeshape",
            # "element": "sD*",
            # "label": r"$D_{%d}$",
            "text": "",
        },  # schottky
        {
            "kind": "node",
            "ctype": "battery",
            "node": "batteryshape",
            # "element": "battery",
            # "label": r"$V_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "battery1",
            "node": "battery1shape",
            # "element": "battery1",
            # "label": r"$V_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "vsourceAM",
            "node": "vsourceAMshape",
            # "element": "vsourceAM",
            # "label": r"$V_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "isourceAM",
            "node": "isourceAMshape",
            # "element": "isourceAM",
            # "label": r"$I_{%d}$",
            "text": "",
        },
        {
            "kind": "node",
            "ctype": "spst",
            "node": "cspstshape",
            # "element": "spst",
            # "label": r"$S_{%d}$",
            "text": "",
        },
        # Node components
        {"kind": "node", "ctype": "nigfete", "node": "nigfete", "text": ""},
        {"kind": "node", "ctype": "nigbt", "node": "nigbt", "text": ""},
        {
            "kind": "node",
            "ctype": "transformer core",
            "node": "transformer core",
            "text": "",
        },
        {"kind": "node", "ctype": "ground", "node": "ground", "text": ""},
        {"kind": "node", "ctype": "tlground", "node": "tlground", "text": ""},
    ]


# ----------------------------
# Wire topology template maker (graph-only)
# ----------------------------
def make_templates(W: float, H: float) -> List[WireTemplate]:
    """
    Wire-only topology templates (no components).
    Includes common canonical connection forms and a composed template.
    """

    def off(nodes: Dict[str, Pt], dx: float, dy: float) -> Dict[str, Pt]:
        return {k: (v[0] + dx, v[1] + dy) for k, v in nodes.items()}

    def merge(
        a: WireTemplate, b: WireTemplate, name: str, connect: List[Tuple[str, str]]
    ) -> WireTemplate:
        # rename b nodes to avoid clashes
        bmap = {k: f"b_{k}" for k in b.nodes.keys()}
        nodes = dict(a.nodes)
        nodes.update({bmap[k]: b.nodes[k] for k in b.nodes})
        edges = list(a.edges) + [(bmap[u], bmap[v]) for (u, v) in b.edges]
        junctions = list(a.junctions) + [bmap[x] for x in b.junctions]
        crossings = list(a.crossings) + list(b.crossings)
        for ua, vb in connect:
            edges.append((ua, bmap[vb]))
        terminals = list(a.terminals) + [bmap[x] for x in b.terminals]
        return WireTemplate(
            name=name,
            nodes=nodes,
            edges=edges,
            junctions=junctions,
            crossings=crossings,
            terminals=terminals,
        )

    # anchors
    x0 = W * 0.10
    x1 = W * 0.30
    x2 = W * 0.50
    x3 = W * 0.70
    x4 = W * 0.90

    y0 = H * 0.15
    y1 = H * 0.35
    y2 = H * 0.55
    y3 = H * 0.80

    templates: List[WireTemplate] = []

    # 1) series chain
    nodes = {"in": (x0, y2), "n1": (x1, y2), "n2": (x2, y2), "out": (x4, y2)}
    edges = [("in", "n1"), ("n1", "n2"), ("n2", "out")]
    templates.append(
        WireTemplate(
            "series_chain",
            nodes,
            edges,
            junctions=["n1", "n2"],
            crossings=[],
            terminals=["in", "out"],
        )
    )

    # 2) parallel_2
    nodes = {"in": (x0, y2), "out": (x4, y2), "u": (x2, y3), "d": (x2, y1)}
    edges = [("in", "u"), ("u", "out"), ("in", "d"), ("d", "out")]
    templates.append(
        WireTemplate(
            "parallel_2",
            nodes,
            edges,
            junctions=["in", "out"],
            crossings=[],
            terminals=["in", "out"],
        )
    )

    # 3) T-network
    nodes = {
        "in": (x0, y2),
        "a": (x1, y2),
        "b": (x3, y2),
        "out": (x4, y2),
        "sh": (x2, y0),
    }
    edges = [("in", "a"), ("a", "b"), ("b", "out"), ("a", "sh")]
    templates.append(
        WireTemplate(
            "T_network",
            nodes,
            edges,
            junctions=["a", "b"],
            crossings=[],
            terminals=["in", "out"],
        )
    )

    # 4) Pi-network
    nodes = {
        "in": (x0, y2),
        "out": (x4, y2),
        "mid": (x2, y2),
        "shL": (x0, y0),
        "shR": (x4, y0),
    }
    edges = [("in", "mid"), ("mid", "out"), ("in", "shL"), ("out", "shR")]
    templates.append(
        WireTemplate(
            "Pi_network",
            nodes,
            edges,
            junctions=["in", "out", "mid"],
            crossings=[],
            terminals=["in", "out"],
        )
    )

    # 5) Y-star
    nodes = {"A": (x1, y3), "B": (x1, y1), "C": (x3, y2), "O": (x2, y2)}
    edges = [("O", "A"), ("O", "B"), ("O", "C")]
    templates.append(
        WireTemplate(
            "Y_star",
            nodes,
            edges,
            junctions=["O"],
            crossings=[],
            terminals=["A", "B", "C"],
        )
    )

    # 6) Delta
    nodes = {"A": (x1, y3), "B": (x1, y1), "C": (x3, y2)}
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    templates.append(
        WireTemplate(
            "Delta", nodes, edges, junctions=[], crossings=[], terminals=["A", "B", "C"]
        )
    )

    # 7) Bridge (wheatstone-like)
    nodes = {"in": (x0, y2), "out": (x4, y2), "u": (x2, y3), "d": (x2, y1)}
    edges = [("in", "u"), ("u", "out"), ("in", "d"), ("d", "out"), ("u", "d")]
    templates.append(
        WireTemplate(
            "bridge",
            nodes,
            edges,
            junctions=["u", "d"],
            crossings=[],
            terminals=["in", "out"],
        )
    )

    # 8) ladder_2
    nodes = {
        "in": (x0, y2),
        "n1": (x1, y2),
        "n2": (x2, y2),
        "n3": (x3, y2),
        "out": (x4, y2),
        "g1": (x1, y0),
        "g2": (x3, y0),
    }
    edges = [
        ("in", "n1"),
        ("n1", "n2"),
        ("n2", "n3"),
        ("n3", "out"),
        ("n1", "g1"),
        ("n3", "g2"),
    ]
    templates.append(
        WireTemplate(
            "ladder_2",
            nodes,
            edges,
            junctions=["n1", "n2", "n3"],
            crossings=[],
            terminals=["in", "out"],
        )
    )

    # 9) mesh box + chord
    nodes = {
        "A": (x1, y1),
        "B": (x1, y3),
        "C": (x3, y3),
        "D": (x3, y1),
        "in": (x0, y2),
        "out": (x4, y2),
    }
    edges = [
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "A"),
        ("in", "A"),
        ("out", "C"),
        ("B", "D"),
    ]
    templates.append(
        WireTemplate(
            "box_mesh",
            nodes,
            edges,
            junctions=["A", "B", "C", "D"],
            crossings=[],
            terminals=["in", "out"],
        )
    )

    # 10) explicit crossing jump motif
    cx, cy = W * 0.5, H * 0.5
    nodes = {
        "L": (cx - W * 0.25, cy),
        "R": (cx + W * 0.25, cy),
        "B": (cx, cy - H * 0.25),
        "T": (cx, cy + H * 0.25),
    }
    edges = [("L", "R")]
    crossings = [((cx, cy - H * 0.25), (cx, cy + H * 0.25))]
    templates.append(
        WireTemplate(
            "crossing_jump",
            nodes,
            edges,
            junctions=[],
            crossings=crossings,
            terminals=["L", "R", "B", "T"],
        )
    )

    return templates


def normalize_wt(wt: WireTemplate):
    xs = [p[0] for p in wt.nodes.values()]
    ys = [p[1] for p in wt.nodes.values()]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    nodes2 = {}
    for k, (x, y) in wt.nodes.items():
        nx = (x - minx) / max(1e-6, (maxx - minx))
        ny = (y - miny) / max(1e-6, (maxy - miny))
        nodes2[k] = (nx, ny)

    return WireTemplate(
        name=wt.name,
        nodes=nodes2,
        edges=wt.edges,
        junctions=wt.junctions,
        crossings=wt.crossings,
        terminals=wt.terminals,
    )


def place_in_cell(wt: WireTemplate, ox, oy):
    nodes2 = {}
    for k, (nx, ny) in wt.nodes.items():
        x = ox + COMP_SIZE + nx * (CELL_W - 2 * COMP_SIZE)
        y = oy + COMP_SIZE + ny * (CELL_H - 2 * COMP_SIZE)
        nodes2[k] = (x, y)

    return WireTemplate(
        name=wt.name,
        nodes=nodes2,
        edges=wt.edges,
        junctions=wt.junctions,
        crossings=wt.crossings,
        terminals=wt.terminals,
    )


def wt_offset(wt: WireTemplate, dx: float, dy: float) -> WireTemplate:
    nodes2 = {k: (v[0] + dx, v[1] + dy) for k, v in wt.nodes.items()}
    return WireTemplate(
        name=wt.name,
        nodes=nodes2,
        edges=list(wt.edges),
        junctions=list(wt.junctions),
        crossings=list(wt.crossings),
        terminals=list(wt.terminals),
    )


def wt_rename(wt: WireTemplate, prefix: str) -> WireTemplate:
    # rename nodes to avoid collision
    mp = {k: f"{prefix}{k}" for k in wt.nodes.keys()}
    nodes2 = {mp[k]: v for k, v in wt.nodes.items()}
    edges2 = [(mp[u], mp[v]) for (u, v) in wt.edges]
    junctions2 = [mp[x] for x in wt.junctions if x in mp]
    crossings2 = list(wt.crossings)  # crossings are geometry-only; keep as-is
    terminals2 = [mp[x] for x in wt.terminals if x in mp]
    return WireTemplate(
        name=f"{wt.name}",
        nodes=nodes2,
        edges=edges2,
        junctions=junctions2,
        crossings=crossings2,
        terminals=terminals2,
    )


def compose_random_template(
    base_templates: List[WireTemplate],
    W: float,
    H: float,
    rng: random.Random,
    k_min: int = 2,
    k_max: int = 4,
    mode: str = "connect",  # "connect" | "bus"
) -> WireTemplate:

    assert mode in ("connect", "bus")

    k = rng.randint(k_min, k_max)
    picks = [rng.choice(base_templates) for _ in range(k)]

    # ---- layout planning: choose grid size based on k ----
    # Use near-square grid so it scales naturally with W/H.
    cols = max(1, math.ceil(math.sqrt(k)))
    rows = max(1, math.ceil(k / cols))

    # ---- W/H-driven padding/gap ----
    # These are FRACTIONS of W/H, not absolute cm.
    # Feel free to tweak: larger gap_frac => more separation, less crowding.
    gap_x = 0.08 * W
    gap_y = 0.10 * H

    # Keep some outer margin so drawings don't stick to border.
    margin_x = 0.06 * W
    margin_y = 0.08 * H

    # Effective drawable area after margins + gaps between cells
    avail_w = max(1e-6, W - 2 * margin_x - (cols - 1) * gap_x)
    avail_h = max(1e-6, H - 2 * margin_y - (rows - 1) * gap_y)

    cell_w = avail_w / cols
    cell_h = avail_h / rows

    # Inside each cell, reserve an inner padding region.
    # This ensures terminals/edges don't hug cell borders.
    inner_pad_x = 0.12 * cell_w
    inner_pad_y = 0.12 * cell_h

    composed_nodes: Dict[str, Pt] = {}
    composed_edges: List[Tuple[str, str]] = []
    composed_junctions: List[str] = []
    composed_crossings: List[Tuple[Pt, Pt]] = []
    composed_terminals: List[str] = []

    placed_modules: List[WireTemplate] = []

    def _bbox(nodes: Dict[str, Pt]) -> Tuple[float, float, float, float]:
        xs = [p[0] for p in nodes.values()]
        ys = [p[1] for p in nodes.values()]
        return (min(xs), min(ys), max(xs), max(ys))

    def _normalize_nodes(nodes: Dict[str, Pt]) -> Dict[str, Pt]:
        x1, y1, x2, y2 = _bbox(nodes)
        sx = max(1e-6, x2 - x1)
        sy = max(1e-6, y2 - y1)
        # map into [0,1]
        return {k: ((p[0] - x1) / sx, (p[1] - y1) / sy) for k, p in nodes.items()}

    def _place_into_cell(
        wt: WireTemplate, cell_ox: float, cell_oy: float, cw: float, ch: float
    ) -> WireTemplate:
        # normalize to [0,1] then scale into cell interior
        n01 = _normalize_nodes(wt.nodes)
        nodes2 = {}
        for nk, (u, v) in n01.items():
            x = cell_ox + inner_pad_x + u * max(1e-6, (cw - 2 * inner_pad_x))
            y = cell_oy + inner_pad_y + v * max(1e-6, (ch - 2 * inner_pad_y))
            nodes2[nk] = (x, y)
        return WireTemplate(
            name=wt.name,
            nodes=nodes2,
            edges=list(wt.edges),
            junctions=list(wt.junctions),
            crossings=list(wt.crossings),
            terminals=list(wt.terminals),
        )

    # ---- place each picked module into its own cell ----
    for i, wt in enumerate(picks):
        r = i // cols
        c = i % cols

        cell_ox = margin_x + c * (cell_w + gap_x)
        cell_oy = margin_y + r * (cell_h + gap_y)

        # place + jitter within cell (small jitter so it doesn't look too grid-robotic)
        jitter_x = (rng.random() * 0.10 - 0.05) * cell_w
        jitter_y = (rng.random() * 0.10 - 0.05) * cell_h

        # 1) put inside cell by scaling topology to cell interior
        m = _place_into_cell(wt, cell_ox, cell_oy, cell_w, cell_h)

        # 2) apply tiny jitter after placement (still safe because inner_pad exists)
        m = wt_offset(m, jitter_x, jitter_y)

        # 3) rename to avoid collisions
        m = wt_rename(m, prefix=f"m{i}_")

        # merge module content
        composed_nodes.update(m.nodes)
        composed_edges.extend(m.edges)
        composed_junctions.extend(m.junctions)
        composed_crossings.extend(m.crossings)
        composed_terminals.extend(m.terminals)

        placed_modules.append(m)

    # ---- Stitching (same logic as your original) ----
    if mode == "connect":
        for i in range(len(placed_modules) - 1):
            A = placed_modules[i]
            B = placed_modules[i + 1]

            ta = (
                rng.choice(A.terminals)
                if A.terminals
                else rng.choice(list(A.nodes.keys()))
            )
            tb = (
                rng.choice(B.terminals)
                if B.terminals
                else rng.choice(list(B.nodes.keys()))
            )

            composed_edges.append((ta, tb))
            composed_junctions.extend([ta, tb])

    elif mode == "bus":
        # Place bus in the middle of the whole canvas (W/H space), not inside a cell.
        bus_y = H * 0.50
        bus_x1 = W * 0.05
        bus_x2 = W * 0.95
        bus_a = "BUS_A"
        bus_b = "BUS_B"
        composed_nodes[bus_a] = (bus_x1, bus_y)
        composed_nodes[bus_b] = (bus_x2, bus_y)
        composed_edges.append((bus_a, bus_b))
        composed_junctions.extend([bus_a, bus_b])

        for m in placed_modules:
            t = (
                rng.choice(m.terminals)
                if m.terminals
                else rng.choice(list(m.nodes.keys()))
            )
            composed_edges.append((t, bus_a))
            composed_junctions.append(t)

    # de-duplicate junction list
    composed_junctions = list(dict.fromkeys(composed_junctions))

    return WireTemplate(
        name=f"COMPOSED_{mode}_{k}",
        nodes=composed_nodes,
        edges=composed_edges,
        junctions=composed_junctions,
        crossings=composed_crossings,
        terminals=composed_terminals,
    )


# ----------------------------
# Generation logic
# ----------------------------
class CircuitGenerator:
    def __init__(
        self,
        out_dir: str,
        seed: int = 0,
        n: int = 10,
        W: float = 4.0,
        H: float = 3.0,
        density: int = 1,
        p_node_component: float = 0.25,  # probability to insert node-type component on a segment
        p_junction: float = 0.35,  # probability to add -*, *-, *-* on bipole segments
        p_crossing: float = 0.40,  # optional extra internal crossing augmentation
        node_bias: float = 0.35,  # bias in picking node components
        force_both_kinds: bool = True,  # ensure each circuit has >=1 node and >=1 to
    ):
        self.out_dir = out_dir
        self.seed = seed
        self.n = n
        self.W = W
        self.H = H
        self.density = density
        self.p_node_component = p_node_component
        self.p_junction = p_junction
        self.p_crossing = p_crossing
        self.node_bias = node_bias
        self.force_both_kinds = force_both_kinds

        self.catalog = build_component_catalog()
        self.cat_to = [c for c in self.catalog if c["kind"] == "to"]
        self.cat_node = [c for c in self.catalog if c["kind"] == "node"]
        self.node_transistors = [
            c for c in self.cat_node if c["ctype"] in ("nigbt", "nigfete")
        ]

        random.seed(seed)

    def _pick_component(self) -> Dict[str, Any]:
        # 如果某一类为空，直接从另一类选
        if not self.cat_to and not self.cat_node:
            raise RuntimeError(
                "Component catalog is empty. Check build_component_catalog()."
            )

        if not self.cat_to:
            return random.choice(self.cat_node)
        if not self.cat_node:
            return random.choice(self.cat_to)

        # 两类都存在时：按 node_bias 混合采样
        if random.random() < self.node_bias:
            if self.node_transistors and random.random() < 0.85:
                return random.choice(self.node_transistors)
            return random.choice(self.cat_node)
        return random.choice(self.cat_to)

    def _edge_waypoints(self, a: Pt, b: Pt, density: int) -> List[Pt]:
        if density <= 0:
            return [a, b]
        pts = [a]
        for k in range(1, density + 1):
            t = k / (density + 1)
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        pts.append(b)
        return pts

    def _make_to_element(
        self, element: str, label: str, idx: int, with_current: bool
    ) -> str:
        ltxt = label % idx if "%d" in label else label
        if with_current:
            return f"{element}, l={ltxt}, i=${{i_{idx}}}$"
        return f"{element}, l={ltxt}"

    def _draw_edge_with_random_components(
        self,
        edge_name: str,
        pts: List[Pt],
        gt: List[ComponentGT],
        comp_counter: Dict[str, int],
    ) -> str:
        """
        Now each segment is drawn as its own \draw so each component can have its own local bounding box.
        """
        lines: List[str] = []
        cur = pts[0]

        for i in range(1, len(pts)):
            nxt = pts[i]
            comp = self._pick_component()

            use_node = (comp["kind"] == "node") and (
                random.random() < self.p_node_component
            )

            if comp["kind"] == "to" and not use_node:
                ctype = comp["ctype"]
                comp_counter.setdefault(ctype, 0)
                comp_counter[ctype] += 1
                idx = comp_counter[ctype]

                with_current = random.random() < 0.35
                elem_opts = self._make_to_element(
                    comp["element"], comp["label"], idx, with_current
                )

                junction_suffix = ""
                if random.random() < self.p_junction:
                    junction_suffix = random.choice([", -*", ", *-", ", *-*"])

                bbox_name = f"{ctype}_{idx}BB"
                # IMPORTANT: component alone in a scope
                lines.append(rf"\begin{{scope}}[local bounding box={bbox_name}]")
                lines.append(
                    rf"\draw {fmt_pt(cur)} to[{elem_opts}{junction_suffix}] {fmt_pt(nxt)};"
                )
                lines.append(r"\end{scope}")

                gt.append(
                    ComponentGT(
                        name=f"{ctype}_{idx}",
                        ctype=ctype,
                        kind="to",
                        start=cur,
                        end=nxt,
                        mid=midpoint(cur, nxt),
                        extra={
                            "edge": edge_name,
                            "element": comp["element"],
                            "junction": junction_suffix.strip(),
                        },
                    )
                )

            else:
                # Insert node at midpoint; draw short wire + node + short wire
                node = comp.get("node", comp["ctype"])
                ctype = comp["ctype"]
                comp_counter.setdefault(ctype, 0)
                comp_counter[ctype] += 1
                idx = comp_counter[ctype]

                m = midpoint(cur, nxt)
                txt = comp.get("text", "")

                # wire cur -> m
                lines.append(rf"\draw {fmt_pt(cur)} to[short] {fmt_pt(m)};")

                # node itself in bbox scope
                bbox_name = f"{ctype}_{idx}BB"
                lines.append(rf"\begin{{scope}}[local bounding box={bbox_name}]")
                if txt:
                    lines.append(rf"\draw {fmt_pt(m)} node[{node}]{{{txt}}};")
                else:
                    lines.append(rf"\draw {fmt_pt(m)} node[{node}]{{}};")
                lines.append(r"\end{scope}")

                # wire m -> nxt (optional junction marker)
                junction = ""
                if random.random() < self.p_junction:
                    junction = random.choice(["-*", "*-", "*-*"])
                opts = "short" + (f", {junction}" if junction else "")
                lines.append(rf"\draw {fmt_pt(m)} to[{opts}] {fmt_pt(nxt)};")

                gt.append(
                    ComponentGT(
                        name=f"{ctype}_{idx}",
                        ctype=ctype,
                        kind="node",
                        at=m,
                        extra={"edge": edge_name, "node": node},
                    )
                )

            cur = nxt

        return "\n".join(lines)

    def _optional_crossing_and_branch(self, gt: List[ComponentGT]) -> str:
        """
        Extra internal branch augmentation:
          - sometimes junction cross (circ)
          - sometimes crossing jump (to[crossing])
        """
        if random.random() > self.p_crossing:
            return ""

        lines: List[str] = []
        cx, cy = self.W * 0.5, self.H * 0.5
        h1 = (cx - self.W * 0.30, cy)
        h2 = (cx + self.W * 0.30, cy)
        v1 = (cx, cy - self.H * 0.35)
        v2 = (cx, cy + self.H * 0.35)

        do_junction = random.random() < 0.5

        if do_junction:
            lines.append(
                f"\\draw {fmt_pt(h1)} to[short] {fmt_pt((cx, cy))} node[circ]{{}} to[short] {fmt_pt(h2)};"
            )
            lines.append(
                f"\\draw {fmt_pt(v1)} to[short] {fmt_pt((cx, cy))} to[short] {fmt_pt(v2)};"
            )
            gt.append(
                ComponentGT(
                    name="junction_extra_1",
                    ctype="junction",
                    kind="node",
                    at=(cx, cy),
                    extra={"style": "circ", "note": "extra_branch"},
                )
            )
        else:
            lines.append(f"\\draw {fmt_pt(h1)} to[short] {fmt_pt(h2)};")
            lines.append(f"\\draw {fmt_pt(v1)} to[crossing] {fmt_pt(v2)};")
            gt.append(
                ComponentGT(
                    name="crossing_extra_1",
                    ctype="crossing",
                    kind="to",
                    start=v1,
                    end=v2,
                    mid=(cx, cy),
                    extra={"style": "crossing", "note": "extra_branch"},
                )
            )

        return "\n".join(lines)

    def _latex_doc(self, tikz_body: str, labels_filename: str) -> str:
        # labels_filename 只传文件名，不传路径（LaTeX 在 workdir 里写）
        return rf"""
    \documentclass[border=2pt]{{standalone}}
    \usepackage[siunitx]{{circuitikz}}
    \usepackage{{pgfmath}}
    \usetikzlibrary{{arrows.meta,calc}}

    \begin{{document}}

    % ---- write YOLO labels to file ----
    \newwrite\posfile
    \immediate\openout\posfile={labels_filename}

    \begin{{circuitikz}}[
    american voltages,
    american currents,
    x=1cm, y=1cm
    ]
    {tikz_body}

    % ---- helper: compute normalized YOLO bbox for a given local bounding box ----
    \newcommand{{\WriteYoloBBox}}[2]{{%
    % #1 = bbox name (without parentheses), #2 = class id
    \path (#1.south west); \pgfgetlastxy{{\rOneMinX}}{{\rOneMinY}}
    \path (#1.north east); \pgfgetlastxy{{\rOneMaxX}}{{\rOneMaxY}}

    \path (current bounding box.south west); \pgfgetlastxy{{\canvasminx}}{{\canvasminy}}
    \path (current bounding box.north east); \pgfgetlastxy{{\canvasmaxx}}{{\canvasmaxy}}

    \newdimen\canvaswidth
    \newdimen\canvasheight
    \pgfmathsetlength{{\canvaswidth}}{{\canvasmaxx-\canvasminx}}
    \pgfmathsetlength{{\canvasheight}}{{\canvasmaxy-\canvasminy}}

    \pgfmathsetmacro{{\widthratio}}{{(\rOneMaxX-\rOneMinX)/(\canvaswidth)}}
    \pgfmathsetmacro{{\heightratio}}{{(\rOneMaxY-\rOneMinY)/(\canvasheight)}}
    \pgfmathsetmacro{{\xpositionratio}}{{(\rOneMinX+\rOneMaxX-\canvasminx-\canvasminx)/2/(\canvaswidth)}}
    \pgfmathsetmacro{{\ypositionratio}}{{1-(\rOneMinY+\rOneMaxY-\canvasminy-\canvasminy)/2/(\canvasheight)}}

    \immediate\write\posfile{{#2\space \xpositionratio\space \ypositionratio\space \widthratio\space \heightratio}}
    }}

    % ---- YOLO exports inserted here ----
    %__YOLO_EXPORTS__

    \end{{circuitikz}}
    \immediate\closeout\posfile
    \end{{document}}
    """.strip()

    def _compile_tex_to_pdf(self, tex_path: str, workdir: str) -> str:
        pdf_path = os.path.splitext(tex_path)[0] + ".pdf"
        latex = which("pdflatex") or which("lualatex") or which("xelatex")
        if latex is None:
            raise RuntimeError(
                "No LaTeX engine found (pdflatex/lualatex/xelatex). Please install TeX Live or MiKTeX."
            )

        cmd = [
            latex,
            "-interaction=nonstopmode",
            "-halt-on-error",
            os.path.basename(tex_path),
        ]
        run_cmd(cmd, cwd=workdir)

        if not os.path.exists(pdf_path):
            pdf_path = os.path.join(workdir, os.path.basename(pdf_path))
        return pdf_path

    def _pdf_to_png(self, pdf_path: str, png_path: str, dpi: int = 300) -> None:
        out_dir = os.path.dirname(os.path.abspath(png_path))
        os.makedirs(out_dir, exist_ok=True)

        # 1) pdftocairo
        pdftocairo = which("pdftocairo")
        if pdftocairo:
            out_base = os.path.splitext(png_path)[0]
            cmd = [
                pdftocairo,
                "-png",
                "-singlefile",
                "-r",
                str(dpi),
                pdf_path,
                out_base,
            ]
            proc = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            if proc.returncode == 0:
                produced = out_base + ".png"
                if os.path.exists(produced):
                    if produced != png_path:
                        os.replace(produced, png_path)
                    return
            print("pdftocairo failed with output:\n", proc.stdout)

        # 2) MuPDF mutool
        mutool = which("mutool")
        if mutool:
            cmd = [mutool, "draw", "-r", str(dpi), "-o", png_path, pdf_path]
            proc = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            if proc.returncode == 0 and os.path.exists(png_path):
                return
            print("mutool failed with output:\n", proc.stdout)

        # 3) ImageMagick
        magick = which("magick")
        convert = which("convert")
        if magick:
            cmd = [magick, "-density", str(dpi), pdf_path, "-quality", "100", png_path]
            proc = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            if proc.returncode == 0 and os.path.exists(png_path):
                return
            print("magick failed with output:\n", proc.stdout)
        elif convert and ("System32" not in convert):
            cmd = [convert, "-density", str(dpi), pdf_path, "-quality", "100", png_path]
            proc = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            if proc.returncode == 0 and os.path.exists(png_path):
                return
            print("convert failed with output:\n", proc.stdout)

        raise RuntimeError(
            "PDF->PNG conversion failed.\n"
            "Recommended fix on Windows: install MuPDF and ensure `mutool` is in PATH.\n"
            "Alternatively install Poppler (pdftocairo) with its DLLs correctly in PATH."
        )

    def _ensure_both_kinds(
        self, gt: List[ComponentGT], comp_counter: Dict[str, int], tikz_lines: List[str]
    ) -> None:
        """
        Ensure at least one 'node' and one 'to' appear (optional).
        If missing, add a transistor node at a random point, or add a resistor segment between two random graph nodes.
        """
        if not self.force_both_kinds:
            return

        has_node = any(c.kind == "node" for c in gt)
        has_to = any(c.kind == "to" for c in gt)

        # If no node: add a transistor node at center-ish (pure augmentation)
        if not has_node:
            c = random.choice(self.node_transistors) if self.node_transistors else None
            if c:
                m = (self.W * 0.5, self.H * 0.5)
                node = c.get("node", c["ctype"])
                txt = c.get("text", "Q")
                tikz_lines.append(f"\\draw {fmt_pt(m)} node[{node}]{{{txt}}};")
                comp_counter.setdefault(c["ctype"], 0)
                comp_counter[c["ctype"]] += 1
                gt.append(
                    ComponentGT(
                        name=f"{c['ctype']}_{comp_counter[c['ctype']]}",
                        ctype=c["ctype"],
                        kind="node",
                        at=m,
                        extra={"note": "forced_node"},
                    )
                )

        # If no to: add a resistor somewhere (rare)
        if not has_to:
            a = (self.W * 0.2, self.H * 0.2)
            b = (self.W * 0.4, self.H * 0.2)
            comp_counter.setdefault("R", 0)
            comp_counter["R"] += 1
            idx = comp_counter["R"]
            tikz_lines.append(f"\\draw {fmt_pt(a)} to[R, l=$R_{{{idx}}}$] {fmt_pt(b)};")
            gt.append(
                ComponentGT(
                    name=f"R_{idx}",
                    ctype="R",
                    kind="to",
                    start=a,
                    end=b,
                    mid=midpoint(a, b),
                    extra={"note": "forced_to"},
                )
            )

    def generate_one(self, idx: int) -> None:
        templates = make_templates(self.W, self.H)

        rng = random.Random(self.seed * 1000003 + idx)
        if rng.random() < 0.6:

            wt = compose_random_template(
                base_templates=templates,
                W=self.W,
                H=self.H,
                rng=rng,
                k_min=2,
                k_max=4,
                mode=rng.choice(["connect", "bus"]),
            )

        else:
            wt = rng.choice(templates)

        gt: List[ComponentGT] = []
        comp_counter: Dict[str, int] = {}
        tikz_lines: List[str] = []

        # 1) For each graph edge: split -> fill segments with random components
        for ei, (u, v) in enumerate(wt.edges):
            a = wt.nodes[u]
            b = wt.nodes[v]
            pts_edge = self._edge_waypoints(a, b, self.density)

            tikz_lines.append(
                self._draw_edge_with_random_components(
                    edge_name=f"{wt.name}:{u}_{v}_{ei}",
                    pts=pts_edge,
                    gt=gt,
                    comp_counter=comp_counter,
                )
            )

        # 2) Explicit junction dots
        for jname in wt.junctions:
            if jname not in wt.nodes:
                continue
            p = wt.nodes[jname]
            tikz_lines.append(rf"\draw {fmt_pt(p)} node[circ]{{}};")
            gt.append(
                ComponentGT(
                    name=f"junction_{jname}",
                    ctype="junction",
                    kind="node",
                    at=p,
                    extra={"style": "circ", "node": jname, "template": wt.name},
                )
            )

        # 3) Crossing segments (wire jump)
        for ci, (a, b) in enumerate(wt.crossings):
            tikz_lines.append(rf"\draw {fmt_pt(a)} to[crossing] {fmt_pt(b)};")
            gt.append(
                ComponentGT(
                    name=f"crossing_{ci}",
                    ctype="crossing",
                    kind="to",
                    start=a,
                    end=b,
                    mid=midpoint(a, b),
                    extra={"style": "crossing", "template": wt.name},
                )
            )

        # 4) Optional extra branch/noise
        extra = self._optional_crossing_and_branch(gt)
        if extra.strip():
            tikz_lines.append(extra)

        # 5) Ensure both node + to appear if requested
        self._ensure_both_kinds(gt, comp_counter, tikz_lines)

        tikz_body = "\n".join(tikz_lines)
        # Build YOLO export commands from gt list
        yolo_exports = []
        for comp in gt:
            yolo_cls = map_ctype_to_yolo(comp.ctype)
            if not yolo_cls:
                continue
            cid = CLASS_ID[yolo_cls]
            bbox_name = f"{comp.name}BB"  # must match what we used in drawing
            yolo_exports.append(rf"\WriteYoloBBox{{{bbox_name}}}{{{cid}}}")

        # tex = self._latex_doc(tikz_body)
        labels_filename = "labels.txt"
        tex = self._latex_doc(tikz_body, labels_filename=labels_filename)
        tex = tex.replace("%__YOLO_EXPORTS__", "\n".join(yolo_exports))

        # Paths
        ensure_dir(self.out_dir)
        sample_dir = os.path.join(self.out_dir, f"{idx:06d}")
        ensure_dir(sample_dir)

        tex_path = os.path.join(sample_dir, "circuit.tex")
        pdf_path = os.path.join(sample_dir, "circuit.pdf")
        png_path = os.path.join(sample_dir, "circuit.png")
        # gt_path = os.path.join(sample_dir, "ground_truth.json")
        labels_path = os.path.join(sample_dir, "labels.txt")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex)

        # Compile
        produced_pdf = self._compile_tex_to_pdf(tex_path, workdir=sample_dir)
        if produced_pdf != pdf_path:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            os.replace(produced_pdf, pdf_path)

        # Convert
        self._pdf_to_png(pdf_path, png_path, dpi=300)

        # Save GT (graph + component geometry)
        # gt_payload = {
        #     "seed": self.seed,
        #     "index": idx,
        #     "template_name": wt.name,
        #     "canvas": {"W": self.W, "H": self.H},
        #     "graph": {
        #         "nodes": {k: {"x": v[0], "y": v[1]} for k, v in wt.nodes.items()},
        #         "edges": [{"u": u, "v": v} for (u, v) in wt.edges],
        #         "junctions": wt.junctions,
        #         "crossings": [
        #             {"a": {"x": a[0], "y": a[1]}, "b": {"x": b[0], "y": b[1]}}
        #             for (a, b) in wt.crossings
        #         ],
        #     },
        #     "components": [asdict(x) for x in gt],
        # }

        # with open(gt_path, "w", encoding="utf-8") as f:
        #     json.dump(gt_payload, f, indent=2, ensure_ascii=False)

    def generate(self) -> None:
        for i in range(self.n):
            self.generate_one(i)


# ----------------------------
# CLI entry
# ----------------------------
def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="out_circuits", help="output directory")
    ap.add_argument("--n", type=int, default=50, help="number of circuits")
    ap.add_argument("--seed", type=int, default=0, help="random seed")
    ap.add_argument("--W", type=float, default=4.0, help="template width")
    ap.add_argument("--H", type=float, default=3.0, help="template height")
    ap.add_argument(
        "--density",
        type=int,
        default=1,
        help="intermediate splits per edge (0/1/2/...)",
    )
    ap.add_argument(
        "--p_node",
        type=float,
        default=0.25,
        help="probability to insert a node component on a segment",
    )
    ap.add_argument(
        "--p_junction",
        type=float,
        default=0.35,
        help="probability of -* / *- / *-* markers on bipole segments",
    )
    ap.add_argument(
        "--p_crossing",
        type=float,
        default=0.40,
        help="probability to add internal crossing/junction branch augmentation",
    )
    ap.add_argument(
        "--node_bias",
        type=float,
        default=0.35,
        help="sampling bias to pick node components (0..1)",
    )
    ap.add_argument(
        "--force_both",
        action="store_true",
        help="force each circuit to contain both 'node' and 'to' components",
    )

    args = ap.parse_args()

    gen = CircuitGenerator(
        out_dir=args.out,
        seed=args.seed,
        n=args.n,
        W=args.W,
        H=args.H,
        density=args.density,
        p_node_component=args.p_node,
        p_junction=args.p_junction,
        p_crossing=args.p_crossing,
        node_bias=args.node_bias,
        force_both_kinds=args.force_both,
    )
    gen.generate()
    print(f"Done. Output in: {args.out}")


if __name__ == "__main__":
    main()
