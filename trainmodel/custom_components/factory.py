from schemdraw.elements import Element

import schemdraw

from resistor import ResistorCustom
from ac_src import ACSourceCustom
from battery import BatteryCustom
from cap import CapacitorCustom
from curr_src import CurrentSourceCustom
from diode import DiodeCustom
from inductor import InductorCustom
from swi_real import NMosCustom
from swi_ideal import SwitchIdealCustom
from xformer import TransformerCustom
from volt_src import VoltageSourceCustom

import inspect
from schemdraw.segments import Segment, SegmentArc, SegmentBezier, SegmentCircle


from typing import Sequence
import random


def make_rng(seed: int | None = None) -> random.Random:
    return random.Random(seed)


def _sample_turns(rng: random.Random, lo=2, hi=7, p_multi=0.25) -> int | Sequence[int]:
    """Return int or list[int]. Keep list short to avoid crazy height."""
    if rng.random() < p_multi:
        groups = rng.choice([2, 3])  # 2-3 groups max
        return [rng.randint(lo, hi) for _ in range(groups)]
    return rng.randint(lo, hi)


def _sum_turns(t: int | Sequence[int]) -> int:
    return sum(t) if isinstance(t, (list, tuple)) else int(t)


# transformer


def sample_transformer_params(rng: random.Random) -> dict:
    loop = rng.random() < 0.5
    core = rng.random() >= 0.5

    t1 = _sample_turns(rng)
    t2 = _sample_turns(rng)

    # 基于绕组规模决定 spacing 的合理范围
    scale = max(_sum_turns(t1), _sum_turns(t2))
    # gap 随规模微增，但有上下界
    phase_gap_left = rng.uniform(0.25, 0.55) + 0.02 * min(scale, 8)
    phase_gap_right = rng.uniform(0.25, 0.55) + 0.02 * min(scale, 8)

    align = rng.choice(["center", "bottom", "top"])

    if loop:
        # cycloid 参数：确保 b > a
        loop_a = rng.uniform(0.025, 0.1)
        loop_b = rng.uniform(0.09, 0.26)

        # corewidth：越胖的圈需要越大间距
        # (loop_b - loop_a) 越大圈越胖
        fat = loop_b - loop_a
        corewidth = rng.uniform(0.60, 0.95) + fat * 1.2
        corewidth = max(corewidth, 0.65)

        looparclw = rng.uniform(0.5, 2)
        noloooparclw = rng.uniform(0.5, 2)  # 这个在 loop=False 才用，先给个值

        corelw = rng.uniform(0.5, 2)  # core 不要比绕组粗太多

        return dict(
            t1=t1,
            t2=t2,
            core=core,
            loop=True,
            align=align,
            phase_gap_left=phase_gap_left,
            phase_gap_right=phase_gap_right,
            arcwidth=rng.uniform(
                0.30, 0.55
            ),  # loop模式下通常不用，但你类里可能还会引用
            corewidth=corewidth,
            corelw=corelw,
            looparclw=looparclw,
            noloooparclw=noloooparclw,
            loop_a=loop_a,
            loop_b=loop_b,
        )

    # non-loop 模式
    arcwidth = rng.uniform(0.2, 0.8)
    # corewidth 必须 >= arcwidth + margin，否则左右半圆会挤到一起
    corewidth = rng.uniform(0.2, 1.05)
    corewidth = max(corewidth, arcwidth + 0.35)

    noloooparclw = rng.uniform(0.5, 2)
    looparclw = rng.uniform(0.5, 2)  # loop=True 才用
    corelw = rng.uniform(0.5, 2)

    return dict(
        t1=t1,
        t2=t2,
        core=core,
        loop=False,
        align=align,
        phase_gap_left=phase_gap_left,
        phase_gap_right=phase_gap_right,
        arcwidth=arcwidth,
        corewidth=corewidth,
        corelw=corelw,
        looparclw=looparclw,
        noloooparclw=noloooparclw,
        loop_a=rng.uniform(0.045, 0.075),
        loop_b=rng.uniform(0.16, 0.24),  # 备用
    )


