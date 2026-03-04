import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentBezier
from schemdraw import util

gap = (math.nan, math.nan)


class ACSourceCustom(Element):
    """
    AC source: circle with sine-like bezier inside.
    """

    _element_defaults = {"sin_lw": None, "sin_color": None}

    def __init__(self, length=2.2, radius=0.35, lw=1.5):
        super().__init__()
        self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))
        self.segments.append(
            SegmentCircle(
                (0.5, 0),
                0.5,
            )
        )
        self.elmparams["theta"] = 90
        sin_y = util.linspace(-0.25, 0.25, num=25)
        sin_x = [0.2 * math.sin((sy - 0.25) * math.pi * 2 / 0.5) + 0.5 for sy in sin_y]
        self.segments.append(
            Segment(
                list(zip(sin_x, sin_y)),
                lw=self.params["sin_lw"],
                color=self.params["sin_color"],
            )
        )
