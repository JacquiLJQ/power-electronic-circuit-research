import os
import glob
import csv
from dataclasses import dataclass
from typing import List, Tuple, Dict
import numpy as np
from ultralytics import YOLO

# ---------------------------
# 配置区：按你的路径改这几个
# ---------------------------
WEIGHTS = r"models/best_mixed_train-2500+2500.pt"
VAL_IMAGES_DIR = r"testset11cls/images/valid"
VAL_LABELS_DIR = r"testset11cls/labels/valid"
OUT_CSV = "per_image_rank.csv"

CONF_THRES = 0.25  # 预测置信度阈值
IOU_THRES = 0.50  # 匹配阈值（常用0.5，也可以0.75更严格）
IMG_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


# ---------------------------
# 工具函数
# ---------------------------
def yolo_norm_to_xyxy(box, w, h):
    # box: [cx, cy, bw, bh] (normalized)
    cx, cy, bw, bh = box
    x1 = (cx - bw / 2.0) * w
    y1 = (cy - bh / 2.0) * h
    x2 = (cx + bw / 2.0) * w
    y2 = (cy + bh / 2.0) * h
    return np.array([x1, y1, x2, y2], dtype=np.float32)


def compute_iou(a, b):
    # a,b: [x1,y1,x2,y2]
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    inter = inter_w * inter_h
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter + 1e-9
    return inter / union


def load_gt(label_path, img_w, img_h):
    gts = []
    if not os.path.exists(label_path):
        return gts
    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            cls = int(float(parts[0]))
            cx, cy, bw, bh = map(float, parts[1:])
            xyxy = yolo_norm_to_xyxy([cx, cy, bw, bh], img_w, img_h)
            gts.append((cls, xyxy))
    return gts


def greedy_match(preds, gts, iou_thres=0.5):
    """
    preds: list of (cls, conf, xyxy)
    gts:   list of (cls, xyxy)
    返回: matches [(pi, gi, iou)], unmatched_pred_idxs, unmatched_gt_idxs
    """
    matches = []
    used_g = set()

    # 预测按置信度从高到低匹配（更符合常见评估习惯）
    pred_order = sorted(range(len(preds)), key=lambda i: preds[i][1], reverse=True)

    for pi in pred_order:
        p_cls, p_conf, p_box = preds[pi]
        best = (-1, 0.0)  # (gi, iou)
        for gi, (g_cls, g_box) in enumerate(gts):
            if gi in used_g:
                continue
            if g_cls != p_cls:
                continue
            iou = compute_iou(p_box, g_box)
            if iou >= iou_thres and iou > best[1]:
                best = (gi, iou)
        if best[0] != -1:
            used_g.add(best[0])
            matches.append((pi, best[0], best[1]))

    unmatched_p = [i for i in range(len(preds)) if i not in {m[0] for m in matches}]
    unmatched_g = [i for i in range(len(gts)) if i not in {m[1] for m in matches}]
    return matches, unmatched_p, unmatched_g


# ---------------------------
# 主流程
# ---------------------------
def main():
    model = YOLO(WEIGHTS)

    image_paths = []
    for ext in IMG_EXTS:
        image_paths.extend(glob.glob(os.path.join(VAL_IMAGES_DIR, f"*{ext}")))
    image_paths = sorted(image_paths)

    rows = []
    for img_path in image_paths:
        # 读图尺寸：用 ultralytics 的结果里拿原图尺寸最省事
        r = model.predict(img_path, conf=CONF_THRES, verbose=False)[0]
        img_h, img_w = r.orig_shape  # (h, w)

        # 预测框
        preds = []
        if r.boxes is not None and len(r.boxes) > 0:
            boxes_xyxy = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            clss = r.boxes.cls.cpu().numpy().astype(int)
            for cls, conf, xyxy in zip(clss, confs, boxes_xyxy):
                preds.append((int(cls), float(conf), xyxy.astype(np.float32)))

        # GT 标签
        stem = os.path.splitext(os.path.basename(img_path))[0]
        label_path = os.path.join(VAL_LABELS_DIR, stem + ".txt")
        gts = load_gt(label_path, img_w, img_h)

        # 匹配 + per-image 指标
        matches, unmatched_p, unmatched_g = greedy_match(preds, gts, IOU_THRES)
        tp = len(matches)
        fp = len(unmatched_p)
        fn = len(unmatched_g)

        precision = tp / (tp + fp + 1e-9)
        recall = tp / (tp + fn + 1e-9)
        f1 = 2 * precision * recall / (precision + recall + 1e-9)
        mean_iou = float(np.mean([m[2] for m in matches])) if tp > 0 else 0.0

        rows.append(
            {
                "image": os.path.basename(img_path),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "mean_iou": mean_iou,
                "num_preds": len(preds),
                "num_gts": len(gts),
            }
        )

    # 排序：你可以改成按 mean_iou 或 recall 排
    rows_sorted = sorted(rows, key=lambda x: (x["f1"], x["mean_iou"]), reverse=True)

    # 写 CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows_sorted[0].keys()) if rows_sorted else []
        )
        writer.writeheader()
        writer.writerows(rows_sorted)

    print(f"[DONE] wrote ranking to: {OUT_CSV}")
    if rows_sorted:
        print("\nTop 5 (best):")
        for r in rows_sorted[:5]:
            print(
                r["image"],
                "F1=",
                round(r["f1"], 3),
                "mIoU=",
                round(r["mean_iou"], 3),
                "P=",
                round(r["precision"], 3),
                "R=",
                round(r["recall"], 3),
                "TP/FP/FN=",
                (r["tp"], r["fp"], r["fn"]),
            )
        print("\nBottom 5 (worst):")
        for r in rows_sorted[-5:]:
            print(
                r["image"],
                "F1=",
                round(r["f1"], 3),
                "mIoU=",
                round(r["mean_iou"], 3),
                "P=",
                round(r["precision"], 3),
                "R=",
                round(r["recall"], 3),
                "TP/FP/FN=",
                (r["tp"], r["fp"], r["fn"]),
            )


if __name__ == "__main__":
    main()
