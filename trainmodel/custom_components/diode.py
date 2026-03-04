import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentPoly

height = 0.25  # Resistor height

gap = (math.nan, math.nan)


class DiodeCustom(Element):
    """
    Simple diode: triangle -> bar.
    """

    def __init__(
        self,
        polyheight=0.2,  # 三角形高
        lineheight=0.2,  # 直线高
        lw=1,
        polylw=1,
        fill=False,
        length=2,  # 三角形要拉长多少
    ):
        super().__init__()
        line_seg = Segment(
            [
                (0, 0),
                gap,
                (lineheight * length, height),
                (lineheight * length, -height),
                gap,
                (lineheight * length, 0),
            ],
            lw=lw,
        )
        self.segments.append(line_seg)
        line_height = abs(line_seg.get_bbox().ymax - line_seg.get_bbox().ymin) / 2

        self.segments.append(
            SegmentPoly(
                [(0, line_height), (lineheight * length, 0), (0, -line_height)],
                fill=fill,
                color="black",
                lw=polylw,
            )
        )
