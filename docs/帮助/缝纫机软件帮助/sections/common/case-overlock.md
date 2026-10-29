---
id: case-ol
title: 案例二　包缝机：空间四杆的弯针
lead: 弯针要摆多大、传动角够不够、会不会卡死；摆杆能减多少重。
---
**实际问题**：一台 504 三线包缝机（教材算例，7000 r/min）。包缝机的上、下弯针都由**空间四杆（RSSR）**驱动：主轴上的偏心轮带球头连杆，推着摆杆绕另一根轴摆。空间四杆不像平面四杆那样一眼看得出好坏——传动角太小会别劲、发热，偏心半径过了临界值会**卡死**。

### 第一步　看默认设计：一盏黄灯 {#case-ol-base}

<ol class="steps">
<li>打开包缝机（教材算例参数）。“样机”页签下面的主要结果：针杆行程 {{ol_stroke}}，下弯针摆角 {{ol_swing}}、弯针尖最高速度 {{ol_tipv}}，上弯针摆角 {{ol_ulswing}}；下弯针偏心半径的卡死临界值 {{ol_crit}}。</li>
<li>“校核”页签：{{ol.base.counts.all}} 项里红灯 0、黄灯 {{ol.base.counts.warn}}：<b>{{ol.base.warn.0.name}} {{ol.base.warn.0.value}}</b>（要求 {{ol.base.warn.0.limit}}）。能用，但上弯针机构会别劲。</li>
</ol>

### 第二步　下弯针摆大一点行不行？ {#case-ol-lower}

常有人想：下弯针多摆一点，线环钩得更稳。把“下弯针（空间四杆 RSSR）”的**偏心半径**从 4.36 mm 往上拖：

| 偏心半径 | 下弯针摆角与弧长 | 下弯针最小传动角 | 偏心半径 / 卡死临界值 | 弯针尖最高速度 | 黄灯 |
|---|---|---|---|---|---|
| 4.36（算例） | {{ol.base.vals.ll_swing}} | {{ol.base.vals.ll_gamma}} | {{ol.base.vals.ll_crit}} | {{ol.base.vals.ll_speed}} | {{ol.base.counts.warn}} |
| 6 | {{ol.ll_r_6.vals.ll_swing}} | {{ol.ll_r_6.vals.ll_gamma}} | {{ol.ll_r_6.vals.ll_crit}} | {{ol.ll_r_6.vals.ll_speed}} | {{ol.ll_r_6.counts.warn}} |
| 8 | {{ol.ll_r_8.vals.ll_swing}} | {{ol.ll_r_8.vals.ll_gamma}} | {{ol.ll_r_8.vals.ll_crit}} | {{ol.ll_r_8.vals.ll_speed}} | {{ol.ll_r_8.counts.warn}} |

摆得越大，弧长超出 15–20 mm 的合适范围，弯针尖速度超过 10 m/s，传动角掉到 40° 以下，离卡死越来越近（临界值 {{ol_crit}}，超过就转不过去）。（黄灯数里含上弯针那一盏。）**结论：下弯针保持算例的摆角。**想系统地找，用“设计优化”的目标“下弯针：弧长 15–20 mm 时传动角最大”。

### 第三步　设计优化：把上弯针的黄灯消掉 {#case-ol-upper}

<ol class="steps">
<li>“CAE 分析 → 设计优化”，目标选<b>“上弯针：摆角不变时传动角最大”</b>，提交。几秒出三组方案，每组都整机校核过。</li>
<li>最好的一组：上弯针{{ol_opt}}（mm），最小传动角 <b>{{ol_opt_gamma}}°</b>，红灯 0、黄灯 0。</li>
<li>点“采用”回填到左边：{{ol.opt_upper_after.counts.all}} 项全部合格。上弯针摆角基本没变（{{ol_ulswing}} → {{ol_ulswing_opt}}），线迹不受影响。</li>
</ol>

::try{label="打开包缝机算例（上弯针传动角黄灯）" machine=overlock tab=checks}

### 第四步　一个零件：下弯针摆杆减重 {#case-ol-rocker}

摆杆每针来回摆一次，越轻，主轴负担和振动越小。但减多少？

<ol class="steps">
<li>“零件强度与疲劳（有限元）”选<b>下弯针摆杆</b>：{{ol.rocker_fea.vm}} MPa，安全系数 {{ol.rocker_fea.sf}}，疲劳寿命 &gt; 1000 年。有余量。</li>
<li>“零件减重（拓扑优化）”选下弯针摆杆，分别留 <b>50%</b> 和 <b>40%</b> 提交，再各自“送有限元复核”：</li>
</ol>

| 留下的材料 | 轻了 | 复核：最大应力 | 安全系数（≥ 2） | 疲劳寿命（≥ 5 年） | 结论 |
|---|---|---|---|---|---|
| 原样 | — | {{ol.rocker_fea.vm}} MPa | {{ol.rocker_fea.sf}} | &gt; 1000 年 | 合格 |
| 50% | {{ol_cut50}}% | {{ol.rocker_topo50.verify.vm}} MPa | {{ol.rocker_topo50.verify.sf}} | {{ol_life50}} 年 | **合格，用这个** |
| 40% | {{ol_cut40}}% | {{ol.rocker_topo40.verify.vm}} MPa | {{ol.rocker_topo40.verify.sf}} | 不到 1 年 | **不合格** |

留下的材料从 50% 降到 40%，最大应力涨到 {{ol_ratio40}} 倍，寿命从 {{ol_life50}} 年掉到不到一年——**拓扑优化的结果一定要送有限元复核**，软件也是这么要求的。（“留 50%”说的是毂和孔周以外那部分材料留一半；毂和孔周不减，所以整件只轻了 {{ol_cut50}}%。）

<ol class="steps" start="3">
<li>在“留 50%”的结果上点“出铣削程序”：{{ol_cam_topo}}，试切检查 0 错误。比原样的摆杆（约 {{ol_cam}} 秒）还慢一点——挖出的型腔要多铣几圈，减重省的是材料和运动惯量，不是加工时间。减重后的轮廓按单元网格取出，边上有小台阶，出图前在 CAD 里圆顺；DXF、STEP 在同一个结果里下载。</li>
</ol>

### 差动送布：布边平不平 {#case-ol-diff}

包缝机的另一个典型机构。弹力布、针织布缝时容易被拉长（荷叶边）或缩皱，靠**差动送布**：前面的差动牙（布先经过它）比后面的主送布牙走得多一点或少一点。软件算出这块布要平整的差动比 D* = {{ol_D}}，差动臂长 l_d = D·l_m = {{ol_ld}}；“送布与差动”一组里改“差动比 D”，校核“布边平整（差动送布）”马上告诉你布边会被拉长还是缩皱。设计优化里对应的目标是“差动比：布边平整”。

切边也在校核里：上刀切布时针必须在布里（布不动），上下刀要有重叠量（“切边”一组）。

::only{web}
::video{src=web-10-case-ol title="案例二：包缝机上弯针设计优化；下弯针摆杆留 50% 和 40% 减重复核"}
::end

::only{freecad}
FreeCAD 里“新建包缝机设计”可以生成引针机构、上下弯针空间四杆、差动送布臂、切刀，改参数、看校核；设计优化、有限元、减重、数控在网页版做，参数文件两边互通。
::end
