"""Lab guides (实验指导书) and lab report templates (实验报告模板) for Chapter 1, Chinese–English."""
from pathlib import Path
from docgen import Doc

ROOT = Path("out/大学物理（上）课程资料")
GUIDES = ROOT / "第1章 质点运动学" / "虚拟实验"
REPORTS = ROOT / "第1章 质点运动学" / "虚拟实验" / "实验报告模板"
GUIDES.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)
LINK = "问渠课程页“虚拟实验”，或课件实验页的“打开虚拟实验”按钮 / the Virtual Lab link on the course page or the “Open virtual lab” button in the slides"

LABS = [
  {
    "no": "1.1", "file": "实验1.1 参考系与相对运动（传送带抓取）",
    "zh": "参考系：同一运动的不同描述", "en": "Reference Frames: One Motion, Different Descriptions",
    "goal": [("理解运动的相对性：同一运动在不同参考系中的轨迹和速度不同。", "Understand that motion is relative: the path and velocity of one motion differ between frames."),
             ("学会用速度叠加 v(对地) = v(相对) + v(牵连) 计算运动物体的速度。", "Use velocity addition v(ground) = v(relative) + v(frame) to compute velocities."),
             ("用参考系的思想解决机器人传送带跟踪抓取问题。", "Apply frame thinking to a robot grasping parts from a moving conveyor.")],
    "theory": [("以速度 u 相对地面运动的参考系中，物体的速度 v′ 与对地速度 v 满足 v = v′ + u（伽利略变换，u ≪ c）。", "In a frame moving at u relative to the ground, an object’s velocity v′ and ground velocity v satisfy v = v′ + u (Galilean transformation, u ≪ c)."),
               ("列车中静止释放的小球：车厢参考系中做自由落体，轨迹是竖直线；地面参考系中水平速度为 u，轨迹是抛物线。下落时间 t = √(2h/g)，与参考系无关。", "A ball released at rest in a train falls straight down in the carriage frame and follows a parabola in the ground frame (horizontal speed u). The fall time t = √(2h/g) is the same in both frames."),
               ("传送带抓取：让机械臂末端相对传送带竖直向下运动（v′ = 0.25 m/s），则对地速度为 v = √(u² + 0.25²)，方向与水平面夹角 α = arctan(0.25/u)。", "Conveyor grasp: if the gripper moves straight down relative to the belt (v′ = 0.25 m/s), its ground velocity is v = √(u² + 0.25²) at an angle α = arctan(0.25/u) below horizontal.")],
    "env": [("场景", "Scene", "列车上落球；机器人：传送带抓取", "Ball in a train; Robot: conveyor grasp"),
            ("列车速度", "Train speed", "0 – 30 m/s，下落高度 1.80 m", "0 – 30 m/s, drop height 1.80 m"),
            ("传送带速度", "Belt speed", "0 – 1.00 m/s", "0 – 1.00 m/s"),
            ("观察者速度", "Observer speed", "列车 −30 – 30 m/s；传送带 −1 – 1 m/s", "train −30 – 30 m/s; belt −1 – 1 m/s")],
    "steps": [("选“列车上落球”，列车速度 12 m/s，“站在地面上”，按“松手”。记录轨迹形状和水平位移。", "Choose “Ball in a train”, train speed 12 m/s, “On the ground”, press “Let go”. Record the path shape and horizontal shift."),
              ("改为“坐在车厢里”“反向运动”各做一次，填表 1。", "Repeat with “In the carriage” and “Moving the other way”; fill in Table 1."),
              ("选“机器人：传送带抓取”，传送带速度 0.50 m/s，“随传送带运动”，按“开始抓取”，观察末端轨迹。", "Choose “Robot: conveyor grasp”, belt speed 0.50 m/s, “Moving with the belt”, press “Start grasp” and watch the gripper path."),
              ("改为“站在地面上”，读出末端对地速度和夹角；把传送带速度改为 0.20、0.80 m/s 重复，填表 2。", "Switch to “On the ground”, read the gripper’s ground speed and angle; repeat for belt speeds 0.20 and 0.80 m/s; fill in Table 2."),
              ("用公式计算表 2 的理论值，与测量值比较。", "Compute the theoretical values in Table 2 and compare.")],
    "tables": [
      ("表 1  列车上落球（u = 12 m/s） Table 1  Ball in a train", ["观察者 Observer", "观察者速度 m/s", "轨迹形状 Path", "水平位移 m（测）", "水平位移 m（算）"],
       [["站在地面上 ground", "0", "", "", ""], ["坐在车厢里 carriage", "12", "", "", ""], ["反向运动 opposite", "−12", "", "", ""]], [3.2, 2.4, 3.0, 2.8, 2.8]),
      ("表 2  传送带抓取 Table 2  Conveyor grasp", ["传送带速度 u  m/s", "对地速度 m/s（测）", "对地速度 m/s（算）", "夹角 α（测）", "夹角 α（算）"],
       [["0.20", "", "", "", ""], ["0.50", "", "", "", ""], ["0.80", "", "", "", ""]], [3.0, 2.8, 2.8, 2.4, 2.4]),
    ],
    "cautions": [("读数在小球落地、抓取完成后才出现。", "Readings appear only after the ball lands or the grasp finishes."),
                 ("“慢放”只改变播放速度，不改变物理过程。", "“Slow motion” changes only the playback speed, not the physics.")],
    "questions": [("车厢里的人说小球“竖直下落”，地面上的人说它“做平抛运动”，谁对？为什么？", "The passenger says the ball falls straight down; the person on the ground says it is a projectile. Who is right, and why?"),
                  ("下落时间与观察者速度有没有关系？在什么情况下伽利略变换不再适用？", "Does the fall time depend on the observer’s speed? When does the Galilean transformation stop working?")],
    "problem": ("传送带跟踪抓取", "Grasping from a moving conveyor",
                "工件在传送带上以 u = 0.50 m/s 运动。机械臂在传送带参考系中规划“竖直下降 0.50 m、速度 0.25 m/s”的抓取动作。(1) 在地面参考系中，末端的速度和轨迹是怎样的？(2) 如果末端对地只竖直下降（忘了跟随传送带），抓取时工件相对末端移动了多远？(3) 在真实产线上，还有哪些因素会让这个模型失效？",
                "A part moves on the belt at u = 0.50 m/s. In the belt frame the arm plans a straight 0.50 m descent at 0.25 m/s. (1) What are the gripper’s velocity and path in the ground frame? (2) If the gripper only moved straight down relative to the ground, how far would the part slide past it during the grasp? (3) What else on a real line could break this model?"),
    "everyday": ("雨天坐车，车窗上的雨痕是斜的。若雨滴竖直下落速度约 7 m/s、车速 20 m/s，雨痕与竖直方向成多大角？", "On a rainy day, raindrop streaks on a car window are slanted. If raindrops fall at about 7 m/s and the car moves at 20 m/s, what angle do the streaks make with the vertical?"),
  },
  {
    "no": "1.2", "file": "实验1.2 位矢、位移与速度（机器人里程计）",
    "zh": "位矢、位移与速度", "en": "Position, Displacement and Velocity",
    "goal": [("区分位移与路程，理解 |Δr| ≠ Δs 而 |dr| = ds。", "Distinguish displacement from path length: |Δr| ≠ Δs, but |dr| = ds."),
             ("理解瞬时速度是平均速度在 Δt → 0 时的极限，方向沿轨迹切线。", "See instantaneous velocity as the limit of average velocity as Δt → 0, tangent to the path."),
             ("分析由离散定位数据估算速度时，采样间隔与测量噪声的权衡。", "Analyse the trade-off between sampling interval and measurement noise when estimating speed from position samples.")],
    "theory": [("平均速度 v̄ = Δr/Δt；瞬时速度 v = dr/dt，速率 v = ds/dt。", "Average velocity v̄ = Δr/Δt; instantaneous velocity v = dr/dt; speed v = ds/dt."),
               ("用相邻两个定位点估算速率：v ≈ |r(k+1) − r(k)| / T。T 太大时，弦比弧短，低估速率并抹平变化；T 太小时，定位误差 σ 被放大，速率误差约为 √2·σ / T。", "Estimating speed from neighbouring samples, v ≈ |r(k+1) − r(k)| / T: a large T shortens the chord, underestimating speed and smoothing changes; a small T amplifies position error σ, giving a speed error of about √2·σ / T.")],
    "env": [("运动方程", "Motion", "例1-1、匀速圆周、摆线、机器人里程计、自定义", "Example 1-1, circle, cycloid, robot odometry, custom"),
            ("时间间隔 Δt", "Interval Δt", "0.002 – 2 s", "0.002 – 2 s"),
            ("采样间隔 T", "Sampling interval T", "0.02 – 1.5 s", "0.02 – 1.5 s"),
            ("定位噪声 σ", "Position noise σ", "0 – 3 cm", "0 – 3 cm")],
    "steps": [("选“例1-1”，t = 0.80 s。把 Δt 依次设为约 1、0.5、0.1、0.01 s，记录 |Δr| 与 Δs，填表 1。", "Choose Example 1-1, t = 0.80 s. Set Δt to about 1, 0.5, 0.1 and 0.01 s; record |Δr| and Δs in Table 1."),
              ("把 t 调到 1.00 s，读出 v 和 a，与例题答案比较。", "Set t = 1.00 s, read v and a, and compare with the worked example."),
              ("选“匀速圆周”，比较速率 |v| 与 d|r|/dt。", "Choose the uniform circle and compare |v| with d|r|/dt."),
              ("选“机器人：里程计数据”，σ = 1.0 cm。采样间隔依次取表 2 中的值，记录速率相对误差。", "Choose “Robot: odometry data”, σ = 1.0 cm. Use the sampling intervals in Table 2 and record the speed error."),
              ("画出“误差—采样间隔”曲线，找出误差最小的采样间隔。", "Plot error against sampling interval and find the interval with the smallest error.")],
    "tables": [
      ("表 1  位移与路程（例1-1，t = 0.80 s） Table 1  Displacement vs path length", ["Δt  s", "|Δr|  m", "Δs  m", "(Δs − |Δr|)/Δs"],
       [["≈1", "", "", ""], ["≈0.5", "", "", ""], ["≈0.1", "", "", ""], ["≈0.01", "", "", ""]], [3.0, 3.5, 3.5, 4.0]),
      ("表 2  里程计采样间隔（σ = 1.0 cm） Table 2  Odometry sampling interval", ["采样间隔 T  s", "0.02", "0.05", "0.1", "0.2", "0.5", "1.0", "1.5"],
       [["速率误差 %", "", "", "", "", "", "", ""]], [3.4, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]),
    ],
    "cautions": [("Δt 滑块是对数刻度，读数以右侧显示为准。", "The Δt slider is logarithmic; use the value shown on the right."),
                 ("里程计的噪声是固定的一组随机数，同一组参数每次结果相同，便于比较。", "The odometry noise is a fixed random sequence, so the same settings always give the same result.")],
    "questions": [("为什么 d|r|/dt 不是速率？举一个 d|r|/dt = 0 而速率不为零的例子。", "Why is d|r|/dt not the speed? Give an example where d|r|/dt = 0 but the speed is not zero."),
                  ("由表 2，误差为什么先减小后增大？", "From Table 2, why does the error first fall and then rise?")],
    "problem": ("移动机器人的里程计", "Odometry of a mobile robot",
                "仓储机器人每隔 T 记录一次自己的位置，定位误差约 1 cm，行驶速度约 0.5 m/s。(1) 用 v ≈ √2·σ/T 估计：要让噪声引起的速率误差小于 5%，T 至少多大？(2) 结合表 2，T 太大有什么问题？(3) 实际机器人怎样同时得到“不抖”又“不迟钝”的速度？（提示：滤波、融合轮速计和惯性测量单元。）",
                "A warehouse robot logs its position every T seconds with about 1 cm error while moving at about 0.5 m/s. (1) Using √2·σ/T, how large must T be for the noise-induced speed error to stay below 5%? (2) From Table 2, what goes wrong when T is too large? (3) How do real robots get a speed that is neither noisy nor sluggish? (Hint: filtering, fusing wheel encoders and an IMU.)"),
    "everyday": ("手机导航每秒得到一个 GPS 定位点（误差几米），它显示的车速为什么比定位点本身稳定？", "A phone gets one GPS fix per second with a few metres of error. Why is the speed it shows steadier than the fixes themselves?"),
  },
  {
    "no": "1.3", "file": "实验1.3 抛体运动（投篮机器人）",
    "zh": "抛体运动", "en": "Projectile Motion",
    "goal": [("验证抛体运动是水平匀速运动与竖直匀加速运动的合成。", "Verify that projectile motion combines uniform horizontal motion and uniformly accelerated vertical motion."),
             ("测量射程、最大高度与抛射角的关系，验证 R = v₀² sin2θ / g。", "Measure how range and maximum height depend on angle and check R = v₀² sin2θ / g."),
             ("理解理想模型（忽略空气阻力、出手高度）的适用范围。", "Understand when the ideal model (no drag, zero launch height) applies."),
             ("为投篮机器人计算出手速度与角度。", "Compute launch speed and angle for a basketball-shooting robot.")],
    "theory": [("忽略空气阻力：x = v₀cosθ·t，y = h₀ + v₀sinθ·t − ½gt²。", "Without drag: x = v₀cosθ·t, y = h₀ + v₀sinθ·t − ½gt²."),
               ("h₀ = 0 时：飞行时间 T = 2v₀sinθ/g，射程 R = v₀² sin2θ/g，最大高度 H = v₀² sin²θ/(2g)；θ = 45° 射程最大，互余角射程相同。", "With h₀ = 0: flight time T = 2v₀sinθ/g, range R = v₀² sin2θ/g, max height H = v₀² sin²θ/(2g); 45° gives the maximum range and complementary angles give equal ranges."),
               ("过定点 (X, Δy) 所需初速度：v₀ = (X / cosθ) · √[ g / (2(X tanθ − Δy)) ]。", "Launch speed to pass through (X, Δy): v₀ = (X / cosθ) · √[ g / (2(X tanθ − Δy)) ].")],
    "env": [("场景", "Scene", "发射场打靶；机器人：投篮", "Target range; Robot: basket"),
            ("初速度 v₀", "Launch speed v₀", "3 – 40 m/s（投篮 3 – 15 m/s）", "3 – 40 m/s (basket 3 – 15 m/s)"),
            ("抛射角 θ、抛出高度 h₀", "Angle θ, height h₀", "0 – 90°；0 – 30 m", "0 – 90°; 0 – 30 m"),
            ("重力加速度 g", "Gravity g", "地球 9.8、火星 3.71、月球 1.62 m/s²", "Earth 9.8, Mars 3.71, Moon 1.62 m/s²"),
            ("篮筐", "Hoop", "高 2.43 m，距出手点 4 m，出手高 0.8 m", "2.43 m high, 4 m away, release at 0.8 m")],
    "steps": [("“发射场打靶”，v₀ = 20 m/s，h₀ = 0，无阻力。θ 依次取 15°–75°，记录射程和最大高度，填表 1。", "Target range, v₀ = 20 m/s, h₀ = 0, no drag. Launch at 15°–75°; record range and height in Table 1."),
              ("打开空气阻力，重复 30°、40°、45°、50°，找出新的最佳角度。", "Switch on drag and repeat at 30°, 40°, 45°, 50°; find the new best angle."),
              ("h₀ = 2.0 m、v₀ = 13.5 m/s（铅球），找出射程最大的角度。", "Set h₀ = 2.0 m, v₀ = 13.5 m/s (shot put) and find the best angle."),
              ("“机器人：投篮”，θ 取 45°、55°、65°，先用公式算出所需 v₀，再发射验证，填表 2。", "Robot: basket. For θ = 45°, 55°, 65°, compute v₀ from the formula, then launch to check; fill in Table 2.")],
    "tables": [
      ("表 1  射程与抛射角（v₀ = 20 m/s，h₀ = 0） Table 1  Range vs angle", ["θ", "15°", "30°", "45°", "60°", "75°"],
       [["射程 R 测量 m", "", "", "", "", ""], ["射程 R 理论 m", "", "", "", "", ""], ["最大高度 H 测量 m", "", "", "", "", ""], ["最大高度 H 理论 m", "", "", "", "", ""]], [4.0, 2.0, 2.0, 2.0, 2.0, 2.0]),
      ("表 2  投篮机器人（出手高 0.8 m，篮筐 2.43 m，距离 4 m） Table 2  Basketball robot", ["θ", "所需 v₀ 计算 m/s", "实际使用 v₀ m/s", "是否投进", "飞行时间 s"],
       [["45°", "", "", "", ""], ["55°", "", "", "", ""], ["65°", "", "", "", ""]], [2.0, 3.4, 3.2, 2.4, 2.6]),
    ],
    "cautions": [("投篮判定：球须从上方落入篮筐（下降时穿过篮筐高度）。", "A basket counts only if the ball comes down through the hoop."),
                 ("初速度滑块步长 0.1 m/s，计算值需四舍五入。", "The speed slider moves in 0.1 m/s steps; round your computed value.")],
    "questions": [("有空气阻力时，最佳角度为什么小于 45°？", "Why is the best angle below 45° with air drag?"),
                  ("投篮时，角度大一些和小一些各有什么好处？（提示：对速度误差的敏感程度、入射角。）", "For a basket, what are the advantages of a steeper or flatter shot? (Hint: sensitivity to speed error, entry angle.)")],
    "problem": ("投篮机器人", "A basketball-shooting robot",
                "机器人出手点高 0.8 m，篮筐高 2.43 m、水平距离 4 m。(1) 分别求 θ = 45°、55°、65° 时所需的出手速度。(2) 若发射机构的速度误差为 ±0.1 m/s，哪个角度落点偏差最小？（提示：分别用 v₀ ± 0.1 发射，比较落在篮筐高度时的水平位置。）(3) 真实比赛中还要考虑哪些因素？",
                "The robot releases at 0.8 m; the hoop is 2.43 m high and 4 m away. (1) Find the launch speed needed at θ = 45°, 55° and 65°. (2) If the launcher’s speed error is ±0.1 m/s, which angle gives the smallest miss? (Hint: launch with v₀ ± 0.1 and compare where the ball crosses hoop height.) (3) What else matters in a real competition?"),
    "everyday": ("铅球出手高度约 2 m、出手速度约 13–14 m/s。为什么最佳出手角约为 42°，而不是 45°？", "A shot is released at about 2 m and 13–14 m/s. Why is the best angle about 42° rather than 45°?"),
  },
  {
    "no": "1.4", "file": "实验1.4 圆周运动（AGV 转弯限速）",
    "zh": "圆周运动的速度与加速度", "en": "Velocity and Acceleration in Circular Motion",
    "goal": [("理解切向加速度改变速率、法向加速度改变速度方向。", "Understand that tangential acceleration changes speed and normal acceleration changes direction."),
             ("验证 aₙ = v²/R = Rω²、aₜ = Rα。", "Verify aₙ = v²/R = Rω² and aₜ = Rα."),
             ("用法向加速度为 AGV 确定转弯限速。", "Use normal acceleration to set a cornering speed limit for an AGV.")],
    "theory": [("a = aₜ eₜ + aₙ eₙ，aₜ = dv/dt = Rα，aₙ = v²/R = Rω²。", "a = aₜ eₜ + aₙ eₙ, with aₜ = dv/dt = Rα and aₙ = v²/R = Rω²."),
               ("车辆转弯时，地面摩擦提供向心力。不打滑的条件 aₙ ≤ μg；不侧翻的条件 aₙ ≤ g·(b/2)/h（b 为轮距，h 为质心高度）。两者取较小值决定限速 v_max = √(aₙ,max · R)。", "When a vehicle turns, friction provides the centripetal force. No sliding requires aₙ ≤ μg; no tipping requires aₙ ≤ g·(b/2)/h (b: track width, h: height of the centre of mass). The smaller limit sets v_max = √(aₙ,max · R).")],
    "env": [("类型", "Mode", "匀速圆周、匀加速圆周、例1-3、机器人：AGV 转弯", "Uniform, speeding up, Example 1-3, Robot: AGV turning"),
            ("半径 R", "Radius R", "0.5 – 3 m", "0.5 – 3 m"),
            ("角速度 ω、角加速度 α", "ω, α", "0 – 4 rad/s；−1 – 1.5 rad/s²", "0 – 4 rad/s; −1 – 1.5 rad/s²"),
            ("AGV", "AGV", "质心高 0.6 m，轮距 0.5 m，μ = 0.6，速度 0 – 4 m/s", "CoM 0.6 m high, track 0.5 m, μ = 0.6, speed 0 – 4 m/s")],
    "steps": [("“匀速圆周”，R = 2 m，ω 取 0.5、1.0、1.5、2.0 rad/s，记录 aₙ，填表 1。", "Uniform mode, R = 2 m, ω = 0.5, 1.0, 1.5, 2.0 rad/s; record aₙ in Table 1."),
              ("“匀加速圆周”，观察 a 与 v 的夹角怎样随时间变化。", "Speeding-up mode: watch how the angle between a and v changes."),
              ("“例1-3”，按“跳到 t = 2 s”，读出 aₜ、aₙ，与例题答案比较。", "Example 1-3: press “Jump to t = 2 s”, read aₜ and aₙ, compare with the worked example."),
              ("“机器人：AGV 转弯”，R 取 1.0、1.5、2.0、2.5 m，逐渐加大速度，找出开始侧翻的速度，填表 2。", "Robot: AGV turning. For R = 1.0, 1.5, 2.0, 2.5 m, raise the speed until the AGV starts to tip; fill in Table 2.")],
    "tables": [
      ("表 1  法向加速度（R = 2 m） Table 1  Normal acceleration", ["ω  rad/s", "0.5", "1.0", "1.5", "2.0"],
       [["aₙ 测量 m/s²", "", "", "", ""], ["Rω² 计算 m/s²", "", "", "", ""]], [4.0, 2.4, 2.4, 2.4, 2.4]),
      ("表 2  AGV 转弯限速 Table 2  AGV speed limit", ["R  m", "侧翻速度 测量 m/s", "侧翻速度 计算 m/s", "打滑速度 计算 m/s", "先发生"],
       [["1.0", "", "", "", ""], ["1.5", "", "", "", ""], ["2.0", "", "", "", ""], ["2.5", "", "", "", ""]], [1.8, 3.4, 3.4, 3.4, 2.4]),
    ],
    "cautions": [("箭头长度按比例压缩显示，只看方向，数值以右侧读数为准。", "Arrow lengths are compressed; read magnitudes from the panel."),
                 ("AGV 模型把轮胎看成刚性、忽略悬挂和货物晃动。", "The AGV model treats tyres as rigid and ignores suspension and load sway.")],
    "questions": [("匀速圆周运动速率不变，为什么还有加速度？", "In uniform circular motion the speed is constant. Why is there still an acceleration?"),
                  ("表 2 中侧翻速度与 R 是什么关系？把轮距加大一倍，限速会怎样变化？", "How does the tipping speed in Table 2 depend on R? What happens to the limit if the track width doubles?")],
    "problem": ("AGV 转弯限速", "AGV cornering speed limit",
                "仓储 AGV 载货后质心高 h = 0.6 m，轮距 b = 0.5 m，轮胎与地面 μ = 0.6，通道转弯半径 1.5 m。(1) 分别求不打滑和不侧翻的最大速度，哪个先发生？(2) 若要求侧向加速度不超过 0.3g（保护货物），限速应是多少？(3) 为了让 AGV 在弯道更快，可以从哪些方面改进设计？",
                "A loaded warehouse AGV has h = 0.6 m, b = 0.5 m, μ = 0.6 and turns on a 1.5 m radius. (1) Find the maximum speed before sliding and before tipping. Which happens first? (2) If sideways acceleration must stay below 0.3g to protect the load, what is the limit? (3) How could the design be changed to corner faster?"),
    "everyday": ("高速公路弯道按侧向加速度不超过约 0.2g 设计。半径 500 m 的弯道，限速大约是多少 km/h？", "Highway curves are designed for sideways acceleration below about 0.2g. What is the speed limit for a 500 m curve, in km/h?"),
  },
  {
    "no": "1.5", "file": "实验1.5 相对运动（无人机侧风航线修正）",
    "zh": "相对运动：伽利略速度变换", "en": "Relative Motion: Galilean Velocity Addition",
    "goal": [("掌握速度矢量的合成 v(A 对 C) = v(A 对 B) + v(B 对 C)。", "Master vector velocity addition v(A rel. C) = v(A rel. B) + v(B rel. C)."),
             ("分析渡河的最短时间和最短航程。", "Analyse the shortest-time and shortest-path river crossings."),
             ("为无人机计算侧风下的航向修正。", "Compute the heading correction for a drone in a crosswind.")],
    "theory": [("船（或无人机）相对介质的速度 u、介质相对地面的速度 w，则对地速度 v = u + w。", "With velocity u relative to the medium and medium velocity w relative to the ground, the ground velocity is v = u + w."),
               ("船头垂直河岸时渡河时间最短：t = d/u，下游漂移 x = w·d/u。", "Pointing straight across gives the shortest time t = d/u, with downstream drift x = w·d/u."),
               ("要沿直线到达正对岸，须 u sinφ = w，即 sinφ = w/u（需 w < u）；此时对地速度 √(u² − w²)，时间 d/√(u² − w²)。", "To go straight across, u sinφ = w, so sinφ = w/u (requires w < u); the ground speed is √(u² − w²) and the time d/√(u² − w²).")],
    "env": [("场景", "Scene", "小船过河（河宽 100 m）；机器人：无人机侧风（目标正北 1 km）", "River (100 m wide); Robot: drone crosswind (target 1 km north)"),
            ("船速 / 空速", "Boat / air speed", "0.5 – 5 m/s；1 – 20 m/s", "0.5 – 5 m/s; 1 – 20 m/s"),
            ("水速 / 风速", "Current / wind", "0 – 5 m/s；0 – 15 m/s", "0 – 5 m/s; 0 – 15 m/s"),
            ("偏角 φ", "Heading φ", "−60° – 80°", "−60° – 80°")],
    "steps": [("“小船过河”，船速 2.0 m/s，水速 1.2 m/s。φ = 0 开船，记录渡河时间和下游漂移。", "River: boat 2.0 m/s, current 1.2 m/s. Go with φ = 0; record time and drift."),
              ("先用公式算出正对岸所需的 φ，再开船验证，填表 1。", "Compute φ for a straight crossing, then go and check; fill in Table 1."),
              ("把水速调到 2.5 m/s（大于船速），试着正对岸靠岸，记录结果。", "Set the current to 2.5 m/s (faster than the boat) and try to land straight across."),
              ("“机器人：无人机侧风”，空速 12 m/s，风速 5 m/s。先算 φ，再起飞，使到达点偏差不超过 10 m，填表 2。", "Robot: drone. Airspeed 12 m/s, wind 5 m/s. Compute φ, then fly so the miss is within 10 m; fill in Table 2.")],
    "tables": [
      ("表 1  小船过河（船速 2.0 m/s，水速 1.2 m/s，河宽 100 m） Table 1  River crossing", ["φ", "渡河时间 测 s", "渡河时间 算 s", "下游漂移 测 m", "下游漂移 算 m"],
       [["0°", "", "", "", ""], ["算出的 φ = ____°", "", "", "", ""]], [3.4, 2.8, 2.8, 2.8, 2.8]),
      ("表 2  无人机侧风（空速 12 m/s，风速 5 m/s，距离 1 km） Table 2  Drone crosswind", ["φ", "地速 m/s", "飞行时间 s", "到达点偏东 m"],
       [["0°", "", "", ""], ["算出的 φ = ____°", "", "", ""], ["实验找到的 φ = ____°", "", "", ""]], [4.2, 3.2, 3.2, 3.2]),
    ],
    "cautions": [("φ 为正表示偏向上游（迎风一侧）。", "Positive φ means turning upstream (into the wind)."),
                 ("虚线是按当前参数预测的航迹，可以先看预测再出发。", "The dashed line is the predicted path; check it before you go.")],
    "questions": [("水速大于船速时，能否正对岸靠岸？航程最短时船头应朝哪个方向？", "If the current is faster than the boat, can it land straight across? Which heading gives the shortest path?"),
                  ("侧风使无人机的飞行时间增加了多少？这对电池续航规划有什么影响？", "How much longer does the crosswind make the flight? What does that mean for battery planning?")],
    "problem": ("无人机侧风航线修正", "Drone crosswind correction",
                "巡检无人机空速 12 m/s，遇到 5 m/s 的东风侧风，要沿直线飞到正北 1 km 的目标。(1) 机头应向迎风一侧偏多少度？(2) 地速和飞行时间是多少？比无风时多用多少时间？(3) 若风速变为 15 m/s 会怎样？飞控系统应该怎么处理？",
                "An inspection drone flies at 12 m/s airspeed in a 5 m/s crosswind and must fly straight to a target 1 km north. (1) How many degrees into the wind must it head? (2) What are the ground speed and flight time? How much longer than in still air? (3) What if the wind rises to 15 m/s, and how should the flight controller respond?"),
    "everyday": ("飞机遇到侧风时机头会斜对跑道着陆（“蟹行”）。它和小船过河是同一个模型吗？", "Aircraft land in a crosswind with the nose angled off the runway (“crabbing”). Is this the same model as the river crossing?"),
  },
]

