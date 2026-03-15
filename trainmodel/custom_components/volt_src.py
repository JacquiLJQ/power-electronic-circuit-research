import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentText

gap = (math.nan, math.nan)


class VoltageSourceCustom(Element):
    """
    Voltage source: circle with + and -.
    """

    def __init__(
        self,
        r=0.5,  # 圆圈半径
        theta=90,  # 角度
        circlelw=1,  # 圆圈线宽
        plus_len=0.2,  # 加号长
        pluslw=1,  # 加号线宽
        minuslw=1,  # 减号线宽
        minusx=0.1,  # 减号起始x
        plusx=0.5,  # 加号起始x
        specificstyle=True,
        style=1,
        **kwargs
    ):
        super().__init__(**kwargs)
        if specificstyle == True:
            # style 1
            # self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))

            # self.segments.append(SegmentCircle((0.5, 0), 0.5, 3))
            # self.elmparams["theta"] = 90

            # self.segments.append(
            #     Segment([(0.1, 0.1), (0.1,0.35)], lw=2.5)
            # )  # '-' sign
            # self.segments.append(
            #     Segment(
            #         [(0.6 , 0), (0, 0)],
            #         lw=1,
            #     )
            # )  # '+' sign
            # self.segments.append(Segment([(0.6, 0.1), (0.6, 0.5)], lw=1))
            if style == 1:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=3))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.21
                plus_half_w = 0.14
                plus_half_h = 0.14

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.15

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=2.8,
                        capstyle="butt",
                    )
                )  # - horizontal

            elif style == 2:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=3))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.21
                plus_half_w = 0.14
                plus_half_h = 0.14

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.15

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 3:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1.5))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.21
                plus_half_w = 0.15
                plus_half_h = 0.14

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.15

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 4:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1.5))
                self.elmparams["theta"] = 180

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.21
                plus_half_w = 0.15
                plus_half_h = 0.14

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.15

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 5:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=3))
                self.elmparams["theta"] = 180

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.21
                plus_half_w = 0.14
                plus_half_h = 0.14

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.15

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 6:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.3
                plus_half_w = 0.12
                plus_half_h = 0.12

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=1,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.32
                minus_half_w = 0.12

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=1,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 7:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.4, lw=3))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.21
                plus_half_w = 0.14
                plus_half_h = 0.12

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.1
                minus_half_w = 0.1

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 8:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=2))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.20
                plus_half_w = 0.17
                plus_half_h = 0.17

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=2,
                        capstyle="round",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=2,
                        capstyle="round",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.15
                minus_half_w = 0.18

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=2,
                        capstyle="round",
                    )
                )  # - horizontal
            elif style == 9:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=2.2))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.3
                plus_half_w = 0.1
                plus_half_h = 0.1

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=2.2,
                        capstyle="projecting",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=2.2,
                        capstyle="projecting",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.32
                minus_half_w = 0.1

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=2.2,
                        capstyle="projecting",
                    )
                )  # - horizontal
            elif style == 10:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.45, lw=2.2))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.21
                plus_half_w = 0.11
                plus_half_h = 0.11

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=2.2,
                        capstyle="round",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=2.2,
                        capstyle="round",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.22
                minus_half_w = 0.1

                self.segments.append(
                    Segment(
                        [(cx, minus_y - minus_half_w), (cx, minus_y + minus_half_w)],
                        lw=2.2,
                        capstyle="round",
                    )
                )  # - horizontal
            elif style == 11:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=2))
                self.elmparams["theta"] = 90

                cx, cy = 0.45, 0.0

                # 上方 +
                plus_y = cy + 0.15
                plus_half_w = 0.1
                plus_half_h = 0.1

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=2,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=2,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.32
                minus_half_w = 0.06

                self.segments.append(
                    Segment(
                        [(cx, minus_y - minus_half_w), (cx, minus_y + minus_half_w)],
                        lw=2,
                        capstyle="round",
                    )
                )  # - horizontal

            elif style == 12:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.4, lw=2.2))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.15
                plus_half_w = 0.11
                plus_half_h = 0.11

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=2.2,
                        capstyle="round",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=2.2,
                        capstyle="round",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.15
                minus_half_w = 0.1

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=2.2,
                        capstyle="round",
                    )
                )
            if style == 13:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=3))
                self.elmparams["theta"] = -90

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.21
                plus_half_w = 0.14
                plus_half_h = 0.14

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=0.8,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.15

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=2.8,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 14:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.2
                plus_half_w = 0.1
                plus_half_h = 0.1

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1.5,
                        capstyle="round",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=1.8,
                        capstyle="round",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.2
                minus_half_w = 0.07

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=3,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 15:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.23
                plus_half_w = 0.11
                plus_half_h = 0.11

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1.9,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=1.9,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.08

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=1.8,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 16:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.18
                plus_half_w = 0.22
                plus_half_h = 0.22

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=1,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.19

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=1.8,
                        capstyle="butt",
                    )
                )  # - horizontal
            elif style == 17:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=3))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.18
                plus_half_w = 0.22
                plus_half_h = 0.22

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=3,
                        capstyle="round",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=3,
                        capstyle="round",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.19

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=3,
                        capstyle="round",
                    )
                )  # - horizontal
            elif style == 18:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1.5))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.2
                plus_half_w = 0.15
                plus_half_h = 0.15

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1.5,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=1.5,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.2
                minus_half_w = 0.15

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=1.5,
                        capstyle="butt",
                    )
                )  # - horizontal

            elif style == 19:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.23
                plus_half_w = 0.11
                plus_half_h = 0.11

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1.9,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=1.9,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.20
                minus_half_w = 0.08

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=1.8,
                        capstyle="butt",
                    )
                )  # - horizontal

            elif style == 20:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=2.2))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.23
                plus_half_w = 0.1
                plus_half_h = 0.1

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=2.2,
                        capstyle="projecting",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=2.2,
                        capstyle="projecting",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.23
                minus_half_w = 0.1

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=2.2,
                        capstyle="projecting",
                    )
                )  # - horizontal

            elif style == 21:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=1.5))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.3
                plus_half_w = 0.1
                plus_half_h = 0.1

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=1.5,
                        capstyle="round",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=1.5,
                        capstyle="round",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.32
                minus_half_w = 0.1

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=1.5,
                        capstyle="round",
                    )
                )  # - horizontal
            elif style == 22:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.5, lw=2))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.2
                plus_half_w = 0.14
                plus_half_h = 0.14

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=2,
                        capstyle="round",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=2,
                        capstyle="round",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.28
                minus_half_w = 0.14

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=2,
                        capstyle="round",
                    )
                )  # - horizontal
            elif style == 23:
                self.segments.append(Segment([(0, 0), gap, (1, 0)]))

                self.segments.append(SegmentCircle((0.5, 0), 0.4, lw=2))
                self.elmparams["theta"] = 0

                cx, cy = 0.5, 0.0

                # 上方 +
                plus_y = cy + 0.11
                plus_half_w = 0.18
                plus_half_h = 0.18

                self.segments.append(
                    Segment(
                        [(cx - plus_half_w, plus_y), (cx + plus_half_w, plus_y)],
                        lw=2,
                        capstyle="butt",
                    )
                )  # + horizontal
                self.segments.append(
                    Segment(
                        [(cx, plus_y - plus_half_h), (cx, plus_y + plus_half_h)],
                        lw=2,
                        capstyle="butt",
                    )
                )  # + vertical

                # 下方 -
                minus_y = cy - 0.17
                minus_half_w = 0.18

                self.segments.append(
                    Segment(
                        [(cx - minus_half_w, minus_y), (cx + minus_half_w, minus_y)],
                        lw=2,
                        capstyle="butt",
                    )
                )  # - horizontal

        else:
            self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))

            self.segments.append(SegmentCircle((0.5, 0), r, lw=circlelw))
            self.elmparams["theta"] = theta

            self.segments.append(
                Segment([(minusx, -plus_len / 2), (minusx, plus_len / 2)], lw=minuslw)
            )  # '-' sign
            self.segments.append(
                Segment(
                    [(plusx - plus_len / 2, 0), (plusx + plus_len / 2, 0)],
                    lw=pluslw,
                )
            )  # '+' sign
            self.segments.append(
                Segment([(plusx, -plus_len / 2), (plusx, plus_len / 2)], lw=pluslw)
            )
