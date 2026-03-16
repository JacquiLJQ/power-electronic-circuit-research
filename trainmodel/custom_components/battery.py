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
        lw=1,
        specificstyle=True,
        style=1,
    ):
        super().__init__()
        if specificstyle == True:

            if style == 1:
                self.segments.append(
                    Segment([(-0.29, 0.35), (0.29, 0.35)], lw=1, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.13, 0.2), (0.13, 0.2)], lw=4, capstyle="butt")
                )

                # middle long plate
                self.segments.append(
                    Segment([(-0.29, 0.05), (0.29, 0.05)], lw=1, capstyle="butt")
                )

                # bottom thick bar
                self.segments.append(
                    Segment([(-0.13, -0.1), (0.13, -0.1)], lw=4, capstyle="butt")
                )
            elif style == 2:
                self.segments.append(
                    Segment([(-0.32, 0.35), (0.32, 0.35)], lw=3, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.16, 0.2), (0.16, 0.2)], lw=3, capstyle="butt")
                )

                # middle long plate
                self.segments.append(
                    Segment([(-0.32, 0.05), (0.32, 0.05)], lw=3, capstyle="butt")
                )

                # bottom thick bar
                self.segments.append(
                    Segment([(-0.16, -0.1), (0.16, -0.1)], lw=3, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.35, 0.35), (0.35, 0.35)], lw=0.8, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.18, 0.2), (0.18, 0.2)], lw=0.8, capstyle="butt")
                )

                # middle long plate
                self.segments.append(
                    Segment([(-0.35, 0.05), (0.35, 0.05)], lw=0.8, capstyle="butt")
                )

                # bottom thick bar
                self.segments.append(
                    Segment([(-0.18, -0.1), (0.18, -0.1)], lw=0.8, capstyle="butt")
                )
            elif style == 3:
                self.segments.append(
                    Segment([(-0.26, 0.35), (0.26, 0.35)], lw=2, capstyle="round")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.11, 0.15), (0.11, 0.15)], lw=2, capstyle="round")
                )
            elif style == 4:
                self.segments.append(
                    Segment([(-0.26, 0.35), (0.26, 0.35)], lw=2, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.11, 0.15), (0.11, 0.15)], lw=2, capstyle="butt")
                )
            elif style == 5:
                self.segments.append(
                    Segment([(-0.28, 0.24), (0.28, 0.24)], lw=2, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.13, 0.08), (0.13, 0.08)], lw=2, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.28, -0.08), (0.28, -0.08)], lw=2, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.13, -0.24), (0.13, -0.24)], lw=2, capstyle="butt")
                )
            elif style == 6:
                self.segments.append(
                    Segment([(-0.28, 0.24), (0.28, 0.24)], lw=2, capstyle="round")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.13, 0.08), (0.13, 0.08)], lw=2, capstyle="round")
                )
                self.segments.append(
                    Segment([(-0.28, -0.08), (0.28, -0.08)], lw=2, capstyle="round")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.13, -0.24), (0.13, -0.24)], lw=2, capstyle="round")
                )
            elif style == 7:
                self.segments.append(
                    Segment([(-0.32, 0.21), (0.32, 0.21)], lw=1.8, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.16, 0.07), (0.16, 0.07)], lw=1.8, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.32, -0.07), (0.32, -0.07)], lw=1.8, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.16, -0.21), (0.16, -0.21)], lw=1.8, capstyle="butt")
                )

            elif style == 8:
                self.segments.append(
                    Segment([(-0.46, 0.07), (0.46, 0.07)], lw=2, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.3, -0.09), (0.3, -0.09)], lw=2, capstyle="butt")
                )
            elif style == 9:
                self.segments.append(
                    Segment([(-0.35, 0.07), (0.35, 0.07)], lw=2, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.15, -0.09), (0.15, -0.09)], lw=2, capstyle="butt")
                )
            elif style == 10:
                self.segments.append(
                    Segment([(-0.46, 0.07), (0.46, 0.07)], lw=2, capstyle="round")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.3, -0.09), (0.3, -0.09)], lw=2, capstyle="round")
                )
            elif style == 11:
                self.segments.append(
                    Segment([(-0.35, 0.07), (0.35, 0.07)], lw=2, capstyle="round")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.15, -0.09), (0.15, -0.09)], lw=2, capstyle="round")
                )
            elif style == 12:
                self.segments.append(
                    Segment([(-0.24, 0.20), (0.24, 0.20)], lw=1, capstyle="round")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.10, 0), (0.10, 0)], lw=2.5, capstyle="round")
                )
            elif style == 13:
                self.segments.append(
                    Segment([(-0.28, 0.18), (0.28, 0.18)], lw=1, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.13, 0), (0.13, 0)], lw=2.3, capstyle="butt")
                )
            elif style == 14:
                self.segments.append(
                    Segment([(-0.29, 0.15), (0.29, 0.15)], lw=1, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.13, 0.06), (0.13, 0.06)], lw=2, capstyle="butt")
                )

                # middle long plate
                self.segments.append(
                    Segment([(-0.29, -0.05), (0.29, -0.05)], lw=1, capstyle="butt")
                )

                # bottom thick bar
                self.segments.append(
                    Segment([(-0.13, -0.15), (0.13, -0.15)], lw=2, capstyle="butt")
                )
            elif style == 15:
                self.segments.append(
                    Segment([(-0.36, 0.24), (0.36, 0.24)], lw=3, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.22, 0.12), (0.22, 0.12)], lw=3, capstyle="butt")
                )

                # middle long plate
                self.segments.append(
                    Segment([(-0.36, 0), (0.36, 0)], lw=3, capstyle="butt")
                )

                # bottom thick bar
                self.segments.append(
                    Segment([(-0.22, -0.12), (0.22, -0.12)], lw=3, capstyle="butt")
                )
            elif style == 16:
                self.segments.append(
                    Segment([(-0.36, 0.13), (0.36, 0.13)], lw=1.2, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.16, 0), (0.16, 0)], lw=2, capstyle="butt")
                )
            elif style == 17:
                self.segments.append(
                    Segment([(-0.3, 0.2), (0.3, 0.2)], lw=8, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.16, -0.1), (0.16, -0.1)], lw=8, capstyle="butt")
                )
            elif style == 18:
                self.segments.append(
                    Segment([(-0.26, 0.30), (0.26, 0.30)], lw=2, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.11, 0.15), (0.11, 0.15)], lw=2, capstyle="butt")
                )
            elif style == 19:
                self.segments.append(
                    Segment([(-0.31, 0.24), (0.31, 0.24)], lw=1, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.19, 0.12), (0.19, 0.12)], lw=1, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.31, 0), (0.31, 0)], lw=1, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.19, -0.12), (0.19, -0.12)], lw=1, capstyle="butt")
                )
            elif style == 20:
                self.segments.append(
                    Segment([(-0.31, 0.28), (0.31, 0.28)], lw=1, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.12, 0.14), (0.12, 0.14)], lw=1, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.31, 0), (0.31, 0)], lw=1, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.12, -0.14), (0.12, -0.14)], lw=1, capstyle="butt")
                )
            elif style == 21:
                self.segments.append(
                    Segment([(-0.3, 0.45), (0.3, 0.45)], lw=5.5, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.16, 0.25), (0.16, 0.25)], lw=5.5, capstyle="butt")
                )
                self.segments.append(
                    Segment([(-0.3, 0), (0.3, 0)], lw=5.5, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.16, -0.2), (0.16, -0.2)], lw=5.5, capstyle="butt")
                )
            elif style == 22:
                self.segments.append(
                    Segment([(-0.30, -0.18), (-0.30, 0.18)], lw=lw, capstyle="round")
                )

                # long
                self.segments.append(
                    Segment([(-0.18, -0.34), (-0.18, 0.34)], lw=lw, capstyle="round")
                )

                # short
                self.segments.append(
                    Segment([(-0.06, -0.18), (-0.06, 0.18)], lw=lw, capstyle="round")
                )

                # long
                self.segments.append(
                    Segment([(0.06, -0.34), (0.06, 0.34)], lw=lw, capstyle="round")
                )
            elif style == 23:
                self.segments.append(
                    Segment([(-0.46, 0.07), (0.46, 0.07)], lw=1, capstyle="butt")
                )

                # top thick bar (simulate filled block)
                self.segments.append(
                    Segment([(-0.3, -0.07), (0.3, -0.07)], lw=1, capstyle="butt")
                )
        else:

            if double:
                self.segments.append(Segment([(0, 0), gap, (batw * 3, 0)], lw=lw))
                self.segments.append(Segment([(0, bat1), (0, -bat1)], lw=lw))
                self.segments.append(Segment([(batw, bat2), (batw, -bat2)], lw=lw))
                self.segments.append(
                    Segment([(batw * 2, bat1), (batw * 2, -bat1)], lw=lw)
                )
                self.segments.append(
                    Segment([(batw * 3, bat2), (batw * 3, -bat2)], lw=lw)
                )
            else:
                self.segments.append(Segment([(0, 0), gap, (batw, 0)], lw=lw))
                self.segments.append(Segment([(0, bat1), (0, -bat1)], lw=lw))
                self.segments.append(Segment([(batw, bat2), (batw, -bat2)], lw=lw))
