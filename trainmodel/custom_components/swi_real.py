from __future__ import annotations
from typing import Optional

__all__ = [
    "Bjt",
    "Bjt2",
    "BjtNpn",
    "BjtNpn2",
    "BjtPnp",
    "BjtPnp2",
    "BjtPnp2c",
    "BjtPnp2c2",
    "JFet",
    "JFet2",
    "JFetN",
    "JFetN2",
    "JFetP",
    "JFetP2",
    "NFet",
    "NFet2",
    "NMos",
    "NMos2",
    "PFet",
    "PFet2",
    "PMos",
    "PMos2",
    "AnalogNFet",
    "AnalogPFet",
    "AnalogBiasedFet",
]

from schemdraw.elements import Element, Element2Term
from schemdraw.elements.elements import LabelHint, gap
from schemdraw.elements.twoterm import reswidth
from schemdraw.segments import Segment, SegmentPoly, SegmentCircle
from schemdraw.types import Point


class NMosCustom(Element):
    """
    Simplified NMOS symbol.
    Anchors:
      - drain (left)
      - source (right)
      - gate (bottom)
    Also provides start/end as drain/source for compatibility.
    """

    # def __init__(self, length=2.4, body_h=0.6, gate_len=0.6, lw=1.5):
    #     super().__init__()
    #     # layout: drain --- [channel] --- source, gate from bottom
    #     x0 = 0.0
    #     x1 = 0.7
    #     x2 = length - 0.7
    #     x3 = length
    #     y = body_h / 2

    #     # drain lead
    #     self.segments.append(Segment([(x0, 0), (x1, 0)], lw=lw))
    #     # source lead
    #     self.segments.append(Segment([(x2, 0), (x3, 0)], lw=lw))

    #     # channel (two parallel vertical-ish lines)
    #     self.segments.append(Segment([(x1, -y), (x1, y)], lw=lw))
    #     self.segments.append(Segment([(x2, -y), (x2, y)], lw=lw))
    #     # connect top/bottom between them (box-ish)
    #     self.segments.append(Segment([(x1, y), (x2, y)], lw=lw))
    #     self.segments.append(Segment([(x1, -y), (x2, -y)], lw=lw))

    #     # gate line coming from bottom to near channel
    #     gx = (x1 + x2) / 2
    #     self.segments.append(Segment([(gx, -y - gate_len), (gx, -y)], lw=lw))
    #     # small gap to indicate insulated gate (optional tiny offset)
    #     self.segments.append(Segment([(gx - 0.18, -y), (gx + 0.18, -y)], lw=lw))

    #     self.anchors["drain"] = (x0, 0)
    #     self.anchors["source"] = (x3, 0)
    #     self.anchors["gate"] = (gx, -y - gate_len)

    #     self.anchors["start"] = self.anchors["drain"]
    #     self.anchors["end"] = self.anchors["source"]
    _element_defaults = {"diode": False, "circle": False}
    __variants = ["nmos", "pmos"]

    def __init__(
        self,
        variant: str = "nmos",
        *,
        diode: Optional[bool] = False,
        circle: Optional[bool] = False,
        **kwargs,
    ):
        if variant not in self.__variants:
            raise ValueError(
                "Parameter 'variant' must be one of {}, not {}.".format(
                    self.__variants, variant
                )
            )

        super().__init__(**kwargs)
        self.elmparams["ilabel"] = "right"  # Draw current labels on this side
        u = reswidth * 0.5

        self.segments.extend(
            [
                Segment([(-3 * u, -6.5 * u), (-3 * u, -7.5 * u)]),
                Segment([(-3 * u, -9.5 * u), (-3 * u, -10.5 * u)]),
                Segment([(-3 * u, -12.5 * u), (-3 * u, -13.5 * u)]),
            ]
        )

        # top lead
        self.segments.extend(
            [
                Segment([(0, -7 * u), (0, 0)]),
                Segment([(-3 * u, -7 * u), (0, -7 * u)]),
            ]
        )

        # bottom lead
        self.segments.extend(
            [
                Segment([(0, -20 * u), (0, -13 * u)]),
                Segment([(-3 * u, -13 * u), (0, -13 * u)]),
            ]
        )

        if variant == "nmos":
            # gate
            self.segments.extend(
                [
                    Segment([(-10 * u, -14 * u), (-5 * u, -14 * u)]),
                    Segment([(-5 * u, -14 * u), (-5 * u, -6 * u)]),
                ]
            )
            # source
            self.segments.extend(
                [
                    Segment(
                        [(-3 * u, -10 * u), (0, -10 * u)],
                        arrow="<-",
                        arrowwidth=2 * u,
                        arrowlength=2 * u,
                    ),
                    Segment([(0, -10 * u), (0, -13 * u)]),
                ]
            )

            self.anchors["drain"] = (0, 0)
            self.anchors["gate"] = (-10 * u, -14 * u)
            self.anchors["center"] = (0, -10 * u)
            self.anchors["source"] = (0, -20 * u)

        elif variant == "pmos":
            # gate
            self.segments.extend(
                [
                    Segment([(-10 * u, -6 * u), (-5 * u, -6 * u)]),
                    Segment([(-5 * u, -6 * u), (-5 * u, -14 * u)]),
                ]
            )
            # source
            self.segments.extend(
                [
                    Segment(
                        [(-3 * u, -10 * u), (0, -10 * u)],
                        arrow="->",
                        arrowwidth=2 * u,
                        arrowlength=2 * u,
                    ),
                    Segment([(0, -10 * u), (0, -7 * u)]),
                ]
            )

            self.anchors["source"] = (0, 0)
            self.anchors["gate"] = (-10 * u, -6 * u)
            self.anchors["center"] = (0, -10 * u)
            self.anchors["drain"] = (0, -20 * u)

        # self.anchors["start"] = self.anchors["drain"]
        # self.anchors["end"] = self.anchors["source"]
        # self.elmparams["drop"] = (0, -20 * u)
        # self.elmparams["lblloc"] = "rgt"

        if self.params["diode"]:
            self.segments.extend(
                [
                    Segment([(0, -7 * u), (3 * u, -7 * u)]),
                    Segment([(3 * u, -7 * u), (3 * u, -9 * u)]),
                    Segment([(2 * u, -9 * u), (4 * u, -9 * u)]),
                    SegmentPoly([(3 * u, -9 * u), (2 * u, -11 * u), (4 * u, -11 * u)]),
                    Segment([(3 * u, -11 * u), (3 * u, -13 * u)]),
                    Segment([(3 * u, -13 * u), (0, -13 * u)]),
                ]
            )

        if self.params["circle"]:
            self.segments.append(SegmentCircle((-1 * u, -10 * u), 7 * u))
