from schemdraw.elements import Element
from schemdraw.segments import Segment


class SwitchIdealCustom(Element):
    """
    Ideal switch: two contacts with a tilted blade (open switch).
    """

    def __init__(self, length=2.2, gap=0.35, blade=0.45, lw=1.5):
        super().__init__()
        lead = (length - gap) / 2
        xL = lead
        xR = lead + gap

        # leads
        self.segments.append(Segment([(0, 0), (xL, 0)], lw=lw))
        self.segments.append(Segment([(xR, 0), (length, 0)], lw=lw))

        # contacts (small vertical ticks)
        self.segments.append(Segment([(xL, -0.12), (xL, 0.12)], lw=lw))
        self.segments.append(Segment([(xR, -0.12), (xR, 0.12)], lw=lw))

        # blade from left contact upwards toward right
        self.segments.append(Segment([(xL, 0.0), (xL + blade, 0.25)], lw=lw))

        self.anchors["start"] = (0, 0)
        self.anchors["end"] = (length, 0)
