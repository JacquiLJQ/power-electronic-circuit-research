import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentArc, SegmentText

resheight = 0.25  # Resistor height
reswidth = 1.0 / 6
gap = (math.nan, math.nan)


class CapacitorCustom(Element):
    """
    Two-plate capacitor.
    """

    # def __init__(self, length=2.0, gap=0.25, plate=0.6, lw=1.5):
    #     super().__init__()
    #     lead = (length - gap) / 2

    #     x1 = lead
    #     x2 = lead + gap
    #     y = plate / 2

    #     # leads
    #     self.segments.append(Segment([(0, 0), (x1, 0)], lw=lw))
    #     self.segments.append(Segment([(x2, 0), (length, 0)], lw=lw))

    #     # plates (vertical)
    #     self.segments.append(Segment([(x1, -y), (x1, y)], lw=lw))
    #     self.segments.append(Segment([(x2, -y), (x2, y)], lw=lw))

    #     self.anchors["start"] = (0, 0)
    #     self.anchors["end"] = (length, 0)
    _element_defaults = {"polar": False}

    def __init__(self, *, polar: bool = False, type: int = 2, **kwargs):
        super().__init__(**kwargs)
        capgap = 0.18
        if type == 1:
            self.segments.append(
                Segment(
                    [
                        (0, 0),
                        gap,
                        (0, resheight),
                        (0, -resheight),
                        gap,
                        (capgap, resheight),
                        (capgap, -resheight),
                        gap,
                        (capgap, 0),
                    ]
                )
            )
        if type == 2:
            self.segments.append(
                Segment(
                    [(0, 0), gap, (0, resheight), (0, -resheight), gap, (capgap, 0)]
                )
            )
            self.segments.append(
                SegmentArc(
                    (capgap * 1.5, 0),
                    width=capgap * 1.5,
                    height=resheight * 2.5,
                    theta1=105,
                    theta2=-105,
                )
            )
        if self.params["polar"]:
            self.segments.append(SegmentText((-capgap * 1.2, capgap), "+"))
