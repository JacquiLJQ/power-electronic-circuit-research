import os
import shutil
import pandas as pd
import cv2
from ultralytics import YOLO

# ========= 配置 =========
WEIGHTS = r"best.pt"
CSV_PATH = "generate_data/per_image_rank.csv"

IMAGE_DIR = r"datasets/testset11cls/images/valid"
OUT_COPY_DIR = "ranked_images"  # 可选：分类拷贝原图
OUT_VIS_DIR = "ranked_images_vis"  # 预测框可视化输出

IMAGE_COLUMN = "image"
CONF_THRES = 0.25

# 是否也拷贝原图到 ranked_images/
COPY_ORIGINALS = False
# ========================


def ensure_dirs(base):
    for split in ["good", "ok", "bad"]:
        os.makedirs(os.path.join(base, split), exist_ok=True)


def draw_preds(img_bgr, preds, names):
    """
    preds: [(cls, conf, [x1,y1,x2,y2]), ...]
    """
    h, w = img_bgr.shape[:2]

    def clip(x1, y1, x2, y2):
        x1 = int(max(0, min(w - 1, x1)))
        y1 = int(max(0, min(h - 1, y1)))
        x2 = int(max(0, min(w - 1, x2)))
        y2 = int(max(0, min(h - 1, y2)))
        return x1, y1, x2, y2

    for cls, conf, (x1, y1, x2, y2) in preds:
        x1, y1, x2, y2 = clip(x1, y1, x2, y2)
        # 红色预测框
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 0, 255), 2)
        label = f"{names.get(cls, str(cls))} {conf:.2f}"
        cv2.putText(
            img_bgr,
            label,
            (x1, max(0, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
    return img_bgr


def main():
    df = pd.read_csv(CSV_PATH)
    total = len(df)
    one_third = total // 3

    good_df = df.iloc[:one_third]
    ok_df = df.iloc[one_third : 2 * one_third]
    bad_df = df.iloc[2 * one_third :]

    ensure_dirs(OUT_VIS_DIR)
    if COPY_ORIGINALS:
        ensure_dirs(OUT_COPY_DIR)

    model = YOLO(WEIGHTS)
    names = model.names if hasattr(model, "names") else {}

    def process_group(sub_df, split):
        for img_name in sub_df[IMAGE_COLUMN]:
            src_img_path = os.path.join(IMAGE_DIR, img_name)
            if not os.path.exists(src_img_path):
                print(f"[WARN] missing image: {img_name}")
                continue

            # 可选：拷贝原图
            if COPY_ORIGINALS:
                shutil.copy2(src_img_path, os.path.join(OUT_COPY_DIR, split, img_name))

            img = cv2.imread(src_img_path)
            if img is None:
                print(f"[WARN] cannot read: {img_name}")
                continue

            r = model.predict(src_img_path, conf=CONF_THRES, verbose=False)[0]

            preds = []
            if r.boxes is not None and len(r.boxes) > 0:
                boxes_xyxy = r.boxes.xyxy.cpu().numpy()
                confs = r.boxes.conf.cpu().numpy()
                clss = r.boxes.cls.cpu().numpy().astype(int)
                for cls, conf, xyxy in zip(clss, confs, boxes_xyxy):
                    preds.append((int(cls), float(conf), xyxy.tolist()))

            vis = draw_preds(img, preds, names)

            stem = os.path.splitext(img_name)[0]
            out_name = stem + ".png"
            dst_vis_path = os.path.join(OUT_VIS_DIR, split, out_name)
            cv2.imwrite(dst_vis_path, vis)

    process_group(good_df, "good")
    process_group(ok_df, "ok")
    process_group(bad_df, "bad")

    print("Done.")
    print(f"Visualized images -> {OUT_VIS_DIR}")
    if COPY_ORIGINALS:
        print(f"Copied images -> {OUT_COPY_DIR}")


if __name__ == "__main__":
    main()
