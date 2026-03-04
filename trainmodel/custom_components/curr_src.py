import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentPoly

gap = (math.nan, math.nan)


class CurrentSourceCustom(Element):
    """
    Current source: circle with arrow.
    """

    # _element_defaults = {
    #     "arrowwidth": 0.15,
    #     "arrowlength": 0.25,
    #     "arrow_lw": None,
    #     "arrow_color": None,
    # }

    def __init__(
        self,
        arrowwidth=0.3,  # 三角形尖尖的宽
        arrowlength=0.25,  # 三角形尖尖的长
        arrowlw=1,
        r=0.5,
        theta=90,
        arrowstart=0.2,  # 线段(尾巴)起始
        arrowtaillength=0.6,  # 线段(尾巴)长
        circlelw=1,  # 外圈圆形线宽
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