H = "大学物理A（上） · 第 1 章 质点运动学 · 虚拟实验"
HE = "University Physics A (I) · Chapter 1 · Virtual Lab"


def env_table(d, lab):
    d.table(["项目 Item", "范围 Range"], [[f"{a} {b}", f"{c}\n{e}"] for a, b, c, e in lab["env"]], widths=[4.5, 11.5], font_size=9.5)


def guide(lab):
    d = Doc()
    d.title(f"实验 {lab['no']}  {lab['zh']}", f"Lab {lab['no']}  {lab['en']}")
    d.en(f"{H}    {HE}", size=9)
    d.bh("一、实验目的", "1  Objectives")
    d.blist(lab["goal"], numbered=True)
    d.bh("二、实验原理", "2  Principles")
    for zh, en in lab["theory"]:
        d.bp(zh, en)
    d.bh("三、实验环境与参数范围", "3  Lab environment and parameter ranges")
    d.bp("本实验在问渠虚拟实验中完成，电脑和手机均可使用。", "The lab runs in the WenQuest virtual lab on a computer or phone.")
    d.en("入口 Access: " + LINK)
    env_table(d, lab)
    d.bh("四、实验步骤", "4  Procedure")
    d.blist(lab["steps"], numbered=True)
    d.bh("五、数据记录", "5  Data record")
    d.bp("以下表格同时出现在实验报告模板中，请在报告里填写。", "The same tables appear in the report template; fill them in there.")
    for cap, head, rows, widths in lab["tables"]:
        d.p(cap, indent=False)
        d.table(head, rows, widths=widths, font_size=9.5)
    d.bh("六、注意事项", "6  Notes")
    d.blist(lab["cautions"])
    d.bh("七、思考题", "7  Questions")
    d.blist(lab["questions"], numbered=True)
    t, te, q, qe = lab["problem"]
    d.bh("八、与实际问题的联系", "8  Connection to a real problem")
    d.p(f"机器人问题：{t}", indent=False).runs[0].bold = True
    d.en(f"Robot problem: {te}")
    d.bp(q, qe)
    d.bp("请在实验报告“实际问题的建模与求解”一栏中按五步完成：① 实际问题 ② 建立模型（写出简化假设）③ 求解 ④ 用虚拟实验检验 ⑤ 指出模型在哪里失效、怎样修正。",
         "In the report section “Modelling a real problem”, work through five steps: ① the problem ② the model (state your assumptions) ③ the solution ④ a check with the virtual lab ⑤ where the model fails and how to improve it.")
    d.p("生活中的例子：" + lab["everyday"][0], indent=False)
    d.en("Everyday example: " + lab["everyday"][1])
    d.save(GUIDES / f"{lab['file']} 实验指导书.docx")


