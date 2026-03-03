from schemdraw.elements import Element
from schemdraw.segments import Segment


class NMosCustom(Element):
    """
    Simplified NMOS symbol.
    Anchors:
      - drain (left)
      - source (right)
      - gate (bottom)
    Also provides start/end as drain/source for compatibility.
    """

    def __init__(self, length=2.4, body_h=0.6, gate_len=0.6, lw=1.5):
        super().__init__()
        # layout: drain --- [channel] --- source, gate from bottom
        x0 = 0.0
        x1 = 0.7
        x2 = length - 0.7
        x3 = length
        y = body_h / 2

        # drain lead
        self.segments.append(Segment([(x0, 0), (x1, 0)], lw=lw))
        # source lead
        self.segments.append(Segment([(x2, 0), (x3, 0)], lw=lw))

        # channel (two parallel vertical-ish lines)
        self.segments.append(Segment([(x1, -y), (x1, y)], lw=lw))
        self.segments.append(Segment([(x2, -y), (x2, y)], lw=lw))
        # connect top/bottom between them (box-ish)
        self.segments.append(Segment([(x1, y), (x2, y)], lw=lw))
        self.segments.append(Segment([(x1, -y), (x2, -y)], lw=lw))

        # gate line coming from bottom to near channel
        gx = (x1 + x2) / 2
        self.segments.append(Segment([(gx, -y - gate_len), (gx, -y)], lw=lw))
        # small gap to indicate insulated gate (optional tiny offset)
        self.segments.append(Segment([(gx - 0.18, -y), (gx + 0.18, -y)], lw=lw))

        self.anchors["drain"] = (x0, 0)
        self.anchors["source"] = (x3, 0)
        self.anchors["gate"] = (gx, -y - gate_len)

        self.anchors["start"] = self.anchors["drain"]
        self.anchors["end"] = self.anchors["source"]
