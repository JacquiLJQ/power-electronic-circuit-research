import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentPoly

gap = (math.nan, math.nan)


class CurrentSourceCustom(Element):
    """
    Current source: circle with arrow.
    """

    _element_defaults = {
        "arrowwidth": 0.15,
        "arrowlength": 0.25,
        "arrow_lw": None,
        "arrow_color": None,
    }

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
        self.segments.append(
            Segment(
                [(0.25, 0), (0.75, 0)],
                arrow="->",
                arrowwidth=self.params["arrowwidth"],
                arrowlength=self.params["arrowlength"],
                lw=self.params["arrow_lw"],
                color=self.params["arrow_color"],
            )
        )
