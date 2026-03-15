import math

import numpy as np
from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentCircle, SegmentBezier
from schemdraw import SegmentArc, util

gap = (math.nan, math.nan)


class ACSourceCustom(Element):
    """
    AC source: circle with sine-like bezier inside.
    """

    # _element_defaults = {"sin_lw": None, "sin_color": None}

    def __init__(
        self, r=0.8, theta=180, circlelw=2, sin_lw=1.5, specificstyle=True, style=4
    ):
        super().__init__()
        if specificstyle == True:
            if style == 2:
                self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))
                self.segments.append(SegmentCircle((0.5, 0), 0.45, lw=2.2))
                self.elmparams["theta"] = 180

                cx, cy = 0.5, 0.0

                # Keep the wave comfortably inside the circle
                wave_half_width = 0.25  # controls left-right span
                wave_amp = 0.15  # controls up-down amplitude

                # x goes left -> right
                xs = np.linspace(cx - wave_half_width, cx + wave_half_width, 120)

                # one full sine cycle
                ys = [
                    cy
                    + wave_amp
                    * math.sin(
                        2
                        * math.pi
                        * (x - (cx - wave_half_width))
                        / (2 * wave_half_width)
                    )
                    for x in xs
                ]

                self.segments.append(
                    Segment(
                        list(zip(xs, ys)),
                        lw=2.2,
                        capstyle="butt",
                    )
                )
            elif style == 1:
                """if using arc"""
                # 左右各半段
                self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))
                self.segments.append(SegmentCircle((0.5, 0), 0.4, lw=2.5))
                self.elmparams["theta"] = 180

                cx, cy = 0.5, 0.0
                self.segments.append(
                    SegmentArc(
                        (cx + 0.12, cy),
                        width=0.24,
                        height=0.24,
                        theta1=180,
                        theta2=0,
                        lw=2.5,
                    )
                )

                # 右半个拱：向下
                self.segments.append(
                    SegmentArc(
                        (cx - 0.12, cy),
                        width=0.24,
                        height=-0.24,
                        theta1=180,
                        theta2=0,
                        lw=2.5,
                    )
                )
            elif style == 3:
                """if using square"""
                # 左右各半段
                self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))
                self.segments.append(SegmentCircle((0.5, 0), 0.45, lw=2.2))
                self.elmparams["theta"] = 0
                self.segments.append(
                    Segment(
                        [
                            (0.35, -0.18),
                            (0.35, 0.18),
                            (0.5, 0.18),
                            (0.5, -0.18),
                            (0.65, -0.18),
                            (0.65, 0.18),
                        ],
                        lw=2,
                        capstyle="round",
                    )
                )
            elif style == 4:
                self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))
                self.segments.append(SegmentCircle((0.5, 0), 0.45, lw=1.5))
                self.elmparams["theta"] = 180

                cx, cy = 0.5, 0.0

                # Keep the wave comfortably inside the circle
                wave_half_width = 0.32  # controls left-right span
                wave_amp = 0.21  # controls up-down amplitude

                # x goes left -> right
                xs = np.linspace(cx - wave_half_width, cx + wave_half_width, 120)

                # one full sine cycle
                ys = [
                    cy
                    + wave_amp
                    * math.sin(
                        2
                        * math.pi
                        * (x - (cx - wave_half_width))
                        / (2 * wave_half_width)
                    )
                    for x in xs
                ]

                self.segments.append(
                    Segment(
                        list(zip(xs, ys)),
                        lw=1.5,
                        capstyle="round",
                    )
                )

        else:
            self.segments.append(Segment([(0, 0), (0, 0), gap, (1, 0), (1, 0)]))
            self.segments.append(SegmentCircle((0.5, 0), r, lw=circlelw))
            self.elmparams["theta"] = theta

            sin_y = util.linspace(-0.25, 0.25, num=25)
            sin_x = [
                0.2 * math.sin((sy - 0.25) * math.pi * 2 / 0.5) + 0.5 for sy in sin_y
            ]
            self.segments.append(Segment(list(zip(sin_x, sin_y)), lw=sin_lw))
