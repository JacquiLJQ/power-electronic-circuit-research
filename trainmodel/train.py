from ultralytics import YOLO

yolo = YOLO("yolo11m.pt")
results = yolo.train(
    data="./data.yml",
    epochs=500,
    patience=0,
    translate=0.0,
    scale=0.0,
    flipud=0.0,
    fliplr=0.0,
    erasing=0.0,
    hsv_h=0.0,
    hsv_s=0.0,
    hsv_v=0.0,
    degrees=0.0,
    mosaic=0.0,
    auto_augment="",
)

# yolo train model=yolo11n.pt data=datasets/component_dataset_new_remove_no_wire/data.yaml imgsz=640 epochs=100 batch=4 device=0 project="shiyanzu" name="a2b4" workers=3 hsv_v=0 hsv_s=0 hsv_h=0 patience=0 translate=0.0 scale=0.0 flipud=0.0 fliplr=0.0 erasing=0.0 degrees=0.0 mosaic=0.0 auto_augment=None
# yolo detect val model="best.pt" data="datasets\testset11cls\data.yaml" imgsz=640 project="shiyanzu" name="a2b4test"
