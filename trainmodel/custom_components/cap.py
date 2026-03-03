from schemdraw.elements import Element
from schemdraw.segments import Segment


class CapacitorCustom(Element):
    """
    Two-plate capacitor.
    """

    def __init__(self, length=2.0, gap=0.25, plate=0.6, lw=1.5):
        super().__init__()
        lead = (length - gap) / 2

        x1 = lead
        x2 = lead + gap
        y = plate / 2

        # leads
        self.segments.append(Segment([(0, 0), (x1, 0)], lw=lw))
        self.segments.append(Segment([(x2, 0), (length, 0)], lw=lw))

        # plates (vertical)
        self.segments.append(Segment([(x1, -y), (x1, y)], lw=lw))
        self.segments.append(Segment([(x2, -y), (x2, y)], lw=lw))

        self.anchors["start"] = (0, 0)
        self.anchors["end"] = (length, 0)
