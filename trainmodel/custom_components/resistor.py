# from schemdraw.elements import Element
# from schemdraw.segments import Segment, SegmentPoly


# class ResistorCustom(Element):
#     """
#     Simple zigzag resistor (ANSI-like), start/end anchors for wiring.
#     """

#     def __init__(
#         self,
#         length=2.0,
#         amp=0.3,  # 锯齿高度
#         zigs=4,  # 多少个锯齿
#         lw=1.5,  # 线条宽度
#         resheight=0.25,
#         reswidth=1 / 6,
#         **kwargs
#     ):
#         super().__init__(**kwargs)

#         self.segments.append(
#             Segment(
#                 [
#                     (0, 0),
#                     (0.5 * reswidth, resheight),
#                     (1.5 * reswidth, -resheight),
#                     (2.5 * reswidth, resheight),
#                     (3.5 * reswidth, -resheight),
#                     (4.5 * reswidth, resheight),
#                     (5.5 * reswidth, -resheight),
#                     (6 * reswidth, 0),
#                 ]
#             )
#         )
#         # if zigs < 1:
#         #     raise ValueError("zigs must be >= 1")

#         # dx = length / (2 * zigs)

#         # pts = []
#         # x = 0.0

#         # # start point
#         # pts.append((0.0, 0.0))

#         # y = amp
#         # for _ in range(2 * zigs):
#         #     x += dx
#         #     pts.append((x, y))
#         #     y = -y

#         # # force exact end on center line
#         # pts.append((length, 0.0))

#         # self.segments.append(Segment(pts, lw=lw))

#         # self.anchors["start"] = (0.0, 0.0)
#         # self.anchors["end"] = (length, 0.0)
from schemdraw.elements import Element
from schemdraw.segments import Segment


class ResistorCustom(Element):
    """
    Keep the original zigzag style (0.5, 1.5, 2.5 ...)*reswidth,
    but repeat according to `zigs`.
    No leads.
    """

    def __init__(
        self,
        zigs: int = 6,  # 多少个锯齿
        resheight: float = 0.5,  # 整体高度
        lw: float = 1.5,  # 线宽
        pointgapofst: float = -0.1,  # 每个尖尖的距离offset(可取负值缩短距离)
        **kwargs
    ):
        super().__init__(**kwargs)

        if zigs < 1:
            raise ValueError("zigs must be >= 1")

        reswidth: float = 1 / zigs + pointgapofst

        pts = [(0.0, 0.0)]

        # y alternates: +, -, +, -, ...
        y = resheight

        for i in range(2 * zigs - 2):
            x = (i + 0.5) * reswidth
            pts.append((x, y))
            y = -y

        # End on centerline at x = (2*zigs - 2) * reswidth
        x_end = (2 * zigs - 2) * reswidth
        pts.append((x_end, 0.0))

        self.segments.append(Segment(pts, lw=lw))
        self.anchors["start"] = (0.0, 0.0)
        self.anchors["end"] = (x_end, 0.0)
