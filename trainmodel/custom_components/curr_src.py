import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentPoly

gap = (math.nan, math.nan)


class CurrentSourceCustom(Element):
    """
    Current source: circle with arrow.
    """

    def __init__(
        self,
        arrowwidth=0.3,  # 三角形尖尖的宽
        arrowlength=0.25,  # 三角形尖尖的长
        arrowlw=1,  # 箭头尾巴线宽
        r=0.5,  # 圆圈半径
        theta=90,
        arrowstart=0.2,  # 箭头线段(尾巴)起始
        arrowtaillength=0.6,  # 箭头线段(尾巴)长
        circlelw=1,  # 圆圈线宽
        **kwargs
    ):
        super().__init__(**kwargs)
        self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))
        self.segments.append(SegmentCircle((0.5, 0), r, lw=circlelw))
        self.elmparams["theta"] = theta
        self.segments.append(
            Segment(
                [(arrowstart, 0), (arrowstart + arrowtaillength, 0)],
                arrow="->",
                arrowwidth=arrowwidth,
                arrowlength=arrowlength,
                lw=arrowlw,
                color="black",
                fill=None,
            )
        )