SECTIONS = [
    ("一、实验目的", "1  Objectives", 3), ("二、实验原理（写出主要公式）", "2  Principles (key formulas)", 5),
    ("三、实验步骤（简要）", "3  Procedure (brief)", 4), ("四、数据记录与处理", "4  Data and processing", 0),
    ("五、结果与误差分析", "5  Results and error analysis", 6), ("六、实际问题的建模与求解", "6  Modelling a real problem", 0),
    ("七、结论", "7  Conclusion", 3), ("八、思考题", "8  Questions", 6),
]


def report(lab=None):
    d = Doc()
    if lab:
        d.title(f"实验报告  实验 {lab['no']}  {lab['zh']}", f"Lab Report  Lab {lab['no']}  {lab['en']}")
    else:
        d.title("虚拟实验报告（通用模板）", "Virtual Lab Report (general template)")
    d.table(["姓名 Name", "", "学号 ID", "", "日期 Date", ""], [["班级 Class", "", "同组 Partner", "", "成绩 Score", ""]],
            widths=[2.4, 3.2, 2.2, 2.8, 2.2, 3.2], font_size=10)
    d.en("提交方式：填写本模板后在问渠“作业”中上传；也可在问渠中在线填写同样的栏目。  Submit this file in WenQuest Assignments, or fill in the same sections online.", size=9)
    for zh, en, n in SECTIONS:
        d.bh(zh, en)
        if zh.startswith("四") and lab:
            for cap, head, rows, widths in lab["tables"]:
                d.p(cap, indent=False)
                d.table(head, rows, widths=widths, font_size=9.5)
            d.bp("数据处理：写出计算过程，至少完成一张图（如“误差—参数”或“测量值—理论值”）。", "Processing: show your calculations and include at least one graph (e.g. error vs parameter, or measured vs theory).")
            d.lines(4)
        elif zh.startswith("四"):
            d.bp("按实验指导书中的表格记录数据；写出计算过程，至少完成一张图。", "Record data in the tables from the lab guide; show your calculations and include at least one graph.")
            d.lines(8)
        elif zh.startswith("六"):
            if lab:
                t, te, q, qe = lab["problem"]
                d.p(f"问题：{t}", indent=False).runs[0].bold = True
                d.bp(q, qe)
            for step, en in [("① 实际问题（用自己的话描述，给出已知数据）", "① The problem (in your own words, with the given data)"),
                             ("② 建立模型（写出简化假设）", "② The model (state your assumptions)"),
                             ("③ 求解（公式与数值）", "③ Solution (formulas and numbers)"),
                             ("④ 用虚拟实验检验（写出实验设置与结果）", "④ Check with the virtual lab (settings and results)"),
                             ("⑤ 模型在哪里失效？怎样修正？", "⑤ Where does the model fail? How would you improve it?")]:
                d.p(step, indent=False)
                d.en(en)
                d.lines(3)
        elif zh.startswith("八") and lab:
            for zhq, enq in lab["questions"]:
                d.p(zhq, indent=False); d.en(enq); d.lines(3)
        else:
            d.lines(n)
    d.bh("九、AI 使用声明", "9  AI use statement")
    d.p("□ 未使用 AI　　□ 用 AI 解释概念　　□ 用 AI 检查计算　　□ 其他：____________", indent=False)
    d.en("□ No AI used   □ AI to explain concepts   □ AI to check calculations   □ Other: ____________")
    d.p("如使用了 AI，请写明用在哪里：", indent=False); d.lines(2)
    d.bh("评分量规", "Rubric")
    d.table(["项目 Criterion", "分值 Points", "要求 What earns full marks"],
            [["原理 Principles", "20", "公式正确、说明物理意义 / correct formulas with physical meaning"],
             ["数据 Data", "25", "数据完整、单位与有效数字规范 / complete data, correct units and significant figures"],
             ["分析 Analysis", "25", "理论与测量比较、误差来源分析 / theory vs measurement, sources of error"],
             ["实际问题 Real problem", "20", "五步完整，假设清楚，指出模型局限 / all five steps, clear assumptions, limits named"],
             ["规范 Presentation", "10", "书写清楚、图表规范、AI 使用如实声明 / clear writing and graphs, honest AI statement"]],
            widths=[4.0, 2.2, 9.8], font_size=9.5)
    d.en("AI 按本量规给出评分建议，教师复核后发布。  AI suggests a score against this rubric; the teacher reviews it before release.", size=9)
    name = f"实验{lab['no']} 实验报告模板.docx" if lab else "虚拟实验报告 通用模板.docx"
    d.save(REPORTS / name)


for lab in LABS:
    guide(lab)
    report(lab)
report(None)
print("guides and report templates written")
