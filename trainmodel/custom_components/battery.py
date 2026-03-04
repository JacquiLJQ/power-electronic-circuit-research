import math

from schemdraw.elements import Element
from schemdraw.segments import Segment

resheight = 0.25  # Resistor height

batw = resheight * 0.75
bat1 = resheight * 1.5
bat2 = resheight * 0.75
gap = (math.nan, math.nan)


class BatteryCustom(Element):
    """
    Battery symbol: long plate + short plate.
    """

    def __init__(
        self,
        double=True,
        batw=0.1,
        bat1=0.3,
        bat2=0.2,
        # y1offset=0.5,  # 模拟手写倾斜效果
        # y2offset=0.5,
        lw=1,
    ):
        super().__init__()
        if double:
            self.segments.append(Segment([(0, 0), gap, (batw * 3, 0)], lw=lw))
            self.segments.append(Segment([(0, bat1), (0, -bat1)], lw=lw))
            self.segments.append(Segment([(batw, bat2), (batw, -bat2)], lw=lw))
            self.segments.append(Segment([(batw * 2, bat1), (batw * 2, -bat1)], lw=lw))
            self.segments.append(Segment([(batw * 3, bat2), (batw * 3, -bat2)], lw=lw))
        else:
            self.segments.append(Segment([(0, 0), gap, (batw, 0)], lw=lw))
            self.segments.append(Segment([(0, bat1), (0, -bat1)], lw=lw))
            self.segments.append(Segment([(batw, bat2), (batw, -bat2)], lw=lw))
