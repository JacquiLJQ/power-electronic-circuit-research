from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentPoly


class ResistorCustom(Element):
    """
    Simple zigzag resistor (ANSI-like), start/end anchors for wiring.
    """

    def __init__(self, length=2.0, amp=0.3, zigs=4, lw=1.5):
        super().__init__()
        if zigs < 2:
            zigs = 2

        lead = 0.5
        body_len = max(0.2, length - 2 * lead)
        step = body_len / (2 * zigs)

        # left lead
        self.segments.append(Segment([(0, 0), (lead, 0)], lw=lw))

        # zigzag body
        pts = [(lead, 0)]
        x = lead
        up = True
        for _ in range(2 * zigs):
            x += step
            y = amp if up else -amp
            pts.append((x, y))
            up = not up
        pts.append((lead + body_len, 0))
        self.segments.append(SegmentPoly(pts, lw=lw))

        # right lead
        self.segments.append(Segment([(lead + body_len, 0), (length, 0)], lw=lw))

        self.anchors["start"] = (0, 0)
        self.anchors["end"] = (length, 0)
