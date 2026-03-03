from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentText


class VoltageSourceCustom(Element):
    """
    Voltage source: circle with + and -.
    """

    def __init__(self, length=2.2, radius=0.35, lw=1.5):
        super().__init__()
        lead = (length - 2 * radius) / 2
        cx = lead + radius

        # leads
        self.segments.append(Segment([(0, 0), (lead, 0)], lw=lw))
        self.segments.append(Segment([(lead + 2 * radius, 0), (length, 0)], lw=lw))

        # circle
        self.segments.append(SegmentCircle((cx, 0), radius=radius, lw=lw))

        # + / -
        self.segments.append(SegmentText((cx, 0.12), "+", fontsize=10))
        self.segments.append(SegmentText((cx, -0.18), "-", fontsize=10))

        self.anchors["start"] = (0, 0)
        self.anchors["end"] = (length, 0)