# switch ideal


def sample_switchideal_params(rng: random.Random) -> dict:

    # --- discrete toggles ---
    contacts = rng.random() < 0.5  # mostly with contact dots
    nc = rng.random() < 0.5  # some normally-closed
    action = rng.choices(["", "open", "close"], weights=[0.75, 0.125, 0.125])[0]

    # --- geometry base ---
    length = rng.uniform(0.45, 1.25)  # switch span between contacts
    lead = rng.uniform(0.15, 0.25)  # lead length on each side

    # contact dot radius should be a small fraction of length
    sw_dot_r = rng.uniform(0.03, 0.1) * length

    # linewidths: keep ordering reasonable
    switchlw = rng.uniform(0.5, 2)
    leadlw = max(0.4, min(switchlw, rng.uniform(0.5, 1.2)))
    sw_dot_lw = max(0.4, min(switchlw, rng.uniform(0.5, 1.2)))

    # fill settings
    sw_dot_fill = rng.random() < 0.5
    sw_dot_fill_clr = "black"  # just black for now

    # --- blade constraints ---
    # blade tip must lie between dots, not inside dots:
    # left dot occupies approx [0 - r, 0 + r], right dot occupies [length - r, length + r]
    # We want blade tip x within (2r, length - 2r) for safety.
    xmin = 2.2 * sw_dot_r
    xmax = length - 2.2 * sw_dot_r

    # if length is too small relative to dot size (rare), fix it
    if xmax <= xmin:
        length = max(length, 6 * sw_dot_r)
        xmax = length - 2.2 * sw_dot_r

    blade_tip_x = rng.uniform(max(xmin, 0.55 * length), min(xmax, 0.92 * length))
    blade_x_ratio = blade_tip_x / length

    # blade height: keep within a reasonable band relative to length
    blade_height = rng.uniform(0.18, 0.60) * length

    # --- keep NC consistent (optional aesthetic tweak) ---
    # If normally closed, make blade lower (closer to contact line) so it looks closed-ish.
    if nc:
        blade_height = min(blade_height, 0.35 * length)

    return dict(
        action=action,
        contacts=contacts,
        nc=nc,
        lead=lead,
        leadlw=leadlw,
        switchlw=switchlw,
        sw_dot_r=sw_dot_r,
        sw_dot_fill=sw_dot_fill,
        sw_dot_fill_clr=sw_dot_fill_clr,
        sw_dot_lw=sw_dot_lw,
        length=length,
        blade_x_ratio=blade_x_ratio,
        blade_height=blade_height,
    )


# resistor


def sample_resistor_params(rng: random.Random) -> dict:
    """
    Randomize ResistorCustom(zigs, resheight, lw, pointgapofst) with constraints.
    Assumptions:
      - zigs controls zigzag count
      - resheight controls overall amplitude/height
      - pointgapofst shifts the spacing between zig points (can be negative but not too much)
    """

    # 1) zigs：别太少/太多
    zigs = rng.randint(3, 6)

    # 2) resheight：高度和zigs轻微相关（zigs多时高度稍微小点更像电阻）
    #    经验范围：0.18~0.55（你默认0.5属于偏高，手写风格OK）
    base_h = rng.uniform(0.1, 0.5)
    # zigs 越多，高度稍微压一点，避免“像电感”
    resheight = base_h * (0.95 if zigs <= 6 else 0.80)

    # 3) lw：线宽必须明显小于高度，否则会糊
    #    让 lw 和高度成比例
    lw = rng.uniform(0.5, 2)
    lw = min(lw, resheight * 2.2)  # 高度太小的时候限制 lw
    # lw = max(0.5, lw)

    # 4) pointgapofst：控制尖尖间距的 offset
    #    负值会压缩间距，但不能过头，否则点会重叠/自交
    #    正值会拉开，但太大会变得很稀疏
    #
    #    我们给一个随 zigs 轻微变化的范围：
    #    - zigs 多：允许更小的负值（压缩一点避免太长）
    #    - zigs 少：负值别太多（否则挤没了）
    neg_min = -0.1 if zigs >= 7 else -0.06
    pos_max = 0.20

    pointgapofst = rng.uniform(neg_min, pos_max)

    # 额外安全：不要让压缩过头（你可以按实际视觉继续调）
    # 如果高度很大，压缩也别太多，否则会“锯齿堆叠”
    if resheight > 0.45:
        pointgapofst = max(pointgapofst, -0.10)

    return dict(
        zigs=zigs,
        resheight=resheight,
        lw=lw,
        pointgapofst=pointgapofst,
    )


