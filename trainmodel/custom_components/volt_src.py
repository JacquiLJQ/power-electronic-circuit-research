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
        **kwargs
    ):
        super().__init__(**kwargs)
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
