import math

from schemdraw.elements import Element
from schemdraw.segments import Segment, SegmentArc, SegmentCircle

# sw_dot_r = 0.12

gap = (math.nan, math.nan)


class SwitchIdealCustom(Element):
    """
    Ideal switch: two contacts with a tilted blade (open switch).
    """

    _element_defaults = {
        "arrowwidth": 0.15,
        "arrowlength": 0.25,
        "arrow_lw": None,
        "arrow_color": None,
    }

    def __init__(
        self,
        action: str = "",
        contacts: bool = False,
        nc: bool = False,
        lead: float = 0.3,  # 引线长
        leadlw: float = 0.5,  # 引线线条宽
        switchlw: float = 1,  # 开关线条宽
        sw_dot_r: float = 0.12,  # 开关触点小圆的半径
        sw_dot_fill: bool = False,  # 是否开启开关触点小圆的fill
        sw_dot_fill_clr: str = "black",  # 开关触点小圆的颜色
        sw_dot_lw: float = 1,  # 触点小圆线条宽
        length: float = 0.9,  # 开关从左触点到右触点的距离
        blade_x_ratio: float = 1,  # 刀片顶点的相对 x 位置（原来 0.8 或 0.9
        blade_height: float = 0.2,  # 刀片抬起高度，决定开关张开程度
        **kwargs,
    ):
        super().__init__(**kwargs)
        xr = length
        blade_x = xr * blade_x_ratio
        blade_y = blade_height
        if contacts:
            if nc:
                self.segments.append(
                    Segment(
                        [
                            (0, 0),
                            gap,
                            (sw_dot_r * 2, 0),
                            (blade_x, sw_dot_r + 0.05),
                            gap,
                            (xr, 0),
                        ],
                        lw=switchlw,
                    )
                )
            else:
                self.segments.append(
                    Segment(
                        [
                            (0, 0),
                            gap,
                            (sw_dot_r * 2, 0.1),
                            (blade_x, blade_y),
                            gap,
                            (xr, 0),
                        ],
                        lw=switchlw,
                    )
                )
            self.segments.append(
                SegmentCircle(
                    (sw_dot_r, 0),
                    sw_dot_r,
                    fill=sw_dot_fill,
                    color=sw_dot_fill_clr,
                    zorder=3,
                    lw=sw_dot_lw,
                )
            )
            self.segments.append(
                SegmentCircle(
                    (xr - sw_dot_r, 0),
                    sw_dot_r,
                    fill=sw_dot_fill,
                    color=sw_dot_fill_clr,
                    zorder=3,
                    lw=sw_dot_lw,
                )
            )

        else:

            if nc:
                self.segments.append(
                    Segment(
                        [(0, 0), (xr + 0.15 * xr, blade_y), gap, (xr, 0)], lw=switchlw
                    )
                )
                self.segments.append(
                    Segment([(1, 0), (xr, blade_y + 0.1)], lw=switchlw)
                )
            else:
                self.segments.append(
                    Segment([(0, 0), (blade_x, blade_y), gap, (xr, 0)], lw=switchlw)
                )

        if lead and lead > 0:
            self.segments.append(Segment([(-lead, 0), (0, 0)], lw=leadlw))
            self.segments.append(Segment([(xr, 0), (xr + lead, 0)], lw=leadlw))

        if action == "open":
            self.segments.append(
                SegmentArc(
                    (xr * 0.4, blade_y * 0.25),
                    width=0.5,
                    height=0.75,
                    theta1=-10,
                    theta2=70,
                    arrow="ccw",
                    lw=self.params["arrow_lw"],
                    color=self.params["arrow_color"],
                    arrowwidth=self.params["arrowwidth"],
                    arrowlength=self.params["arrowlength"],
                )
            )
        if action == "close":
            self.segments.append(
                SegmentArc(
                    (xr * 0.4, blade_y * 0.25),
                    width=0.5,
                    height=0.75,
                    theta1=-10,
                    theta2=70,
                    arrow="cw",
                    lw=self.params["arrow_lw"],
                    color=self.params["arrow_color"],
                    arrowwidth=self.params["arrowwidth"],
                    arrowlength=self.params["arrowlength"],
                )
            )