# inductor


def sample_inductor_params(rng: random.Random) -> dict:

    type_ = rng.choice([1, 2])
    loops = rng.randint(3, 6)

    lw = rng.uniform(0.5, 2)

    core = rng.choices([0, 1, 2], weights=[0.3, 0.4, 0.3])[0]

    corelw = rng.uniform(0.5, 2)
    # corelw = min(corelw, lw * 1.3)

    if type_ == 1:
        # cycloid mode
        a = rng.uniform(0.04, 0.08)
        b = rng.uniform(0.1, 0.2)

        coregap = rng.uniform(0.05, 0.18)
        coreofst = rng.uniform(0.1, 0.5)

        return dict(
            loops=loops,
            lw=lw,
            corelw=corelw,
            a=a,
            b=b,
            type=1,
            core=core,
            coregap=coregap,
            coreofst=coreofst,
            ind_w=0.75,  # unused in type=1
        )

    else:
        # arc mode
        ind_w = rng.uniform(0.15, 0.5)

        # 防止整体太长
        if loops * ind_w > 3:
            ind_w = 3 / loops

        coregap = rng.uniform(0.08, 0.18)
        coreofst = ind_w + rng.uniform(0.05, 0.2)

        return dict(
            loops=loops,
            lw=lw,
            corelw=corelw,
            a=0.06,
            b=0.19,
            type=2,
            core=core,
            coregap=coregap,
            coreofst=coreofst,
            ind_w=ind_w,
        )


# Diode


def sample_diode_params(rng: random.Random) -> dict:

    # 1) overall length: don't be too short or too long
    length = rng.uniform(1, 1.5)

    # 2) triangle height: reasonable fraction of length
    #    too big => looks like arrow; too small => looks flat
    polyheight = rng.uniform(0.1, 0.5) * length

    # 3) bar height: should be close to triangle height, but can vary slightly
    #    keep within [0.8, 1.2] of polyheight
    lineheight = polyheight * rng.uniform(0.8, 1.2)

    # 4) linewidths: keep them small compared to height
    lw = rng.uniform(0.5, 4)
    # prevent lw from being huge relative to geometry
    # lw = min(lw, polyheight * 2.0)  # soft cap
    # lw = max(0.4, lw)

    # triangle outline width: near lw
    polylw = rng.uniform(0.5, 4)

    # 5) fill: keep rare if you want "schematic" style; increase if hand-drawn
    fill = rng.random() < 0.5

    return dict(
        polyheight=polyheight,
        lineheight=lineheight,
        lw=lw,
        polylw=polylw,
        fill=fill,
        length=length,
    )


# capacitor


def sample_capacitor_params(rng: random.Random) -> dict:

    # type：按你现有实现来放（你现在默认2）
    # 如果你只有 1/2 两种，就用 [1,2]
    type_ = rng.choice([1, 2])

    # 是否极性：电解电容概率低一点（否则数据里全是极性电容不太真实）
    polar = rng.random() < 0.25

    # plate height：太小像短杠；太大像电池
    # 一般 0.18 ~ 0.45 都挺像，默认 0.25 合理
    height = rng.uniform(0.18, 0.42)

    # capgap：间隙太小会糊、太大不像电容
    # 同时要和线宽成比例：capgap >= ~ 1.5 * caplw 才不会贴一起
    caplw = rng.uniform(0.5, 3)  # 你默认2，说明你希望粗一点也OK

    capgap = rng.uniform(0.08, 0.35)
    capgap = max(capgap, 1.6 * (caplw / 10.0))  # 小约束：线越粗，间隙稍大（经验式）

    # 再做一个“高度-间隙”的比例约束，避免变成 “两根远离的线”
    # capgap 不要超过高度太多（否则看起来像开关）
    capgap = min(capgap, height * 0.9)

    return dict(
        polar=polar,
        type=type_,
        height=height,
        capgap=capgap,
        caplw=caplw,
    )


