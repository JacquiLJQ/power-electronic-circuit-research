from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentArc
from schemdraw.elements.twoterm import cycloid


# class InductorCustom(Element):
#     """
#     Inductor as a series of arcs ("loops").
#     """

#     def __init__(self, length=2.0, loops=4, radius=0.18, lw=1.5):
#         super().__init__()
#         if loops < 2:
#             loops = 2

#         lead = 0.5
#         body_len = max(0.4, length - 2 * lead)
#         pitch = body_len / loops

#         # leads
#         self.segments.append(Segment([(0, 0), (lead, 0)], lw=lw))
#         self.segments.append(Segment([(lead + body_len, 0), (length, 0)], lw=lw))

#         # arcs centered along body
#         x0 = lead + pitch / 2
#         for i in range(loops):
#             cx = x0 + i * pitch
#             # arc from left to right (semi-circle up)
#             self.segments.append(
#                 SegmentArc(
#                     center=(cx, 0),
#                     width=2 * radius,
#                     height=2 * radius,
#                     theta1=180,
#                     theta2=0,
#                     lw=lw,
#                 )
#             )


#         self.anchors["start"] = (0, 0)
#         self.anchors["end"] = (length, 0)
class InductorCustom(Element):
    """
    Inductor drawn as cycloid (loopy), like schemdraw's built-in Inductor2,
    but scaled to custom length and with leads.
    """

    _element_defaults = {
        "core_ls": None,
        "core_lw": None,
        "core_color": None,
    }

    def __init__(
        self,
        length=2.6,
        loops=4,
        lw=1.5,
        lead=0.55,
        type: int = 2,
        core: int = 1,
        **kwargs
    ):
        super().__init__(**kwargs)
        ind_w = 0.25
        coregap = 0.12
        coreofst = 0.5
        if type == 1:
            # body_len = max(0.4, length - 2 * lead)
            # x0 = lead
            # # x1 = lead + body_len

            # # leads
            # # self.segments.append(Segment([(0, 0), (x0, 0)], lw=lw))
            # # self.segments.append(Segment([(x1, 0), (length, 0)], lw=lw))

            # # cycloid path is in x=[0,1] roughly; scale to x=[x0,x1]
            # pts01 = cycloid(loops=loops)  # list of (x,y)
            # pts = [(x0 + p[0] * body_len, p[1]) for p in pts01]

            # self.segments.append(Segment(pts, lw=lw))

            # self.anchors["start"] = (0, 0)
            # self.anchors["end"] = (length, 0)
            self.segments.append(Segment(cycloid(loops=loops)))
            if core > 0:
                for i in range(core):
                    y = coreofst + coregap * i
                    self.segments.append(
                        Segment(
                            [(0, y), (1, y)],
                            ls=self.params["core_ls"],
                            lw=self.params["core_lw"],
                            color=self.params["core_color"],
                        )
                    )
        if type == 2:

            for i in range(loops):
                self.segments.append(
                    SegmentArc(
                        ((i * 2 + 1) * ind_w / 2, 0),
                        theta1=0,
                        theta2=180,
                        width=ind_w,
                        height=ind_w,
                    )
                )

            if core > 0:
                for i in range(core):
                    y = ind_w + coregap * i
                    self.segments.append(
                        Segment(
                            [(0, y), (1, y)],
                            ls=self.params["core_ls"],
                            lw=self.params["core_lw"],
                            color=self.params["core_color"],
                        )
                    )
