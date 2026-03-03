from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentBezier


class ACSourceCustom(Element):
    """
    AC source: circle with sine-like bezier inside.
    """

    def __init__(self, length=2.2, radius=0.35, lw=1.5):
        super().__init__()
        lead = (length - 2 * radius) / 2
        cx = lead + radius

        self.segments.append(Segment([(0, 0), (lead, 0)], lw=lw))
        self.segments.append(Segment([(lead + 2 * radius, 0), (length, 0)], lw=lw))

        self.segments.append(SegmentCircle((cx, 0), radius=radius, lw=lw))

        # sine-ish curve inside circle using a cubic bezier chain (2 segments)
        # left half
        self.segments.append(
            SegmentBezier(
                [(cx - 0.22, 0), (cx - 0.11, 0.18), (cx - 0.11, -0.18), (cx, 0)], lw=lw
            )
        )
        # right half
        self.segments.append(
            SegmentBezier(
                [(cx, 0), (cx + 0.11, 0.18), (cx + 0.11, -0.18), (cx + 0.22, 0)], lw=lw
            )
        )

        self.anchors["start"] = (0, 0)
        self.anchors["end"] = (length, 0)
