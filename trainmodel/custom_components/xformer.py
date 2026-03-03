from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentArc


class TransformerCustom(Element):
    """
    Simple transformer: two inductive coils facing each other.
    start/end are primary left/right for simple inline use.
    For richer wiring, anchors: p1, p2, s1, s2 (top/bottom).
    """

    def __init__(self, width=2.8, loops=3, radius=0.16, gap=0.35, lw=1.5):
        super().__init__()
        # We'll provide 4 terminals: primary top/bottom at left, secondary top/bottom at right
        # Coordinates
        left_x = 0.0
        right_x = width
        coil_w = 0.8
        mid = width / 2

        # terminal y positions
        yt = 0.45
        yb = -0.45

        # primary terminals to coil
        p_coil_x = mid - gap / 2 - coil_w
        self.segments.append(Segment([(left_x, yt), (p_coil_x, yt)], lw=lw))
        self.segments.append(Segment([(left_x, yb), (p_coil_x, yb)], lw=lw))

        # secondary terminals to coil
        s_coil_x = mid + gap / 2 + coil_w
        self.segments.append(Segment([(s_coil_x, yt), (right_x, yt)], lw=lw))
        self.segments.append(Segment([(s_coil_x, yb), (right_x, yb)], lw=lw))

        # coils: draw arcs between yb..yt, centered around their coil area
        # primary coil arcs (facing right)
        pitch = (yt - yb) / (loops + 1)
        for i in range(loops):
            cy = yb + (i + 1) * pitch
            self.segments.append(
                SegmentArc(
                    center=(p_coil_x + coil_w * 0.6, cy),
                    width=2 * radius,
                    height=2 * radius,
                    theta1=90,
                    theta2=-90,
                    lw=lw,
                )
            )

        # secondary coil arcs (facing left)
        for i in range(loops):
            cy = yb + (i + 1) * pitch
            self.segments.append(
                SegmentArc(
                    center=(s_coil_x - coil_w * 0.6, cy),
                    width=2 * radius,
                    height=2 * radius,
                    theta1=270,
                    theta2=90,
                    lw=lw,
                )
            )

        # optional core lines in the middle
        self.segments.append(
            Segment([(mid - 0.08, yb - 0.1), (mid - 0.08, yt + 0.1)], lw=lw)
        )
        self.segments.append(
            Segment([(mid + 0.08, yb - 0.1), (mid + 0.08, yt + 0.1)], lw=lw)
        )

        self.anchors["p1"] = (left_x, yt)
        self.anchors["p2"] = (left_x, yb)
        self.anchors["s1"] = (right_x, yt)
        self.anchors["s2"] = (right_x, yb)

        # compatibility inline anchors (not perfect transformer semantics, but convenient)
        self.anchors["start"] = self.anchors["p1"]
        self.anchors["end"] = self.anchors["s1"]
