from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentPoly


class CurrentSourceCustom(Element):
    """
    Current source: circle with arrow.
    """

    def __init__(self, length=2.2, radius=0.35, lw=1.5):
        super().__init__()
        lead = (length - 2 * radius) / 2
        cx = lead + radius

        self.segments.append(Segment([(0, 0), (lead, 0)], lw=lw))
        self.segments.append(Segment([(lead + 2 * radius, 0), (length, 0)], lw=lw))

        self.segments.append(SegmentCircle((cx, 0), radius=radius, lw=lw))

        # arrow (triangle) pointing up inside circle
        arrow = [(cx, 0.18), (cx - 0.12, -0.05), (cx + 0.12, -0.05)]
        self.segments.append(SegmentPoly(arrow, closed=True, lw=lw))
        self.segments.append(Segment([(cx, -0.18), (cx, 0.05)], lw=lw))

        self.anchors["start"] = (0, 0)
        self.anchors["end"] = (length, 0)
