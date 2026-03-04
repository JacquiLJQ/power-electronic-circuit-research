from __future__ import annotations
from typing import Optional, Sequence
import math

from schemdraw.segments import Segment, SegmentArc
from schemdraw.elements import Element
from schemdraw.elements.twoterm import cycloid
from schemdraw.types import XformTap


class TransformerCustom(Element):

    def __init__(
        self,
        t1: int | Sequence[int] = 4,  # 左边画几个线圈，分别画多长
        t2: int | Sequence[int] = 4,  # 右边画几个线圈，分别画多长
        *,
        core: bool = True,  # 是否画core
        loop: bool = False,  # 是否用cycloid画loop
        align: str = "center",  # 线圈alignment
        phase_gap_left: float = 0.4,  # 左边绕组的间隙
        phase_gap_right: float = 0.4,  # 右边绕组的间隙
        arcwidth: float = 0.4,  # 非loop模式下，每一个半弧圆的直径大小 (如果变大整个xformer会变高)
        corewidth: float = 0.75,  # 左右两个线圈之间的水平间距
        corelw: float = 1,  # 画core的线条宽度
        looparclw: float = 1,  # 画cycloid loop的线条宽度
        nolooparclw: float = 1,  # 画非loop的圆弧的线条宽度
        loop_a: float = 0.06,  # 用cycloid画loop的a值
        loop_b: float = 0.2,  # 0.19,  # 用cycloid画loop的b值. b>a -> 胖线圈，b≈a -> 普通线圈
        **kwargs,  # 可以设置整体线条宽度
    ):
        super().__init__(**kwargs)

        if isinstance(t1, int):
            t1 = [t1]
        if isinstance(t2, int):
            t2 = [t2]

        self._t1, self._t2 = t1, t2

        if loop == True:
            corewidth = corewidth + 0.4
        if core == True:
            corewidth = corewidth + 0.25
        # self._corewidth = corewidth

        def right_position():
            if align == "center":
                right_bot = left_height / 2 - right_height / 2
                right_top = right_bot + right_height
            elif align == "bottom":
                right_bot = 0
                right_top = right_height
            else:
                right_top = left_height
                right_bot = right_top - right_height
            return right_bot, right_top

        if loop == True:
            left_cycloids = [
                cycloid(n, a=loop_a, b=loop_b, norm=False, vertical=True) for n in t1
            ]
            right_cycloids = [
                cycloid(
                    n,
                    a=loop_a,
                    b=loop_b,
                    ofst=(corewidth, 0),
                    norm=False,
                    vertical=True,
                    flip=True,
                )
                for n in t2
            ]
            left_height = sum(c[-1][1] for c in left_cycloids) + phase_gap_left * (
                len(left_cycloids) - 1
            )
            right_height = sum(c[-1][1] for c in right_cycloids) + phase_gap_right * (
                len(right_cycloids) - 1
            )

            left_bot = 0
            left_top = left_height
            right_bot, right_top = right_position()

            # 画tap的
            # a, b = 0.06, 0.19
            # yint = math.acos(a / b)
            # period = math.pi * 2 * a
            # ofst = period - (a * yint - b * math.sin(yint))
            # resheight = 0.25  # 0.25
            # tapxofst = (a - b) / 2 / resheight

            y = left_bot
            tapnum = 0
            for i, cyc in enumerate(left_cycloids):
                height = cyc[-1][1]
                cyc_y = [(c[0], c[1] + y) for c in cyc]  # Shift to vertical position
                self.segments.append(Segment(cyc_y, lw=looparclw))
                self.anchors[f"p{i*2+1}"] = cyc_y[0]
                self.anchors[f"p{i*2+2}"] = cyc_y[-1]
                left_top = cyc_y[-1][1]

                # tap 相关
                # for k in range(0, t1[i]):
                #     self.anchors[f"tapP{tapnum+k+1}"] = (
                #         tapxofst,
                #         cyc_y[0][1] + k * period + ofst,
                #     )

                # tapnum += k + 1
                y += height + phase_gap_left

            y = right_bot
            tapnum = 0
            for i, cyc in enumerate(right_cycloids):
                height = cyc[-1][1]
                cyc_y = [(c[0], c[1] + y) for c in cyc]  # Shift to vertical position
                self.segments.append(Segment(cyc_y, lw=looparclw))
                self.anchors[f"s{i*2+1}"] = cyc_y[0]
                self.anchors[f"s{i*2+2}"] = cyc_y[-1]
                right_top = cyc_y[-1][1]
                # tap 相关
                # for k in range(0, t2[i]):
                #     self.anchors[f"tapS{tapnum+k+1}"] = (
                #         corewidth - tapxofst,
                #         cyc_y[0][1] + k * period + ofst,
                #     )
                # tapnum += k + 1

                y += height + phase_gap_right

        else:  # Not loop
            arcw = arcwidth

            left_height = sum(t1) * arcw + phase_gap_left * (len(t1) - 1)
            right_height = sum(t2) * arcw + phase_gap_right * (len(t2) - 1)
            left_bot = 0
            left_top = left_height
            right_bot, right_top = right_position()

            y = left_bot
            tapnum = 0
            for i, turns in enumerate(t1):
                self.anchors[f"p{i*2+2}"] = (0, y)
                self.anchors[f"p{i*2+1}"] = (0, y + turns * arcw)
                for k in range(turns):
                    self.segments.append(
                        SegmentArc(
                            (0, y + arcw / 2),
                            theta1=270,
                            theta2=90,
                            width=arcw,
                            height=arcw,
                            lw=nolooparclw,
                        )
                    )
                    if k < turns - 1:
                        self.anchors[f"tapP{tapnum+k+1}"] = (0, y + arcw)
                    y += arcw
                tapnum += turns - 1
                y += phase_gap_left

            y = right_bot
            tapnum = 0
            for i, turns in enumerate(t2):
                self.anchors[f"s{i*2+2}"] = (corewidth, y)
                self.anchors[f"s{i*2+1}"] = (corewidth, y + turns * arcw)
                for k in range(turns):
                    self.segments.append(
                        SegmentArc(
                            (corewidth, y + arcw / 2),
                            theta1=90,
                            theta2=270,
                            width=arcw,
                            height=arcw,
                            lw=nolooparclw,
                        )
                    )
                    if k < turns - 1:
                        self.anchors[f"tapS{tapnum+k+1}"] = (corewidth, y + arcw)
                    y += arcw
                tapnum += turns - 1
                y += phase_gap_right

        if core == True:
            top = max(left_top, right_top)
            bot = min(left_bot, right_bot)
            center = corewidth / 2
            core_w = corewidth / 10
            self.segments.append(
                Segment([(center - core_w, top), (center - core_w, bot)], lw=corelw)
            )
            self.segments.append(
                Segment([(center + core_w, top), (center + core_w, bot)], lw=corelw)
            )

        self._left_top = left_top
        self._right_top = right_top
