# -*- coding: utf-8 -*-
"""生成 E 部分“工装夹具”的条目（第 13 轮 8.7）：按下面的表写 catalog/E/<编号>/entry.yaml，可重复运行。

模型由 generators/e_fixture.py 调用 factory/digital/models3d 的函数生成（书中三维图、动画、工程图、数字工厂用的同一份）。
元件的结构型式参照 JB/T 8004–8045 机床夹具零件及部件标准的典型形式；尺寸是书中所用的那一个规格（示意比例），
不是标准尺寸表，设计时以标准为准。
    python3 library/tools/import_fixtures.py
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-10-05"
MFG = "机械制造技术"

# 参数：(键, 中文, 英文, 单位)
P = {
    "d": ("d", "直径 d", "Diameter d", "mm"), "D": ("D", "外径 D", "Outer diameter D", "mm"),
    "H": ("H", "高度 H", "Height H", "mm"), "L": ("L", "长度 L", "Length L", "mm"), "B": ("B", "宽度 B", "Width B", "mm"),
    "h": ("h", "工作段高 h", "Working height h", "mm"), "t": ("t", "厚度 t", "Thickness t", "mm"),
    "alpha": ("alpha", "V 形角 α", "V angle α", "°"), "apex": ("apex", "V 槽顶点离底面", "Apex above base", "mm"),
    "relief": ("relief", "中段退刀深", "Middle relief depth", "mm"), "kind": ("kind", "型式", "Type", ""),
    "b": ("b", "宽度 b", "Width b", "mm"), "e": ("e", "偏心距 e", "Eccentricity e", "mm"),
    "alpha_deg": ("alpha_deg", "楔角 α", "Wedge angle α", "°"), "h0": ("h0", "小端高 h₀", "Thin-end height h₀", "mm"),
    "r": ("r", "半径 r", "Radius r", "mm"), "reach": ("reach", "伸出长", "Reach", "mm"),
    "arm": ("arm", "压臂长", "Arm length", "mm"), "bore": ("bore", "缸径", "Bore", "mm"), "stroke": ("stroke", "行程", "Stroke", "mm"),
    "d_grip": ("d_grip", "夹持直径", "Gripping diameter", "mm"), "slots": ("slots", "开槽数", "Number of slots", ""),
    "size": ("size", "规格尺寸", "Size", "mm"), "D_bar": ("D_bar", "镗杆直径", "Boring-bar diameter", "mm"),
    "h_out": ("h_out", "伸出高度", "Protrusion", "mm"), "n": ("n", "分度数", "Divisions", ""),
    "pitch": ("pitch", "孔距", "Hole pitch", "mm"), "w": ("w", "T 形槽宽", "T-slot width", "mm"),
    "grip": ("grip", "夹持直径", "Gripping diameter", "mm"), "jaw_w": ("jaw_w", "钳口宽", "Jaw width", "mm"),
    "opening": ("opening", "钳口开度", "Jaw opening", "mm"), "taper": ("taper", "锥度", "Taper", ""),
    "half_angle": ("half_angle", "半锥角", "Half cone angle", "°"), "span": ("span", "两支点距", "Contact span", "mm"),
    "collar_d": ("collar_d", "台肩直径", "Collar diameter", "mm"), "lowered": ("lowered", "钻模板落下比例", "Plate lowered (0–1)", ""),
    "stations": ("stations", "工位数", "Stations", ""), "parts_per_face": ("parts_per_face", "每面工件数", "Parts per face", ""),
    "work_state": ("work_state", "工件状态", "Workpiece state", ""), "spacing": ("spacing", "状态间距", "Spacing", "mm"),
}

# (编号, 中文名, 英文名, 函数, {参数: 默认}, {固定参数}, 原理, [用途], [(章, 节名)], 结构型式参照)
E = [
    # ---------------- 定位元件
    ("E-LOC-SPINA", "支承钉（A 型平头）", "Rest button, flat head (type A)", "elements.support_pin", {"kind": "A", "d": 12.0, "H": 8.0}, {},
     "平头支承钉用于已加工过的精基准面，一个支承钉相当于一个支承点，限制工件沿其法向的一个移动自由度。三个支承钉组成主要支承面时，三点距离越大越稳。",
     ["精基准平面的点支承"], [(51, "常用定位元件"), (52, "定位元件")], "JB/T 8029.2 支承钉 A 型"),
    ("E-LOC-SPINB", "支承钉（B 型球头）", "Rest button, spherical head (type B)", "elements.support_pin", {"kind": "B", "d": 12.0, "H": 8.0}, {},
     "球头支承钉与工件近似点接触，用于未加工的粗基准面，接触位置稳定，但接触应力大、易磨损。",
     ["毛坯面（粗基准）的点支承"], [(51, "常用定位元件")], "JB/T 8029.2 支承钉 B 型"),
    ("E-LOC-SPINC", "支承钉（C 型网纹）", "Rest button, serrated head (type C)", "elements.support_pin", {"kind": "C", "d": 12.0, "H": 8.0}, {},
     "网纹顶面摩擦力大，多用于工件的侧面粗基准，防止工件在夹紧时滑移。",
     ["侧面粗基准的定位"], [(51, "常用定位元件")], "JB/T 8029.2 支承钉 C 型"),
    ("E-LOC-SPLATE", "支承板", "Rest plate", "elements.support_plate", {"kind": "A", "L": 80.0, "B": 20.0, "H": 12.0}, {"n": 2},
     "支承板用于精基准平面，一块窄长的支承板限制两个自由度（相当于两个支承点），两块组成一个平面。B 型带斜槽，切屑容易清除，用在侧面和顶面以外的位置。",
     ["精基准大平面的支承"], [(51, "常用定位元件"), (52, "定位元件")], "JB/T 8029.1 支承板"),
    ("E-LOC-ADJ", "可调支承", "Adjustable rest", "elements.adjustable_support", {"d": 12.0, "H": 30.0}, {},
     "高度可以调节、调好后用螺母锁紧的支承，用于毛坯尺寸变化较大的粗基准，每批毛坯调整一次，调好后作固定支承用，限制一个自由度。",
     ["毛坯尺寸变化大的粗基准"], [(51, "常用定位元件")], None),
    ("E-LOC-SELF", "自位支承", "Self-aligning rest", "locating.self_aligning_support", {"span": 30.0, "d": 10.0}, {},
     "两个或三个支点连在一个能浮动的杠杆上，与工件多点接触，但只起一个支承点的作用（限制一个自由度），用于提高刚度而不过定位。",
     ["粗基准、断续表面、刚度差的工件"], [(51, "常用定位元件")], None),
    ("E-LOC-AUX", "辅助支承（弹簧自位式）", "Auxiliary support (spring type)", "elements.auxiliary_support", {"d": 16.0}, {},
     "辅助支承不起定位作用：工件定位、夹紧之后，柱塞在弹簧作用下顶住工件，再用侧面的顶紧螺钉锁住，只为提高工件的刚度和稳定性。",
     ["工件悬伸部位的补充支承"], [(51, "常用定位元件"), (52, "定位元件")], None),
    ("E-LOC-PIN", "圆柱定位销", "Cylindrical locating pin", "elements.locating_pin", {"d": 16.0, "h": 12.0}, {"kind": "cyl"},
     "圆柱销插入工件的孔中定位：短销限制两个移动自由度，长销还限制两个转动自由度。与孔的配合常用 g6、f7，间隙是基准位移误差的来源。",
     ["以孔定位", "一面两销中的圆柱销"], [(51, "一面两销定位"), (52, "定位元件")], "JB/T 8014 定位销"),
    ("E-LOC-DPIN", "菱形销（削边销）", "Diamond pin", "elements.locating_pin", {"d": 16.0, "h": 12.0, "b": 4.0}, {"kind": "diamond", "flat_dir": "y"},
     "把圆柱销沿两孔连线的垂直方向削去两边，只在两孔连线方向留一段窄的圆柱面，补偿两孔中心距的误差，避免一面两销过定位，只限制工件绕圆柱销的转动。",
     ["一面两销中的菱形销"], [(51, "一面两销定位"), (52, "定位元件")], "JB/T 8014 定位销（菱形）"),
    ("E-LOC-VB", "V 形块", "V-block", "elements.vblock", {"alpha": 90.0, "B": 72.0, "L": 40.0, "H": 40.0, "apex": 14.0}, {},
     "外圆柱面放在 V 形块上定位，对中性好：外圆直径变化时，工件轴线只在 V 形块的对称平面内上下移动。长 V 形块限制四个自由度，短 V 形块限制两个。90° 最常用。",
     ["轴类零件外圆定位"], [(51, "V 形块定位的误差"), (52, "定位元件")], "JB/T 8018.1 V 形块"),
    ("E-LOC-SLEEVE", "定位套", "Locating sleeve", "locating.locating_sleeve", {"d": 40.0, "L": 40.0}, {},
     "工件的外圆插入定位套的孔中定位，结构简单，但有配合间隙，定心精度不如 V 形块和定心夹紧机构；长套限制四个自由度，短套限制两个。",
     ["外圆定位"], [(51, "常用定位元件")], None),
    ("E-LOC-HALF", "半圆孔定位座", "Half-bore locating seat", "locating.half_bore_seat", {"d": 60.0, "L": 50.0}, {},
     "下半个圆孔装在夹具体上作定位，上半个作盖板夹紧；用于大型轴类零件、不便从轴端插入定位套的场合。",
     ["大型轴的外圆定位"], [(51, "常用定位元件")], None),
    ("E-LOC-MANDREL", "圆柱心轴", "Cylindrical mandrel", "elements.mandrel", {"d": 30.0, "L": 60.0, "collar_d": 50.0}, {},
     "工件的孔套在心轴上、端面靠在台肩上定位，再用螺母压紧；间隙配合装卸方便，但有基准位移误差。",
     ["盘套类零件以孔定位车外圆、磨外圆"], [(51, "常用定位元件"), (52, "车床夹具")], None),
    ("E-LOC-TAPERMANDREL", "小锥度心轴", "Taper mandrel", "locating.taper_mandrel", {"d": 35.0, "L": 120.0, "taper": 0.001}, {},
     "锥度 1:1000～1:5000 的心轴，工件压上去后靠孔的弹性变形消除间隙，定心精度高，但轴向位置随孔径变化，只能承受较小的切削力。",
     ["精车、磨外圆的高精度定心"], [(51, "常用定位元件")], None),
    ("E-LOC-EXPMANDREL", "胀胎心轴", "Expanding mandrel", "locating.expanding_mandrel", {"d": 35.0, "L": 60.0, "slots": 6}, {},
     "开槽的弹性套在锥面推动下均匀胀开，把工件的孔撑紧，同时定心和夹紧，没有配合间隙。",
     ["以孔定心夹紧"], [(51, "常用定位元件"), (52, "定心夹紧机构")], None),
    ("E-LOC-CONEPIN", "锥销", "Cone pin", "locating.cone_pin", {"d": 20.0, "half_angle": 30.0, "h": 14.0}, {},
     "锥面与孔口接触定位，消除间隙，限制三个移动自由度；常与其他元件组合使用（如浮动锥销）。",
     ["孔口定位"], [(51, "常用定位元件")], None),
    # ---------------- 夹紧元件
    ("E-CLP-STRAP", "移动压板", "Sliding strap clamp", "elements.moving_strap", {"L": 110.0, "b": 32.0, "h": 14.0}, {},
     "螺母拧紧时压板以后端的支承为支点压住工件，杠杆比决定夹紧力；压板可沿长槽移动、绕螺柱转开，便于装卸工件。JJ-301-50 用两块移动压板压住轴的两端。",
     ["铣床、钻床夹具的螺旋压板夹紧"], [(52, "螺旋夹紧机构")], None),
    ("E-CLP-HOOK", "钩形压板", "Hook clamp", "elements.hook_clamp", {"r": 18.0, "H": 60.0, "reach": 26.0}, {},
     "钩头转到工件上方后下拉压紧，转开即可装卸；结构紧凑，适合夹具上空间小的地方。",
     ["空间紧凑处的夹紧"], [(52, "螺旋夹紧机构")], None),
    ("E-CLP-SCREW", "螺旋压紧（带摆动压块）", "Screw clamp with swivel pad", "elements.swivel_screw_clamp", {"d": 12.0, "L": 50.0}, {},
     "螺钉直接压紧工件时，端部装一个能摆动的压块，避免螺钉转动带动工件、压伤工件表面；螺旋夹紧自锁好、增力比大。",
     ["单件小批的直接螺旋夹紧"], [(52, "螺旋夹紧机构")], None),
    ("E-CLP-WEDGE", "斜楔", "Wedge", "elements.wedge", {"alpha_deg": 8.0, "L": 80.0, "B": 24.0, "h0": 10.0}, {},
     "斜楔把水平推力变成垂直的夹紧力，楔角小于两处摩擦角之和时自锁；楔角越小增力比越大，但行程越小，常用 6°～8°。",
     ["气动夹紧的增力环节"], [(52, "斜楔夹紧机构")], None),
    ("E-CLP-ECC", "圆偏心轮", "Circular eccentric cam", "elements.eccentric", {"D": 40.0, "e": 2.5, "B": 16.0}, {"handle": 80.0},
     "手柄转动圆偏心轮，靠半径的变化压紧工件，动作快；自锁条件是 e ≤ (D/2)·μ 左右，夹紧行程小，只适合尺寸变化小、振动小的场合。",
     ["快速手动夹紧"], [(52, "偏心夹紧机构")], None),
    ("E-CLP-TOGGLE", "铰链快速夹钳", "Toggle clamp", "elements.toggle_clamp", {}, {"open_deg": 0.0},
     "铰链杠杆在接近死点时增力比很大，越过死点后自锁，开合迅速；常用于焊接、装配夹具和轻切削。",
     ["焊接、装配、轻切削的快速夹紧"], [(52, "铰链夹紧机构")], None),
    ("E-CLP-SWING", "转角压紧缸", "Swing clamp cylinder", "elements.swing_clamp", {"arm": 40.0, "H": 70.0}, {"ang_deg": 0.0},
     "活塞先带压臂转过 90° 到工件上方，再直线下行压紧；松开时反向，压臂自动让开，便于机械手上下料。",
     ["加工中心、自动线的液压夹紧"], [(52, "气动与液压夹紧")], None),
    ("E-CLP-CYL", "夹紧气缸", "Pneumatic clamping cylinder", "elements.cylinder_pneu", {"bore": 50.0, "stroke": 40.0}, {},
     "气缸的推力 F = p·πD²/4·η，压缩空气 0.4～0.6 MPa；动作快但推力小、有压缩性，常配斜楔、杠杆增力。",
     ["气动夹紧"], [(52, "气动与液压夹紧")], None),
    ("E-CLP-COLLET", "弹簧夹头", "Spring collet", "elements.collet", {"d_grip": 30.0, "L": 70.0, "slots": 3}, {},
     "开槽的弹性套筒被锥面压缩，同时定心和夹紧工件的外圆，定心精度高、动作快，夹持直径范围小。",
     ["棒料、小轴的定心夹紧"], [(52, "定心夹紧机构")], None),
    # ---------------- 对刀与导向
    ("E-GDE-SETBLOCK", "对刀块（直角）", "Setting block (right-angle)", "elements.setting_block", {}, {"kind": "angle", "size": 20.0},
     "铣刀相对夹具的位置靠对刀块确定：刀齿与对刀块工作面之间塞进塞尺，以手感松紧合适为准。直角对刀块同时对深度和侧面两个方向。",
     ["铣床夹具对刀"], [(52, "对刀装置")], "JB/T 8031.3 直角对刀块"),
    ("E-GDE-FEELER", "对刀塞尺", "Feeler gauge", "elements.feeler", {"t": 3.0, "L": 60.0}, {},
     "对刀时塞在刀齿与对刀块之间，避免刀具直接碰对刀块；常用厚度 1、3、5 mm，对刀尺寸要减去塞尺厚度。",
     ["铣床夹具对刀"], [(52, "对刀装置")], "JB/T 8032.1 对刀平塞尺"),
    ("E-GDE-BUSHFIX", "固定钻套", "Fixed drill bushing", "elements.drill_bushing", {"d": 10.0, "H": 20.0}, {"kind": "fixed"},
     "直接压入钻模板，位置精度高，但磨损后不易更换，用于中小批生产、只钻一个工步的孔。",
     ["钻模的刀具导向"], [(52, "钻套")], "JB/T 8045.1 固定钻套"),
    ("E-GDE-BUSHREN", "可换钻套", "Renewable drill bushing", "elements.drill_bushing", {"d": 10.0, "H": 20.0}, {"kind": "renewable"},
     "装在压入钻模板的衬套里，用螺钉防转和防止被切屑带出；磨损后可以更换，用于大批量生产。",
     ["大批量钻孔"], [(52, "钻套")], "JB/T 8045.2 可换钻套"),
    ("E-GDE-BUSHQC", "快换钻套", "Quick-change drill bushing", "elements.drill_bushing", {"d": 10.0, "H": 20.0}, {"kind": "quick"},
     "转过一个角度就能取出，不用拧螺钉；一个孔要钻、扩、铰几个工步时，按工步换不同内径的钻套。",
     ["同一孔多工步加工"], [(52, "钻套")], "JB/T 8045.3 快换钻套"),
    ("E-GDE-BBUSH", "镗套", "Boring bushing", "elements.boring_bushing", {"D_bar": 40.0, "L": 50.0}, {"axis": "x"},
     "镗模上引导镗杆，保证孔系的位置精度不依赖机床精度。固定式镗套用于低速，回转式（装滚动轴承）用于高速镗削。",
     ["镗模的镗杆导向"], [(52, "镗床夹具")], None),
    # ---------------- 夹具体与连接
    ("E-BAS-KEY", "定位键", "Locating key", "elements.locating_key", {"b": 18.0, "L": 24.0, "h_out": 8.0}, {},
     "装在夹具体底面的槽里，嵌入机床工作台的 T 形槽，使夹具在工作台上定向；两个定位键相距越远，定向精度越高。",
     ["铣床夹具在工作台上定向"], [(52, "夹具体与连接元件")], "JB/T 8016 定位键"),
    ("E-BAS-TSLOT", "T 形槽底板", "T-slot base plate", "elements.tslot_plate", {"L": 400.0, "B": 300.0, "t": 40.0, "w": 14.0}, {},
     "槽系组合夹具和通用夹具的基础板，元件靠 T 形槽和螺栓定位、紧固，位置可以连续调整。",
     ["组合夹具基础件"], [(52, "组合夹具")], None),
    ("E-BAS-GRID", "孔系基础板", "Hole-grid base plate", "elements.hole_grid_plate", {"L": 400.0, "B": 300.0, "t": 30.0, "pitch": 50.0}, {},
     "按网格精密布置的定位孔与螺孔，元件用定位销定位、螺钉紧固，位置精度高、刚度好，但只能在孔距的整数倍上布置。",
     ["孔系组合夹具基础件"], [(52, "组合夹具")], None),
    ("E-BAS-ZPC", "零点定位器", "Zero-point clamping module", "elements.zero_point_chuck", {"D": 138.0, "H": 40.0}, {},
     "装在机床工作台上的模块，夹具底面的拉钉插入后自动定位并拉紧，重复定位精度约 0.005 mm；夹具在机外装好工件，换上去即可加工，换装时间以分钟计。",
     ["加工中心快速换装"], [(52, "零点定位系统")], None),
    ("E-BAS-PULLSTUD", "零点定位拉钉", "Pull stud for zero-point module", "elements.pull_stud", {}, {},
     "装在夹具或托盘底面，插入零点定位器后被钢球拉紧，同时起定位作用。",
     ["零点定位系统"], [(52, "零点定位系统")], None),
    ("E-BAS-INDEX", "分度盘", "Index plate", "elements.index_plate", {"D": 120.0, "n": 6, "t": 14.0}, {},
     "盘上均布分度孔，对定销插入孔中确定转角位置；分度精度取决于孔距精度和对定销的间隙。",
     ["回转式钻模、分度夹具"], [(52, "分度装置")], None),
    # ---------------- 机床附件
    ("E-ACC-CHUCK3", "三爪自定心卡盘", "Three-jaw self-centring chuck", "machines.chuck3", {"D": 160.0, "grip": 40.0}, {},
     "三个卡爪同步移动，同时定心和夹紧，装夹方便；定心精度一般 0.05～0.1 mm，夹持长度短时限制两个自由度，长时限制四个。",
     ["车床上装夹回转体零件"], [(50, "工序与安装"), (51, "常用定位元件")], None),
    ("E-ACC-CHUCK4", "四爪单动卡盘", "Four-jaw independent chuck", "locating.chuck4", {"D": 250.0}, {"grips": [60.0, 60.0, 60.0, 60.0]},
     "四个卡爪各自移动，夹紧力大，可以找正偏心或不规则的工件，但找正费时。",
     ["不规则、偏心工件的装夹找正"], [(51, "装夹方式")], None),
    ("E-ACC-VISE", "机用平口钳", "Machine vise", "machines.vise", {"jaw_w": 125.0, "opening": 60.0}, {},
     "固定钳口定位、活动钳口夹紧，是铣床、钻床上最常用的通用夹具；钳口面与导轨面的精度决定定位精度。",
     ["铣、钻小型零件"], [(51, "装夹方式")], None),
    ("E-ACC-CENTERS", "两顶尖", "Lathe centres", "machines.lathe_centers", {"L": 167.0}, {},
     "工件两端的中心孔支在前、后顶尖上，限制五个自由度，转动靠鸡心夹头带动；多次装夹都用同一个基准（中心孔），各外圆同轴度高。SH-301 的精车、磨削就是这样装夹。",
     ["轴类零件精车、磨外圆"], [(50, "工序与安装"), (51, "常用定位元件")], None),
    ("E-ACC-DIVHEAD", "万能分度头", "Universal dividing head", "machines.dividing_head", {}, {},
     "蜗杆蜗轮传动比 1:40，手柄转 40/z 转把工件分成 z 等分；用于铣齿、铣花键、铣多面。",
     ["铣床分度加工"], [(52, "分度装置")], None),
    ("E-ACC-ROTTABLE", "回转工作台", "Rotary table", "machines.rotary_table", {"D": 250.0}, {},
     "工作台由蜗杆驱动回转，用于铣圆弧槽、分度加工；数控回转台可作第四轴。",
     ["圆弧槽、分度加工"], [(52, "分度装置")], None),
    # ---------------- 夹具总成
    ("E-ASM-JJ30150", "键槽铣夹具 JJ-301-50", "Keyway milling fixture JJ-301-50", "local.jj30150_full", {}, {"work_state": "op40"},
     "SH-301 输出轴工序 50 铣键槽的专用夹具：两个 V 形块定位齿轮位两侧的外圆（限制四个自由度），止推板顶住轴肩端面，两块移动压板压紧，直角对刀块配塞尺对刀，两个定位键使夹具在工作台上定向。设计数据在数字工厂（std/JJ-301-50_fixture.yaml），书中第 52 章以它为主线。",
     ["键槽铣削"], [(52, "JJ-301-50 键槽铣夹具设计")], None),
    ("E-ASM-LATHEANGLE", "车床角铁式夹具", "Lathe angle-plate fixture", "typical.lathe_angle_plate", {}, {},
     "角铁装在花盘上，工件以底面和两个孔定位在角铁上，加工与底面平行的孔；要加平衡块平衡重心偏移。",
     ["车床上加工支架类零件的孔"], [(52, "车床夹具")], None),
    ("E-ASM-LATHEMANDREL", "车床心轴夹具", "Lathe mandrel fixture", "typical.lathe_mandrel", {}, {},
     "盘套类零件以孔和端面定位在心轴上，螺母压紧，车外圆和端面，保证外圆与孔同轴。",
     ["盘套类零件车外圆"], [(52, "车床夹具")], None),
    ("E-ASM-DRILLFIXED", "固定式钻模", "Fixed drill jig", "typical.drill_fixed", {}, {},
     "钻模板固定在夹具体上，钻套引导钻头；工件以平面、孔和侧面定位，螺钉压块压紧。",
     ["中小批钻孔"], [(52, "钻床夹具")], None),
    ("E-ASM-DRILLCOVER", "盖板式钻模", "Cover-plate drill jig", "typical.drill_cover", {}, {},
     "钻模板直接盖在工件上，以工件的孔和端面定位，没有夹具体，结构最简单，适合大型工件上钻孔。",
     ["大型工件钻孔"], [(52, "钻床夹具")], None),
    ("E-ASM-DRILLTUMBLE", "翻转式钻模", "Tumble drill jig", "typical.drill_tumble", {}, {},
     "钻模连同工件一起翻转，从几个方向钻孔，不用重新装夹工件；适合小型工件、多方向的孔。",
     ["小型工件多方向钻孔"], [(52, "钻床夹具")], None),
    ("E-ASM-DRILLIDX", "回转式钻模", "Indexing drill jig", "typical.drill_indexing", {"n": 6}, {},
     "工件装在回转分度盘上，转过一个分度、对定销插入定位，依次钻出圆周均布的孔；分度精度取决于分度盘和对定机构。",
     ["圆周均布孔"], [(52, "钻床夹具"), (52, "分度装置")], None),
    ("E-ASM-DRILLCOLUMN", "滑柱式钻模", "Slide-column drill jig", "typical.drill_column", {"lowered": 1.0}, {},
     "钻模板装在两根滑柱上，转动手柄靠齿轮齿条使钻模板升降并压紧工件，同时完成夹紧和导向，是通用化的钻模结构。",
     ["中小件快速钻孔"], [(52, "钻床夹具")], None),
    ("E-ASM-MILLMULTI", "多件联动铣夹具", "Multi-part linked milling fixture", "typical.mill_multi", {"n": 4}, {"linked": True},
     "一次装夹几个工件，一个夹紧动作通过浮动元件同时压紧全部工件，各处夹紧力均匀；用于直线进给铣削，缩短辅助时间。",
     ["小件大批量铣削"], [(52, "铣床夹具")], None),
    ("E-ASM-MILLCIRC", "圆周进给铣夹具", "Rotary-feed milling fixture", "typical.mill_circular", {"stations": 6}, {},
     "多个工位装在回转工作台上连续回转，一边加工一边在装卸区装卸工件，机动时间与辅助时间重合。",
     ["大批量连续铣削"], [(52, "铣床夹具")], None),
    ("E-ASM-BORINGJIG", "镗模", "Boring jig", "typical.boring_jig", {}, {},
     "镗杆由前后镗套引导，孔系的位置精度由镗模保证，不依赖机床精度；镗杆与机床主轴浮动连接。",
     ["箱体孔系镗削"], [(52, "镗床夹具")], None),
    ("E-ASM-TOMBSTONE", "加工中心夹具塔", "Tombstone fixture", "typical.tombstone", {"parts_per_face": 2}, {},
     "立柱的四个面上各装几个工件，卧式加工中心转台每转 90° 加工一面，一次装夹加工许多件，减少换刀与换装时间。",
     ["卧式加工中心批量加工"], [(52, "加工中心夹具")], None),
    ("E-ASM-MODULAR", "组合夹具", "Modular fixture", "typical.modular_fixture", {}, {},
     "用标准化的基础件、支承件、定位件、压紧件按工件组装成夹具，用完拆开、元件重复使用，适合新产品试制和单件小批。",
     ["试制、单件小批"], [(52, "组合夹具")], None),
    ("E-ASM-LINKED2D", "双向联动夹紧夹具", "Two-direction linked clamp", "typical.linked_clamp_two_dir", {}, {},
     "一个夹紧动作通过杠杆同时从两个方向压紧工件，保证先后顺序和夹紧力分配。",
     ["需要两个方向同时夹紧的工件"], [(52, "联动夹紧机构")], None),
    # ---------------- 案例工件
    ("E-WKP-SH301", "SH-301 输出轴（各工序状态）", "Output shaft SH-301 (all process states)", "local.sh301_states", {"spacing": 70.0}, {},
     "WQR-105 减速器的输出轴，《机械制造技术》第 50–57 章的主线零件。毛坯与五个工序状态（粗车、精车、铣键槽、磨外圆）各一个节点，由工艺规程（std/SH-301_process.yaml）的工序简图数据生成，橙色是该工序加工的面。",
     ["工艺过程、尺寸链、定位与夹具设计的教学案例"], [(50, "SH-301 的工艺过程"), (53, "工艺尺寸链")], None),
    ("E-WKP-LEVER", "杠杆（钻模案例工件）", "Lever (drill-jig case part)", "typical.lever_part", {"t": 20.0}, {},
     "大头孔、小头孔和中间连板组成的杠杆，固定式钻模以大头孔和端面定位钻小头孔。",
     ["钻模设计案例"], [(52, "钻床夹具")], None),
    ("E-WKP-BRACKET", "支架（车床夹具案例工件）", "Bracket (lathe-fixture case part)", "typical.bracket_part", {}, {},
     "底板加立板的支架，车床角铁式夹具以底面和两个孔定位，加工立板上的孔。",
     ["车床夹具设计案例"], [(52, "车床夹具")], None),
    ("E-WKP-BOX", "箱体（镗模案例工件）", "Housing (boring-jig case part)", "typical.box_part", {"L": 200.0, "B": 140.0, "H": 120.0}, {"bore": [62.0, 80.0]},
     "前后壁上有同轴的两个轴承孔的箱体（简化），镗模以底面和两个工艺孔定位镗孔系。",
     ["镗模设计、一面两销定位案例"], [(51, "一面两销定位"), (52, "镗床夹具")], None),
]

# 模型函数返回 {名称: 形体} 或 (形体, ...) 时的中文零件名
NAMES = {"E-LOC-AUX": {"body": "支承座", "plunger": "柱塞（支承）", "lock": "顶紧螺钉"},
         "E-LOC-MANDREL": ["心轴", "压紧螺母"], "E-BAS-INDEX": ["分度盘", "对定销"]}

# 按名称判断不准的，逐个指定作用
ROLES = {"E-ASM-JJ30150": {"可调支承": "夹紧", "螺柱": "夹紧"}, "E-ASM-MODULAR": {"后支承": "夹紧"}}

ROLE_NOTE = "尺寸为书中示例规格（示意比例），设计时以所用标准为准；模型与教材插图、数字工厂用的是同一份（factory/digital/models3d）"


def entry_doc(row):
    eid, zh, en, fn, defaults, args, principle, uses, chapters, std = row
    kind = "case" if eid.split("-")[1] in ("ASM", "WKP") else "product"
    params = []
    for k in defaults:
        key, pzh, pen, unit = P[k]
        d = {"key": key, "zh": pzh, "en": pen, "role": "key"}
        if unit:
            d["unit"] = unit
        params.append(d)
    doc = {
        "schema": 1, "id": eid, "kind": kind, "name": {"zh": zh, "en": en}, "category": eid.split("-")[1],
        "tags": ["工装夹具", "机床夹具"] + ([std.split(" ")[0] + " " + std.split(" ")[1]] if std else []),
        "standards": [{"code": " ".join(std.split(" ")[:2]), "title": " ".join(std.split(" ")[2:]) + "（结构型式参照）"}] if std else [],
        "params": params, "defaults": dict(defaults),
        "model": {"engine": "wqfix:" + fn, "formats": ["glb", "step", "stl"],
                  "origin": "毫米制造型，Z 向上（glTF 里换成 Y 向上、米）；每个零件一个节点，节点颜色同教材插图",
                  "note": ROLE_NOTE},
        "source": {"origin": "wenquest", "license": "Apache-2.0",
                   "attribution": "问渠零件库（造型程序 factory/digital/models3d，经 library/generators/e_fixture.py）",
                   "checked": {"by": "Claude", "on": TODAY, "note": "自建；与教材插图同一个函数、同一组参数，零件库测试核对节点与零件表"}},
        "teaching": {"principle": principle, "uses": uses,
                     "courses": [{"course": MFG, "chapter": f"第 {c} 章 {t}"} for c, t in chapters], "labs": []},
        "factory": {"erp_items": [], "suppliers": []},
    }
    if args:
        doc["model"]["args"] = dict(args)
    if eid in ROLES:
        doc["model"]["roles"] = ROLES[eid]
    if eid in NAMES:
        doc["model"]["names"] = NAMES[eid]
    return doc


def main():
    ids = [r[0] for r in E]
    assert len(ids) == len(set(ids)), "编号重复"
    out = ROOT / "catalog" / "E"
    for row in E:
        d = out / row[0]
        d.mkdir(parents=True, exist_ok=True)
        head = f"# {row[0]} · {row[1]}（工装夹具，第 13 轮 8.7；由 tools/import_fixtures.py 生成，改表后重新运行）\n"
        (d / "entry.yaml").write_text(head + yaml.safe_dump(entry_doc(row), allow_unicode=True, sort_keys=False, width=120),
                                      encoding="utf-8")
    print(f"写了 {len(E)} 个条目到 {out}")


if __name__ == "__main__":
    main()
