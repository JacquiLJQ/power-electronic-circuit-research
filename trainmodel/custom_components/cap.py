import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentArc, SegmentText

# height = 0.25  # original Resistor height

gap = (math.nan, math.nan)


class CapacitorCustom(Element):
    """
    Two-plate capacitor.
    """

    def __init__(
        self,
        *,
        polar: bool = False,  # 是否加正负极符号
        type: int = 2,  # 型号
        height=0.25,  # cap高度
        capgap=0.2,  # cap中间的间隙
        caplw=2,  # cap的画线宽度
        specificstyle=True,
        style=1,
        **kwargs
    ):
        super().__init__(**kwargs)
        if specificstyle == True:
            if style == 1:
                # left plate
                self.segments.append(
                    Segment([(-0.12, -0.33), (-0.12, 0.33)], lw=3.5, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.12, -0.33), (0.12, 0.33)], lw=3.5, capstyle="butt")
                )
            elif style == 2:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.32, 0.12), (0.32, 0.12)], lw=5, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.32, -0.12), (0.32, -0.12)], lw=5, capstyle="butt")
                )
            elif style == 3:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.32, 0.1), (0.32, 0.1)], lw=3.5, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.32, -0.11), (0.32, -0.11)], lw=5, capstyle="butt")
                )
            elif style == 4:
                # left plate
                self.segments.append(
                    Segment([(-0.11, -0.33), (-0.11, 0.33)], lw=5, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.12, -0.33), (0.12, 0.33)], lw=3.6, capstyle="butt")
                )
            elif style == 5:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.32, 0.12), (0.32, 0.12)], lw=4, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.32, -0.12), (0.32, -0.12)], lw=4, capstyle="butt")
                )
            elif style == 6:
                # left plate
                self.segments.append(
                    Segment([(-0.11, -0.33), (-0.11, 0.33)], lw=3.6, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.12, -0.33), (0.12, 0.33)], lw=5, capstyle="butt")
                )
            elif style == 7:
                # top plate
                self.segments.append(
                    Segment([(-0.31, 0.12), (0.31, 0.12)], lw=2.5, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.33, 0.12), (0.32, 0.12)], lw=0.8, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.26),
                        width=0.62,
                        height=0.5,
                        theta1=20,
                        theta2=160,
                        lw=2,
                    )
                )
            elif style == 8:
                # top plate
                self.segments.append(
                    Segment([(-0.31, 0.12), (0.31, 0.12)], lw=2.5, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.26),
                        width=0.62,
                        height=0.5,
                        theta1=20,
                        theta2=160,
                        lw=2,
                    )
                )
            elif style == 9:
                # top plate

                self.segments.append(
                    Segment([(-0.16, 0.22), (-0.16, -0.22)], lw=2.2, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.16, 0.23), (-0.16, -0.23)], lw=0.8, capstyle="butt")
                )

                # curved plate
                self.segments.append(
                    SegmentArc(
                        (0.13, 0),
                        width=0.34,
                        height=0.46,
                        theta1=110,
                        theta2=250,
                        lw=1.8,
                    )
                )
            elif style == 10:
                # top plate

                self.segments.append(
                    Segment([(0.16, 0.22), (0.16, -0.22)], lw=2.2, capstyle="butt")
                )
                self.segments.append(
                    Segment([(0.16, 0.23), (0.16, -0.23)], lw=0.8, capstyle="butt")
                )

                # left curved plate
                self.segments.append(
                    SegmentArc(
                        (-0.12, 0),
                        width=0.30,
                        height=0.46,
                        theta1=-75,
                        theta2=75,
                        lw=1.8,
                    )
                )
            elif style == 11:
                # top plate
                self.segments.append(
                    Segment([(-0.28, 0.12), (0.28, 0.12)], lw=2.5, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.26),
                        width=0.56,
                        height=0.5,
                        theta1=20,
                        theta2=160,
                        lw=2,
                    )
                )
            elif style == 12:
                # top plate
                self.segments.append(
                    Segment([(-0.28, -0.12), (0.28, -0.12)], lw=2.5, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.29, -0.12), (0.29, -0.12)], lw=0.8, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, 0.26),
                        width=0.56,
                        height=0.5,
                        theta1=200,
                        theta2=340,
                        lw=2,
                    )
                )
            elif style == 13:
                # top plate
                self.segments.append(
                    Segment([(-0.28, -0.12), (0.28, -0.12)], lw=2.5, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, 0.26),
                        width=0.56,
                        height=0.5,
                        theta1=200,
                        theta2=340,
                        lw=2,
                    )
                )
            elif style == 14:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.28, 0.09), (0.28, 0.09)], lw=2, capstyle="round")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.28, -0.1), (0.28, -0.1)], lw=2, capstyle="round")
                )
            elif style == 15:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.28, 0.09), (0.28, 0.09)], lw=2, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.28, -0.1), (0.28, -0.1)], lw=2, capstyle="butt")
                )
            elif style == 16:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.25, 0.09), (0.25, 0.09)], lw=2, capstyle="round")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.25, -0.1), (0.25, -0.1)], lw=2, capstyle="round")
                )
            elif style == 17:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.25, 0.09), (0.25, 0.09)], lw=2, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.25, -0.1), (0.25, -0.1)], lw=2, capstyle="butt")
                )
            elif style == 18:
                # left plate
                self.segments.append(
                    Segment([(-0.1, -0.25), (-0.1, 0.25)], lw=2, capstyle="round")
                )

                # right plate
                self.segments.append(
                    Segment([(0.1, -0.25), (0.1, 0.25)], lw=2, capstyle="round")
                )
            elif style == 19:
                # left plate
                self.segments.append(
                    Segment([(-0.09, -0.25), (-0.09, 0.25)], lw=2, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.1, -0.25), (0.1, 0.25)], lw=2, capstyle="butt")
                )
            elif style == 20:
                # left plate
                self.segments.append(
                    Segment([(0, -0.22), (0, 0.22)], lw=1, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.09, -0.22), (0.09, 0.22)], lw=1, capstyle="butt")
                )
            elif style == 21:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.25, 0.15), (0.25, 0.15)], lw=2, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.25, -0.1), (0.25, -0.1)], lw=2, capstyle="butt")
                )
            elif style == 22:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.25, 0.01), (0.25, 0.01)], lw=1, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.25, -0.1), (0.25, -0.1)], lw=2, capstyle="butt")
                )
            elif style == 23:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.25, 0.01), (0.25, 0.01)], lw=2, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.25, -0.1), (0.25, -0.1)], lw=2, capstyle="butt")
                )
            elif style == 24:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.25, 0.01), (0.25, 0.01)], lw=1, capstyle="round")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.25, -0.1), (0.25, -0.1)], lw=2, capstyle="round")
                )
            elif style == 25:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.25, 0.01), (0.25, 0.01)], lw=2, capstyle="round")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.25, -0.1), (0.25, -0.1)], lw=2, capstyle="round")
                )
            elif style == 26:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.29, 0), (0.29, 0)], lw=0.5, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.29, -0.1), (0.29, -0.1)], lw=0.8, capstyle="butt")
                )
            elif style == 27:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.29, 0), (0.29, 0)], lw=0.8, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.29, -0.1), (0.29, -0.1)], lw=0.5, capstyle="butt")
                )
            elif style == 28:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.32, 0), (0.32, 0)], lw=1, capstyle="round")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.32, -0.17), (0.32, -0.17)], lw=1, capstyle="round")
                )
            elif style == 29:
                # top plate
                self.segments.append(
                    Segment([(-0.27, 0.12), (0.27, 0.12)], lw=2, capstyle="round")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.28),
                        width=0.56,
                        height=0.50,
                        theta1=20,
                        theta2=160,
                        lw=2,
                    )
                )
            elif style == 30:
                # top plate
                self.segments.append(
                    Segment([(-0.26, 0.12), (0.26, 0.12)], lw=2, capstyle="round")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.31),
                        width=0.6,
                        height=0.50,
                        theta1=30,
                        theta2=150,
                        lw=2,
                    )
                )
            elif style == 31:
                # left plate
                self.segments.append(
                    Segment([(0, -0.22), (0, 0.22)], lw=2, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.1, -0.22), (0.1, 0.22)], lw=1.8, capstyle="butt")
                )
            elif style == 32:
                # left plate
                self.segments.append(
                    Segment([(0, -0.22), (0, 0.22)], lw=1.8, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.1, -0.22), (0.1, 0.22)], lw=2, capstyle="butt")
                )

            elif style == 33:
                # left plate
                self.segments.append(
                    Segment([(0, -0.25), (0, 0.25)], lw=1.8, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.28, -0.25), (0.28, 0.25)], lw=1.8, capstyle="butt")
                )
            elif style == 34:
                # top plate
                self.segments.append(
                    Segment([(-0.26, 0.12), (0.26, 0.12)], lw=2, capstyle="round")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.28),
                        width=0.6,
                        height=0.50,
                        theta1=30,
                        theta2=150,
                        lw=2,
                    )
                )
            elif style == 35:
                # top plate
                self.segments.append(
                    Segment([(-0.3, 0.12), (0.3, 0.12)], lw=3, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.3),
                        width=0.8,
                        height=0.6,
                        theta1=30,
                        theta2=150,
                        lw=3,
                    )
                )
            elif style == 36:
                # top plate
                self.segments.append(
                    Segment([(-0.24, 0.12), (0.24, 0.12)], lw=1.8, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.24),
                        width=0.5,
                        height=0.5,
                        theta1=30,
                        theta2=150,
                        lw=1.8,
                    )
                )
            elif style == 37:
                # top plate
                self.segments.append(
                    Segment([(-0.24, 0.18), (0.24, 0.18)], lw=1.8, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.24),
                        width=0.5,
                        height=0.5,
                        theta1=30,
                        theta2=150,
                        lw=1.8,
                    )
                )
            elif style == 38:
                self.segments.append(
                    Segment([(-0.24, -0.18), (0.24, -0.18)], lw=1.8, capstyle="butt")
                )

                # top arc
                self.segments.append(
                    SegmentArc(
                        (0, 0.24),
                        width=0.5,
                        height=0.5,
                        theta1=210,
                        theta2=330,
                        lw=1.8,
                    )
                )
            elif style == 39:
                # top plate
                self.segments.append(
                    Segment([(-0.3, 0.12), (0.3, 0.12)], lw=1, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.28),
                        width=0.8,
                        height=0.6,
                        theta1=30,
                        theta2=150,
                        lw=1,
                    )
                )
            elif style == 40:
                # left plate
                self.segments.append(
                    Segment([(-0.12, -0.3), (-0.12, 0.3)], lw=1, capstyle="butt")
                )

                # right arc
                self.segments.append(
                    SegmentArc(
                        (0.28, 0),
                        width=0.56,
                        height=0.8,
                        theta1=120,
                        theta2=240,
                        lw=1,
                    )
                )
            elif style == 41:
                # top plate (thicker)
                self.segments.append(
                    Segment([(-0.18, 0.1), (0.18, 0.1)], lw=2, capstyle="butt")
                )

                # bottom plate
                self.segments.append(
                    Segment([(-0.18, -0.1), (0.18, -0.1)], lw=2, capstyle="butt")
                )
            elif style == 42:
                # top plate
                self.segments.append(
                    Segment([(-0.26, 0.12), (0.26, 0.12)], lw=1, capstyle="butt")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.4),
                        width=0.6,
                        height=0.75,
                        theta1=30,
                        theta2=150,
                        lw=1,
                    )
                )
            elif style == 43:
                # left plate
                self.segments.append(
                    Segment([(-0.07, -0.33), (-0.07, 0.33)], lw=1, capstyle="butt")
                )

                # right plate
                self.segments.append(
                    Segment([(0.1, -0.33), (0.1, 0.33)], lw=1, capstyle="butt")
                )
            elif style == 44:
                # top plate
                self.segments.append(
                    Segment([(-0.25, 0.12), (0.25, 0.12)], lw=2.5, capstyle="round")
                )

                # bottom arc
                self.segments.append(
                    SegmentArc(
                        (0, -0.3),
                        width=0.6,
                        height=0.6,
                        theta1=30,
                        theta2=150,
                        lw=2.5,
                    )
                )

        else:
            if type == 1:
                self.segments.append(
                    Segment(
                        [
                            (0, 0),
                            gap,
                            (0, height),
                            (0, -height),
                            gap,
                            (capgap, height),
                            (capgap, -height),
                            gap,
                            (capgap, 0),
                        ],
                        lw=caplw,
                    )
                )
            if type == 2:
                self.segments.append(
                    Segment(
                        [(0, 0), gap, (0, height), (0, -height), gap, (capgap, 0)],
                        lw=caplw,
                    )
                )
                self.segments.append(
                    SegmentArc(
                        (capgap * 1.5, 0),
                        width=capgap * 1.5,
                        height=height * 2.5,
                        theta1=105,
                        theta2=-105,
                        lw=caplw,
                    )
                )
            if polar == True:
                self.segments.append(SegmentText((-capgap * 1.2, capgap), "+"))
