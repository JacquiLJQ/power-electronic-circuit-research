"""
build_yolo_dataset.py
- Run gen.py (optional)
- Cleanup each sample folder: keep only circuit.png + labels.txt
- Build YOLO dataset with train/val/test = 80/10/10 (or configurable)
- Write data.yaml (optional)

Expected gen output:
out_circuits/
  000000/
    circuit.png
    labels.txt
    ... (other junk)
  000001/
    ...
"""

import argparse
import random
import shutil
import subprocess
from pathlib import Path

KEEP_FILES = {"circuit.png", "labels.txt"}


def run_gen(gen_py: str, gen_args: list[str]) -> None:
    """Run: python gen.py ..."""
    cmd = ["python", gen_py] + gen_args
    print("[RUN]", " ".join(cmd))
    subprocess.run(cmd, check=True)


def cleanup_samples(out_dir: Path) -> tuple[int, int]:
    """
    For each sample folder under out_dir, keep only circuit.png and labels.txt.
    Returns (removed_count, kept_count).
    """
    removed = 0
    kept = 0

    for d in out_dir.iterdir():
        if not d.is_dir():
            continue
        for f in d.iterdir():
            if f.name in KEEP_FILES:
                kept += 1
                continue
            try:
                if f.is_file():
                    f.unlink()
                else:
                    shutil.rmtree(f)
                removed += 1
            except Exception:
                pass

    print(f"[CLEANUP] kept={kept}, removed={removed}")
    return removed, kept


def find_samples(out_dir: Path) -> list[Path]:
    """Sample dirs: those that contain circuit.png and labels.txt"""
    samples = []
    for d in sorted(out_dir.iterdir()):
        if not d.is_dir():
            continue
        if (d / "circuit.png").exists() and (d / "labels.txt").exists():
            samples.append(d)
    return samples