# Battery
def sample_battery_params(rng: random.Random) -> dict:

    double = rng.random() < 0.6
    lw = rng.uniform(0.6, 5)
    # 板间距
    batw = rng.uniform(0.09, 0.3)

    # 长板高度
    bat1 = rng.uniform(0.18, 0.45)

    # 短板高度（必须小于长板）
    bat2 = bat1 * rng.uniform(0.35, 0.75)

    return dict(
        double=double,
        batw=batw,
        bat1=bat1,
        bat2=bat2,
        lw=lw,
    )


# current source


def sample_current_src_params(rng: random.Random) -> dict:
    # 圆半径：别太小，否则箭头放不下；别太大，否则和其它器件尺度不一致
    r = rng.uniform(0.3, 0.8)

    # 圆线宽：一般略小于箭头线宽或接近
    circlelw = rng.uniform(0.7, 3)

    # 箭尾线宽：不要比圆线宽大太多
    arrowlw = rng.uniform(0.7, 1.8)

    arrowwidth = rng.uniform(0.20, 0.55) * r  # 三角宽
    arrowlength = rng.uniform(0.18, 0.45) * r  # 三角长

    theta = rng.choice([0, 45, 90, 135, 180, 225, 270, 315])

    # 先随机一个箭尾起点（离圆心不要太近也不要太远）
    arrowstart = rng.uniform(0.5 - 0.88 * r, 0.5 - 0.7 * r)
    arrowtaillength = rng.uniform(r * 1, r * 1.8)

    return dict(
        arrowwidth=arrowwidth,
        arrowlength=arrowlength,
        arrowlw=arrowlw,
        r=r,
        theta=theta,
        arrowstart=arrowstart,
        arrowtaillength=arrowtaillength,
        circlelw=circlelw,
    )


# volt src


def sample_volt_src_params(rng: random.Random) -> dict:
    # 圆半径
    r = rng.uniform(0.35, 0.8)

    # 圆线宽
    circlelw = rng.uniform(0.7, 3)

    theta = rng.choice([0, 45, 90, 135, 180, 225, 270, 315])
    # theta = rng.uniform(0, 360)  # 如果想连续角

    # +/- 的长度：必须明显小于直径
    # 再考虑线宽后，给安全边界 margin
    margin = rng.uniform(0.72, 0.85)
    plus_len = rng.uniform(0.20, 0.55) * (2 * r) * margin

    # +/- 线宽：不要太粗，且别比 plus_len 大太多
    pluslw = rng.uniform(0.7, 3)
    minuslw = rng.uniform(0.7, 3)

    # 放置位置：符号必须落在圆内
    # 你的圆心固定在 (0.5, 0)，所以用这个坐标系做约束
    cx, cy = 0.5, 0.0

    # dx 不要太小，否则 + - 挤在中间
    dx = rng.uniform(plus_len / 2, 0.85 * (r - plus_len / 2))

    plusx = cx + dx
    minusx = cx - dx

    return dict(
        r=r,
        theta=theta,
        circlelw=circlelw,
        plus_len=plus_len,
        pluslw=pluslw,
        minuslw=minuslw,
        minusx=minusx,
        plusx=plusx,
    )


