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
        r=0.5,
        theta=90,
        circlelw=1,
        plus_len=0.2,
        pluslw=1,
        minuslw=1,
        minusx=0.1,
        plusx=0.5,
        **kwargs
    ):  # 外圈圆形线宽
        super().__init__()
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
