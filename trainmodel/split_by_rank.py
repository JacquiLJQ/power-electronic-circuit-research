import os
import shutil
import pandas as pd
import math

# ========= 配置 =========
CSV_PATH = "per_image_rank.csv"
IMAGE_DIR = r"testset11cls/images/valid"  # 原图片目录
OUTPUT_DIR = "ranked_images"  # 输出总目录
IMAGE_COLUMN = "image"  # CSV里图片列名
# ========================

# 读取 CSV（你已经按降序排好）
df = pd.read_csv(CSV_PATH)

total = len(df)
one_third = total // 3

print(f"Total images: {total}")
print(f"Each group size (approx): {one_third}")

# 分组
good_df = df.iloc[:one_third]
ok_df = df.iloc[one_third : 2 * one_third]
bad_df = df.iloc[2 * one_third :]

# 创建文件夹
good_dir = os.path.join(OUTPUT_DIR, "good")
ok_dir = os.path.join(OUTPUT_DIR, "ok")
bad_dir = os.path.join(OUTPUT_DIR, "bad")

os.makedirs(good_dir, exist_ok=True)
os.makedirs(ok_dir, exist_ok=True)
os.makedirs(bad_dir, exist_ok=True)


def copy_images(sub_df, target_dir):
    for img_name in sub_df[IMAGE_COLUMN]:
        src = os.path.join(IMAGE_DIR, img_name)
        dst = os.path.join(target_dir, img_name)

        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            print(f"Warning: {img_name} not found!")


# 开始复制
copy_images(good_df, good_dir)
copy_images(ok_df, ok_dir)
copy_images(bad_df, bad_dir)

print("Done.")
print(f"Good: {len(good_df)}")
print(f"OK: {len(ok_df)}")
print(f"Bad: {len(bad_df)}")
