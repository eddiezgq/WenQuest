# Fig. 17-5 (English): control system of a computerised flat knitting machine
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_w17_lib import *
s = S(1344, 898)
s.t(42, 42, 'The main controller decides “what each course does”; the carriage board decides “when each needle acts”', 20.5, INK, 700)
s.t(42, 78, 'Solid lines: commands and data; dashed lines: feedback. The carriage board travels with the carriage and talks to the main controller over the bus in the cable chain', 14.2, MUTED)
s.box(42, 131, 397, 460, BLUE, FBLUE, 2.6)
s.t(219, 165, 'Main controller', 18.5, INK, 700, 'middle')
for i, l in enumerate(['Parses the pattern program', 'Sends each course: direction, selection', 'data, stitch cam, carriers, racking,', 'take-down, speed']):
    s.t(219, 206 + 27 * i, l, 15, MUTED, anchor='middle')
s.t(219, 328, 'Reversal, protection and stop logic', 15, MUTED, anchor='middle')
s.t(219, 362, 'UI · pattern files · networking', 15, MUTED, anchor='middle')
s.t(219, 418, 'Computed once per course (~100 ms)', 14.5, MUTED, anchor='middle')
s.box(530, 131, 1300, 460, LINE, 'none', 1.6, 14, '8 6')
s.t(548, 155, 'Carriage (moves back and forth with it)', 15, MUTED)
s.box(566, 202, 813, 364, BLUE, FBLUE, 2.6)
s.t(690, 240, 'Carriage control board', 17.5, INK, 700, 'middle')
for i, l in enumerate(['FPGA position compare', 'triggers selection per needle', 'microsecond level']):
    s.t(690, 276 + 28 * i, l, 14.5, MUTED, anchor='middle')
for (y0, y1), lines in zip([(158, 237), (254, 332), (350, 428)], [['Electromagnetic', 'selectors × N'], ['Stitch-cam stepper motors'], ['Carrier and cam solenoids']]):
    s.box(990, y0, 1238, y1, ORANGE, FORANGE, 2.6)
    yc = (y0 + y1) / 2
    for i, l in enumerate(lines):
        s.t(1114, yc + (i - (len(lines) - 1) / 2) * 22, l, 16.5, INK, anchor='middle')
for y in (230, 294, 353):
    s.path([(813, y), (986, y)])
s.path([(397, 283), (562, 283)]); s.t(481, 262, 'Bus', 15, MUTED, anchor='middle')
for (x0, x1), l in zip([(78, 360), (433, 698), (751, 1016), (1078, 1290)], ['Carriage servo', 'Racking servo', 'Take-down motor', 'Yarn feeders']):
    s.box(x0, 527, x1, 604, LINE, '#ffffff', 2)
    s.t((x0 + x1) / 2, 565, l, 18, INK, anchor='middle')
s.path([(219, 460), (219, 523)])
s.curve((355, 447), (470, 470), (566, 524))
s.curve((397, 453), (660, 480), (880, 524))
s.curve((397, 438), (830, 460), (1184, 524))
s.path([(219, 604), (219, 670)], dash=True, arrow=False)
s.path([(99, 670), (672, 670)], dash=True, arrow=False)
s.path([(99, 670), (99, 464)], dash=True)
s.path([(672, 670), (672, 368)], dash=True)
s.t(123, 692, 'Carriage position x (encoder) → main controller and carriage board', 15, MUTED)
s.box(530, 742, 1300, 830, LINE, '#ffffff', 2)
s.t(915, 770, 'Protection sensors', 18, INK, anchor='middle')
s.t(915, 802, 'Yarn break · knots · needle crash · fabric lift-up · fabric roll-up · safety door', 14.5, MUTED, anchor='middle')
s.path([(530, 788), (318, 788), (318, 464)], dash=True)
s.t(42, 860, 'Racking acts when the carriage reverses and take-down tension is set per course; selection acts needle by needle while the carriage is moving,', 14.2, MUTED)
s.t(42, 884, 'so the two kinds of task are placed in different controllers', 14.2, MUTED)
s.h = 904
s.render('w_9028f6e2', 'Flat knitting machine control system')