# ac src
def sample_ac_src_params(rng: random.Random) -> dict:
    """
    Random parameters for your existing ACSourceCustom
    WITHOUT modifying implementation.
    """

    # r 必须 >= 0.35 才能包住固定正弦
    r = rng.uniform(0.45, 1.0)

    # 圆线宽
    circlelw = rng.uniform(0.8, 2.5)

    # 正弦线宽（不要比圆粗太多）
    sin_lw = rng.uniform(0.6, 2.0)
    sin_lw = min(sin_lw, circlelw * 1.4)

    # 旋转角度
    # 离散角度更像电路图
    theta = rng.choice([0, 45, 90, 135, 180, 225, 270, 315])

    return dict(
        r=r,
        theta=theta,
        circlelw=circlelw,
        sin_lw=sin_lw,
    )


def make_component(cls: str, rng: random.Random):
    if cls == "ac_src":
        return ACSourceCustom(**sample_ac_src_params(rng))  # customized
    if cls == "volt_src":
        return VoltageSourceCustom(**sample_volt_src_params(rng))
    if cls == "curr_src":
        return CurrentSourceCustom(**sample_current_src_params(rng))
    if cls == "battery":
        return BatteryCustom(**sample_battery_params(rng))
    if cls == "cap":
        return CapacitorCustom(**sample_capacitor_params(rng))
    if cls == "diode":
        return DiodeCustom(**sample_diode_params(rng))
    if cls == "inductor":
        return InductorCustom(**sample_inductor_params(rng))
    if cls == "resistor":
        return ResistorCustom(**sample_resistor_params(rng))
    if cls == "swi_ideal":
        return SwitchIdealCustom(**sample_switchideal_params(rng))
    if cls == "swi_real":
        return NMosCustom()  # 暂时用系统自带的
    if cls == "xformer":
        return TransformerCustom(**sample_transformer_params(rng))
    raise ValueError(f"Unknown component class: {cls}")


class BBoxRect(Element):
    def __init__(self, xmin, ymin, xmax, ymax, lw=0.8):
        super().__init__()
        self.segments.append(Segment([(xmin, ymin), (xmax, ymin)], lw=lw))
        self.segments.append(Segment([(xmax, ymin), (xmax, ymax)], lw=lw))
        self.segments.append(Segment([(xmax, ymax), (xmin, ymax)], lw=lw))
        self.segments.append(Segment([(xmin, ymax), (xmin, ymin)], lw=lw))


# =========================
# DRAW TEST SECTION
# =========================

if __name__ == "__main__":

    component_list = [
        "ac_src",
        "volt_src",
        "curr_src",
        "battery",
        "cap",
        "diode",
        "inductor",
        "resistor",
        "swi_ideal",
        "xformer",
        "swi_real",
    ]

    dx = 4.0
    dy = 3.0
    cols = 4
    d = schemdraw.Drawing()

    for i, name in enumerate(component_list):
        rng = make_rng()
        r, c = divmod(i, cols)
        x, y = c * dx, -r * dy

        elem = make_component(name, rng)
        d += elem.at((x, y))
        elem.label(name, loc="bottom")

        # --- 1) 元件自身 bbox（未应用 transform） ---
        bb_local = elem.get_bbox(transform=False, includetext=False)
        print(name, "local bbox (no transform, no text):", bb_local)

        # --- 2) 放到 drawing 里的 bbox（应用 transform） ---
        bb_world = elem.get_bbox(transform=True, includetext=False)
        print(name, "world bbox (transform, no text):", bb_world)

        # 画 world bbox 框出来（你也可以画 local bbox，但要手动加偏移/变换，麻烦）
        xmin, ymin, xmax, ymax = bb_world
        d += BBoxRect(xmin, ymin, xmax, ymax, lw=0.8)

    d.draw(show=True)
    # d.save("bbox_debug.svg")
    # print("Saved bbox_debug.svg")
    # for i in range(20):
    #     rng = make_rng()
    #     r, c = divmod(i, cols)
    #     x, y = c * dx, -r * dy

    #     elem = make_component("ac_src", rng)
    #     d += elem.at((x, y))
    #     elem.label("ac_src", loc="bottom")
    # d.draw(show=True)
