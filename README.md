

## gen.py usage

```bash
python gen.py --out out_circuits --n 20 --seed 56 --W 35 --H 30 --density 1 --p_node 0.1 --p_junction 0.1 --p_crossing 0.1 --node_bias 0.3
```
## wire_component_connections.py usage

```bash
python wire_component_connections.py --image path/to/image.jpg --json path/to/json.json
```
yolo train model=yolo11n.pt data=synthetic_schemdraw__dataset_no_wire/data.yaml imgsz=640 epochs=100 batch=16 device=0 project="v2" name="1.1"
 workers=2 hsv_v=0 hsv_s=0 hsv_h=0  