def copy_to_yolo_structure(
    samples: list[Path],
    yolo_root: Path,
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> None:
    """
    Create:
      yolo_root/
        images/train, images/val, images/test
        labels/train, labels/val, labels/test

    Splits by SHUFFLED indices using seed (reproducible).
    """
    if val_ratio < 0 or test_ratio < 0 or (val_ratio + test_ratio) >= 1.0:
        raise ValueError(
            "val_ratio and test_ratio must be >=0 and val_ratio+test_ratio < 1.0"
        )

    rng = random.Random(seed)
    idxs = list(range(len(samples)))
    rng.shuffle(idxs)

    n_total = len(samples)
    n_test = int(round(n_total * test_ratio))
    n_val = int(round(n_total * val_ratio))

    # Ensure train is at least 1 if possible
    if n_total >= 3 and (n_total - n_val - n_test) <= 0:
        # back off ratios minimally
        n_test = min(n_test, max(0, n_total - 2))
        n_val = min(n_val, max(0, n_total - n_test - 1))

    test_set = set(idxs[:n_test])
    val_set = set(idxs[n_test : n_test + n_val])

    img_train = yolo_root / "images" / "train"
    img_val = yolo_root / "images" / "val"
    img_test = yolo_root / "images" / "test"
    lab_train = yolo_root / "labels" / "train"
    lab_val = yolo_root / "labels" / "val"
    lab_test = yolo_root / "labels" / "test"

    for p in [img_train, img_val, img_test, lab_train, lab_val, lab_test]:
        p.mkdir(parents=True, exist_ok=True)

    for i, sidx in enumerate(idxs):
        sd = samples[sidx]
        if sidx in test_set:
            split = "test"
        elif sidx in val_set:
            split = "val"
        else:
            split = "train"

        # use original folder name if it's numeric, else fallback to a running index
        stem = sd.name if sd.name.isdigit() else f"{i:06d}"

        src_img = sd / "circuit.png"
        src_lab = sd / "labels.txt"

        if split == "train":
            dst_img = img_train / f"{stem}.png"
            dst_lab = lab_train / f"{stem}.txt"
        elif split == "val":
            dst_img = img_val / f"{stem}.png"
            dst_lab = lab_val / f"{stem}.txt"
        else:
            dst_img = img_test / f"{stem}.png"
            dst_lab = lab_test / f"{stem}.txt"

        shutil.copy2(src_img, dst_img)
        shutil.copy2(src_lab, dst_lab)

    n_train = n_total - n_val - n_test
    print(f"[YOLO] wrote dataset to: {yolo_root.resolve()}")
    print(f"[YOLO] train={n_train}, val={n_val}, test={n_test} (total={n_total})")


def merge_existing_yolo(
    src_yolo: Path,
    dst_yolo: Path,
    seed: int = 0,
):
    """
    Merge an existing YOLO dataset (images/labels with train/val/test)
    into dst_yolo, renaming files to avoid collision.
    """
    rng = random.Random(seed)

    for split in ["train", "val", "test"]:
        src_img = src_yolo / "images" / split
        src_lab = src_yolo / "labels" / split
        if not src_img.exists():
            continue

        dst_img = dst_yolo / "images" / split
        dst_lab = dst_yolo / "labels" / split
        dst_img.mkdir(parents=True, exist_ok=True)
        dst_lab.mkdir(parents=True, exist_ok=True)

        imgs = sorted(src_img.glob("*.png")) + sorted(src_img.glob("*.jpg"))

        for p in imgs:
            stem = p.stem
            lbl = src_lab / f"{stem}.txt"
            if not lbl.exists():
                continue

            # add random prefix to avoid name collision
            new_stem = f"mix_{rng.randint(0,999999):06d}_{stem}"

            shutil.copy2(p, dst_img / f"{new_stem}{p.suffix}")
            shutil.copy2(lbl, dst_lab / f"{new_stem}.txt")

    print(f"[MERGE] merged existing YOLO dataset from {src_yolo}")


def write_data_yaml(
    yolo_root: Path,
    class_names: list[str] | None,
    include_test: bool = True,
) -> None:
    """
    Optional: write data.yaml for Ultralytics YOLO.
    """
    if not class_names:
        return

    yaml_path = yolo_root / "data.yaml"
    content = [
        f'path: "{yolo_root.resolve().as_posix()}"',
        "train: images/train",
        "val: images/val",
    ]
    if include_test:
        content.append("test: images/test")

    content += [
        f"nc: {len(class_names)}",
        "names:",
    ]
    for i, n in enumerate(class_names):
        content.append(f"  {i}: {n}")

    yaml_path.write_text("\n".join(content) + "\n", encoding="utf-8")
    print(f"[YOLO] wrote: {yaml_path.resolve()}")


def main():
    ap = argparse.ArgumentParser(
        description="Run gen.py -> cleanup -> build YOLO folder structure (train/val/test)"
    )

    # --- generator control ---
    ap.add_argument("--gen_py", type=str, default="gen.py", help="path to gen.py")
    ap.add_argument("--out", type=str, default="out_circuits", help="gen output dir")

    # These are forwarded to gen.py (defaults match your command)
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--seed", type=int, default=156489)
    ap.add_argument("--W", type=float, default=30)
    ap.add_argument("--H", type=float, default=30)
    ap.add_argument("--density", type=int, default=1)
    ap.add_argument("--p_node", type=float, default=0.1)
    ap.add_argument("--p_junction", type=float, default=0.1)
    ap.add_argument("--p_crossing", type=float, default=0.1)
    ap.add_argument("--node_bias", type=float, default=0.3)

    # --- dataset build ---
    ap.add_argument(
        "--yolo_out",
        type=str,
        default="yolo_dataset",
        help="output YOLO dataset root",
    )
    ap.add_argument("--val_ratio", type=float, default=0, help="e.g. 0.10")
    ap.add_argument("--test_ratio", type=float, default=0, help="e.g. 0.10")
    ap.add_argument(
        "--no_run_gen",
        action="store_true",
        help="skip running gen.py (only cleanup + build yolo from existing out dir)",
    )
    ap.add_argument(
        "--no_cleanup",
        action="store_true",
        help="skip cleanup step",
    )
    ap.add_argument(
        "--write_yaml",
        action="store_true",
        help="also write data.yaml (requires --names)",
    )
    ap.add_argument(
        "--names",
        type=str,
        default="",
        help='comma-separated class names (e.g. "battery,cap,curr_src,diode,inductor,resistor,swi_ideal,swi_real,volt_src,xformer")',
    )
    ap.add_argument(
        "--merge_yolo",
        type=str,
        default="",
        help="Path to an existing YOLO dataset to merge (e.g. component_dataset)",
    )

    args = ap.parse_args()

    out_dir = Path(args.out)
    yolo_root = Path(args.yolo_out)

    # 1) run generator
    if not args.no_run_gen:
        gen_args = [
            "--out",
            args.out,
            "--n",
            str(args.n),
            "--seed",
            str(args.seed),
            "--W",
            str(args.W),
            "--H",
            str(args.H),
            "--density",
            str(args.density),
            "--p_node",
            str(args.p_node),
            "--p_junction",
            str(args.p_junction),
            "--p_crossing",
            str(args.p_crossing),
            "--node_bias",
            str(args.node_bias),
        ]
        run_gen(args.gen_py, gen_args)

    # 2) cleanup
    if not args.no_cleanup:
        cleanup_samples(out_dir)

    # 3) gather samples
    samples = find_samples(out_dir)
    if not samples:
        raise RuntimeError(
            f"No valid samples found in {out_dir}. Expected each sample dir to contain circuit.png and labels.txt"
        )
    print(f"[FOUND] samples={len(samples)}")

    # 4) build YOLO structure
    if yolo_root.exists():
        shutil.rmtree(yolo_root)
    copy_to_yolo_structure(
        samples=samples,
        yolo_root=yolo_root,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    # 4.5) merge existing YOLO dataset (e.g. component-based gen)
    if args.merge_yolo:
        merge_existing_yolo(
            src_yolo=Path(args.merge_yolo),
            dst_yolo=yolo_root,
            seed=args.seed,
        )

    # 5) optional data.yaml
    class_names = (
        [s.strip() for s in args.names.split(",") if s.strip()] if args.names else []
    )
    if args.write_yaml:
        if not class_names:
            raise RuntimeError("--write_yaml requires --names")
        write_data_yaml(yolo_root, class_names, include_test=True)


if __name__ == "__main__":
    main()
