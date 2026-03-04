from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentArc
from schemdraw.elements.twoterm import cycloid


class InductorCustom(Element):
    """
    Inductor drawn as cycloid (loopy), like schemdraw's built-in Inductor2,
    but scaled to custom length and with leads.
    """

    # _element_defaults = {
    #     "core_ls": None,
    #     "core_lw": None,
    #     "core_color": None,
    # }

    def __init__(
        self,
        loops=4,  # 多少个线圈
        lw=1.5,  # inductor line width
        corelw=1,  # core line width
        # lead=0.55,
        a=0.06,  # cycloid a
        b=0.19,  # cycloid b
        type: int = 2,
        core: int = 1,  # number of core
        coregap: float = 0.12,
        coreofst: float = 0.5,
        ind_w=0.75,  # 单个长度
        **kwargs
    ):
        super().__init__(**kwargs)
        # ind_w = 0.25
        # coregap = 0.12
        # coreofst = 0.5
        length = loops * ind_w
        if type == 1:

            self.segments.append(Segment(cycloid(loops=loops, a=a, b=b), lw=lw))
            if core > 0:
                for i in range(core):
                    y = coreofst + coregap * i
                    self.segments.append(
                        Segment(
                            [(0, y), (length, y)],
                            lw=corelw,
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
                        lw=lw,
                    )
                )

            if core > 0:
                for i in range(core):
                    y = ind_w + coregap * i
                    self.segments.append(
                        Segment(
                            [(0, y), (length, y)],
                            # ls=self.params["core_ls"],
                            lw=corelw,
                            # color=self.params["core_color"],
                        )
                    )
