import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentArc, SegmentCircle

sw_dot_r = 0.12

gap = (math.nan, math.nan)


class SwitchIdealCustom(Element):
    """
    Ideal switch: two contacts with a tilted blade (open switch).
    """

    # def __init__(self, length=2.2, gap=0.35, blade=0.45, lw=1.5):
    #     super().__init__()
    #     lead = (length - gap) / 2
    #     xL = lead
    #     xR = lead + gap

    #     # leads
    #     self.segments.append(Segment([(0, 0), (xL, 0)], lw=lw))
    #     self.segments.append(Segment([(xR, 0), (length, 0)], lw=lw))

    #     # contacts (small vertical ticks)
    #     self.segments.append(Segment([(xL, -0.12), (xL, 0.12)], lw=lw))
    #     self.segments.append(Segment([(xR, -0.12), (xR, 0.12)], lw=lw))

    #     # blade from left contact upwards toward right
    #     self.segments.append(Segment([(xL, 0.0), (xL + blade, 0.25)], lw=lw))

    #     self.anchors["start"] = (0, 0)
    #     self.anchors["end"] = (length, 0)
    _element_defaults = {
        "arrowwidth": 0.15,
        "arrowlength": 0.25,
        "arrow_lw": None,
        "arrow_color": None,
    }

    def __init__(
        self,
        action: str = "",
        contacts: bool = True,
        nc: bool = False,
        type: int = 1,
        **kwargs
    ):
        super().__init__(**kwargs)
        if contacts:
            if nc:
                self.segments.append(
                    Segment(
                        [
                            (0, 0),
                            gap,
                            (sw_dot_r * 2, 0),
                            (0.9, sw_dot_r + 0.05),
                            gap,
                            (1, 0),
                        ]
                    )
                )
            else:
                self.segments.append(
                    Segment(
                        [(0, 0), gap, (sw_dot_r * 2, 0.1), (0.8, 0.45), gap, (1, 0)]
                    )
                )
            self.segments.append(
                SegmentCircle((sw_dot_r, 0), sw_dot_r, fill="bg", zorder=3)
            )
            self.segments.append(
                SegmentCircle((1 - sw_dot_r, 0), sw_dot_r, fill="bg", zorder=3)
            )

        else:

            if nc:
                self.segments.append(Segment([(0, 0), (1.15, 0.45), gap, (1, 0)]))
                self.segments.append(Segment([(1, 0), (1, 0.55)]))
            else:
                self.segments.append(Segment([(0, 0), (0.85, 0.45), gap, (1, 0)]))

        if action == "open":
            self.segments.append(
                SegmentArc(
                    (0.4, 0.1),
                    width=0.5,
                    height=0.75,
                    theta1=-10,
                    theta2=70,
                    arrow="ccw",
                    lw=self.params["arrow_lw"],
                    color=self.params["arrow_color"],
                    arrowwidth=self.params["arrowwidth"],
                    arrowlength=self.params["arrowlength"],
                )
            )
        if action == "close":
            self.segments.append(
                SegmentArc(
                    (0.4, 0.25),
                    width=0.5,
                    height=0.75,
                    theta1=-10,
                    theta2=70,
                    arrow="cw",
                    lw=self.params["arrow_lw"],
                    color=self.params["arrow_color"],
                    arrowwidth=self.params["arrowwidth"],
                    arrowlength=self.params["arrowlength"],
                )
            )
