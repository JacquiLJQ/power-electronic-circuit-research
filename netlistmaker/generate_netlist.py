import json
from netlistbuilder import NetList

# 读 incidence matrix json
with open("./pngfile/pwm/pwm/35.json", "r") as f:
    data = json.load(f)

# 第一列是 dev_matrix，其余是 con_matrix
dev_matrix = [row[0] for row in data]
con_matrix = [[int(float(x)) for x in row[1:]] for row in data]


# 创建 NetList
nl = NetList("test_35")

# 没 MOSFET 的话，param 给空
# 给很多组，反正用不完也没事
param = [["0", "3u", "10u"]] * 50

# 生成 netlist
nl.generate(con_matrix, dev_matrix, param, time="100u")

print("Netlist generated: test_35.net")
