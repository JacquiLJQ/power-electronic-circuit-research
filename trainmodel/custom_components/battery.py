import math

from schemdraw.elements import Element
from schemdraw.segments import Segment

resheight = 0.25  # Resistor height

batw = resheight * 0.75
bat1 = resheight * 1.5
bat2 = resheight * 0.75
gap = (math.nan, math.nan)


class BatteryCustom(Element):
    """
    Battery symbol: long plate + short plate.
    """

    def __init__(
        self,
        double=False,
        length=2.2,
        long_plate=0.8,
        short_plate=0.45,
        # gap=0.25,
        lw=1.5,
    ):
        super().__init__()
        # lead = (length - gap) / 2
        # x1 = lead
        # x2 = lead + gap

        # # leads
        # self.segments.append(Segment([(0, 0), (x1, 0)], lw=lw))
        # self.segments.append(Segment([(x2, 0), (length, 0)], lw=lw))

        # # plates
        # self.segments.append(
        #     Segment([(x1, -long_plate / 2), (x1, long_plate / 2)], lw=lw)
        # )
        # self.segments.append(
        #     Segment([(x2, -short_plate / 2), (x2, short_plate / 2)], lw=lw)
        # )

        # self.anchors["start"] = (0, 0)
        # self.anchors["end"] = (length, 0)
        if double:
            self.segments.append(Segment([(0, 0), gap, (batw * 3, 0)]))
            self.segments.append(Segment([(0, bat1), (0, -bat1)]))
            self.segments.append(Segment([(batw, bat2), (batw, -bat2)]))
            self.segments.append(Segment([(batw * 2, bat1), (batw * 2, -bat1)]))
            self.segments.append(Segment([(batw * 3, bat2), (batw * 3, -bat2)]))
        else:
            self.segments.append(Segment([(0, 0), gap, (batw, 0)]))
            self.segments.append(Segment([(0, bat1), (0, -bat1)]))
            self.segments.append(Segment([(batw, bat2), (batw, -bat2)]))
