from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentPoly


class DiodeCustom(Element):
    """
    Simple diode: triangle -> bar.
    """

    def __init__(self, length=2.0, height=0.6, lw=1.5):
        super().__init__()
        lead = 0.5
        body_len = max(0.3, length - 2 * lead)

        xL = lead
        xR = lead + body_len
        y = height / 2

        # leads
        self.segments.append(Segment([(0, 0), (xL, 0)], lw=lw))
        self.segments.append(Segment([(xR, 0), (length, 0)], lw=lw))

        # triangle pointing right
        tri = [(xL, -y), (xL, y), (xR - 0.15, 0)]
        self.segments.append(SegmentPoly(tri, closed=True, lw=lw))

        # cathode bar
        self.segments.append(Segment([(xR - 0.15, -y), (xR - 0.15, y)], lw=lw))

        self.anchors["start"] = (0, 0)
        self.anchors["end"] = (length, 0)
