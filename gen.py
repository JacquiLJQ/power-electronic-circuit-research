import os, json, random, subprocess
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict

OUT_DIR = "out"
LATEX_ENGINE = "pdflatex"
DPI = 220
SEED = 20260128
random.seed(SEED)

Pt = Tuple[float, float]


@dataclass
class ComponentGT:
    cid: str
    ctype: str
    p1: Pt
    p2: Pt
    orientation: str
    attrs: Dict


@dataclass
class MarkerGT:
    mid: str
    mtype: str  # "junction" | "wire_jump"
    center: Pt
    attrs: Dict


# ---------------- LaTeX helpers ----------------
def compile_tex_to_pdf(tex_path: str, workdir: str) -> str:
    base = os.path.splitext(os.path.basename(tex_path))[0]
    pdf_out = os.path.join(workdir, base + ".pdf")
    p = subprocess.run(
        [LATEX_ENGINE, "-interaction=nonstopmode", os.path.basename(tex_path)],
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if not os.path.exists(pdf_out):
        print("pdflatex failed.\nSTDOUT:\n", p.stdout, "\nSTDERR:\n", p.stderr)
        raise RuntimeError("pdflatex did not produce PDF")
    return pdf_out


def pdf_to_png(pdf_path: str, out_png_path: str, workdir: str, dpi: int = 220) -> str:
    prefix = os.path.splitext(out_png_path)[0]
    p = subprocess.run(
        [
            "pdftoppm",
            "-r",
            str(dpi),
            "-png",
            os.path.basename(pdf_path),
            os.path.basename(prefix),
        ],
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    generated = prefix + "-1.png"
    if not os.path.exists(generated):
        raise RuntimeError(
            "pdftoppm did not produce png. Is poppler installed and in PATH?"
        )
    os.replace(generated, out_png_path)
    return out_png_path


def tex_preamble(style: str) -> str:
    return rf"""
\documentclass[tikz,border=2pt]{{standalone}}
\usepackage[american]{{circuitikz}}
\begin{{document}}
\begin{{circuitikz}}[{style}]
"""


def tex_end() -> str:
    return r"""
\end{circuitikz}
\end{document}
"""


def tikz_junction(x: float, y: float, r_pt: float = 1.7) -> str:
    return rf"\fill[black] ({x},{y}) circle ({r_pt}pt);"


def tikz_wire_jump(
    cx: float, cy: float, halfgap: float = 0.30, hump_h: float = 0.30
) -> str:
    x1 = cx - halfgap
    x2 = cx + halfgap
    return rf"\draw ({x1},{cy}) .. controls ({x1},{cy + hump_h}) and ({x2},{cy + hump_h}) .. ({x2},{cy});"


# ---------------- geometry helpers ----------------
def rect_from_points(pts: List[Pt], pad: float) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def rects_overlap(a, b, pad: float = 0.0) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (
        ax2 + pad < bx1 or bx2 + pad < ax1 or ay2 + pad < by1 or by2 + pad < ay1
    )


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ---------------- spec ----------------
def component_specs():
    # 11 required. real switch 暂时也画成 switch
    return [
        ("AC1", "ACSource", "sV", "AC"),
        ("BAT1", "Battery", "battery", "BAT"),
        ("C1", "Capacitor", "C", "C1"),
        ("D1", "Diode", "D", "D1"),
        ("V1", "VoltageSource", "V", "V1"),
        ("L1", "Inductor", "L", "L1"),
        ("I1", "CurrentSource", "I", "I1"),
        ("SW_ID", "IdealSwitch", "switch", "SW"),
        ("SW_R", "RealSwitch", "switch", "SWr"),
        ("T1", "Transformer", "transformer", "T1"),  # node[transformer]
        ("R1", "Resistor", "R", "R1"),
    ]


# ---------------- scene generator ----------------
def generate_scene_with_leads():
    comps: List[ComponentGT] = []
    markers: List[MarkerGT] = []
    cmds: List[str] = []

    # fixed canvas (view bbox). Everything we place must stay inside this.
    view_bbox = (-10.0, -8.0, 10.0, 8.0)
    vx1, vy1, vx2, vy2 = view_bbox

    line_w = random.choice([0.8, 1.0, 1.2])
    style = rf"line width={line_w}pt"

    # placement margins inside view bbox
    margin = 1.2

    # component sizing
    comp_len_choices = [1.6, 1.8, 2.0, 2.2]
    lead_len_choices = [0.8, 1.0, 1.2]
    # bbox padding for non-overlap
    pad = 0.85

    occupied: List[Tuple[float, float, float, float]] = []

    def place_two_pin(cid, ctype, element, label):
        # try many times to find a non-overlapping placement fully inside view bbox
        for _ in range(4000):
            ori = random.choice(["h", "v"])
            L = random.choice(comp_len_choices)
            lead = random.choice(lead_len_choices)

            # choose center such that endpoints + leads still inside
            if ori == "h":
                # endpoints x = cx ± L/2, leads extend further ±lead
                cx = random.uniform(
                    vx1 + margin + (L / 2 + lead), vx2 - margin - (L / 2 + lead)
                )
                cy = random.uniform(vy1 + margin, vy2 - margin)
                p1 = (cx - L / 2, cy)
                p2 = (cx + L / 2, cy)
                # lead endpoints
                w1 = (p1[0] - lead, cy)
                w2 = (p2[0] + lead, cy)
            else:
                cx = random.uniform(vx1 + margin, vx2 - margin)
                cy = random.uniform(
                    vy1 + margin + (L / 2 + lead), vy2 - margin - (L / 2 + lead)
                )
                p1 = (cx, cy - L / 2)
                p2 = (cx, cy + L / 2)
                w1 = (cx, p1[1] - lead)
                w2 = (cx, p2[1] + lead)

            # bbox include component + leads so leads also don't overlap too much
            bb = rect_from_points([p1, p2, w1, w2], pad=pad)
            if any(rects_overlap(bb, old, pad=0.15) for old in occupied):
                continue

            occupied.append(bb)

            # draw component
            cmds.append(
                rf"\draw ({p1[0]},{p1[1]}) to[{element},l_={label}] ({p2[0]},{p2[1]});"
            )
            # draw leads (stubs)
            cmds.append(rf"\draw ({w1[0]},{w1[1]}) -- ({p1[0]},{p1[1]});")
            cmds.append(rf"\draw ({p2[0]},{p2[1]}) -- ({w2[0]},{w2[1]});")

            comps.append(
                ComponentGT(
                    cid,
                    ctype,
                    p1,
                    p2,
                    ori,
                    {
                        "label": label,
                        "element": element,
                        "lead_len": lead,
                        "lead_end_1": w1,
                        "lead_end_2": w2,
                    },
                )
            )
            return

        raise RuntimeError(
            f"Could not place {cid} without overlap. Consider enlarging view_bbox or reducing pad."
        )

    def place_transformer_node():
        # transformer footprint (rough)
        for _ in range(4000):
            x = random.uniform(vx1 + margin + 2.0, vx2 - margin - 2.0)
            y = random.uniform(vy1 + margin + 2.0, vy2 - margin - 2.0)
            # include some space + little leads around
            bb = (x - 2.2, y - 2.2, x + 2.2, y + 2.2)
            if any(rects_overlap(bb, old, pad=0.15) for old in occupied):
                continue
            occupied.append(bb)

            cmds.append(rf"\draw ({x},{y}) node[transformer] (T1) {{}};")

            # add 4 short leads from its anchors (not connecting to others)
            lead = random.choice([0.9, 1.1, 1.3])
            cmds.append(rf"\draw (T1.A1) -- ++(-{lead},0);")
            cmds.append(rf"\draw (T1.A2) -- ++(-{lead},0);")
            cmds.append(rf"\draw (T1.B1) -- ++({lead},0);")
            cmds.append(rf"\draw (T1.B2) -- ++({lead},0);")

            comps.append(
                ComponentGT(
                    "T1",
                    "Transformer",
                    (x - 1.6, y + 1.9),
                    (x + 1.6, y - 1.9),
                    "na",
                    {"label": "T1", "lead_len": lead},
                )
            )
            return

        raise RuntimeError("Could not place transformer without overlap.")

    # 1) place transformer first (harder footprint)
    place_transformer_node()

    # 2) place remaining 10 bipoles with leads
    for cid, ctype, element, label in component_specs():
        if cid == "T1":
            continue
        place_two_pin(cid, ctype, element, label)

    # 3) force junction (>=3 wires + dot), also keep inside and avoid overlap
    # 3) force junction (>=3 wires + dot) — DO NOT enforce non-overlap
    jx = random.uniform(vx1 + margin + 2.5, vx2 - margin - 2.5)
    jy = random.uniform(vy1 + margin + 2.5, vy2 - margin - 2.5)

    cmds.append(rf"\draw ({jx-2.0},{jy}) -- ({jx},{jy});")
    cmds.append(rf"\draw ({jx},{jy}) -- ({jx+2.0},{jy});")
    cmds.append(rf"\draw ({jx},{jy}) -- ({jx},{jy+2.0});")
    cmds.append(tikz_junction(jx, jy))

    markers.append(MarkerGT("JUNC1", "junction", (jx, jy), {"min_degree": 3}))

    # 4) force wire jump (vertical continuous + horizontal hump), keep inside and avoid overlap
    # 4) force wire jump — overlap is allowed
    cx = random.uniform(vx1 + margin + 3.0, vx2 - margin - 3.0)
    cy = random.uniform(vy1 + margin + 3.0, vy2 - margin - 3.0)

    gap = 0.30
    cmds.append(rf"\draw ({cx},{cy-2.2}) -- ({cx},{cy+2.2});")
    cmds.append(rf"\draw ({cx-2.4},{cy}) -- ({cx-gap},{cy});")
    cmds.append(tikz_wire_jump(cx, cy, halfgap=gap, hump_h=0.30))
    cmds.append(rf"\draw ({cx+gap},{cy}) -- ({cx+2.4},{cy});")

    markers.append(
        MarkerGT("JUMP1", "wire_jump", (cx, cy), {"gap": gap, "hump_h": 0.30})
    )

    # assemble tex body
    lines: List[str] = []
    lines.append(rf"\path[use as bounding box] ({vx1},{vy1}) rectangle ({vx2},{vy2});")
    # no extra centering needed because we place inside bbox directly
    lines.extend(cmds)
    body = "\n".join(lines)
    return style, body, comps, markers


def generate_one(idx: int):
    os.makedirs(OUT_DIR, exist_ok=True)

    # retry whole scene if rare placement failure
    last_err = None
    for _ in range(80):
        try:
            style, body, comps, markers = generate_scene_with_leads()
            break
        except RuntimeError as e:
            last_err = e
    else:
        raise last_err

    tex = tex_preamble(style) + body + tex_end()

    base = f"sample_{idx:05d}"
    tex_path = os.path.join(OUT_DIR, base + ".tex")
    pdf_path = os.path.join(OUT_DIR, base + ".pdf")
    png_path = os.path.join(OUT_DIR, base + ".png")
    json_path = os.path.join(OUT_DIR, base + ".json")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)

    pdf = compile_tex_to_pdf(tex_path, workdir=OUT_DIR)
    pdf_to_png(pdf, png_path, workdir=OUT_DIR, dpi=DPI)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "image": os.path.basename(png_path),
                "tex": os.path.basename(tex_path),
                "pdf": os.path.basename(pdf_path),
                "components": [asdict(c) for c in comps],
                "markers": [asdict(m) for m in markers],
                "meta": {
                    "seed": SEED,
                    "dpi": DPI,
                    "mode": "scatter_components_with_leads_no_skeleton",
                    "guaranteed_components": True,
                    "guaranteed_junction": True,
                    "guaranteed_wire_jump": True,
                },
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(
        "[OK]",
        os.path.basename(png_path),
        "components=",
        len(comps),
        "markers=",
        len(markers),
    )


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()
    for i in range(args.n):
        generate_one(i)


if __name__ == "__main__":
    main()
