// Interface words in Chinese and English (round 39). The kernel sends its own words for checks and errors.
import { ref } from 'vue'

const saved = (() => { try { return localStorage.getItem('wqcam-lang') } catch { return null } })()
export const lang = ref(saved || (navigator.language?.startsWith('zh') ? 'zh' : 'en'))
export function setLang(l) { lang.value = l; try { localStorage.setItem('wqcam-lang', l) } catch { /* private mode */ } }

const W = {
  app: ['问渠凸轮', 'WenQuest Cam'],
  tagline: ['凸轮设计与制造', 'Cam design & manufacturing'],
  examples: ['示例', 'Examples'],
  newProject: ['新建', 'New'],
  open: ['打开文件', 'Open file'],
  save: ['保存为文件', 'Save as file'],
  report: ['计算书', 'Calculation sheet'],
  savedLocal: ['已自动保存在这台电脑的浏览器里', 'Saved automatically in this browser'],
  title: ['项目名称', 'Project name'],
  tabProgram: ['运动程序', 'Motion'],
  tabMech: ['机构', 'Mechanism'],
  tabLoads: ['载荷与材料', 'Loads & material'],
  tabLimits: ['校核限值', 'Limits'],
  kind: ['类型', 'Kind'], rise: ['升', 'Rise'], dwell: ['停', 'Dwell'], ret: ['回', 'Return'],
  angle: ['转角 °', 'Angle °'], lift: ['行程', 'Lift'], law: ['运动规律', 'Motion law'],
  addSeg: ['加一段', 'Add segment'], total: ['合计', 'Total'], useTable: ['用点表（转角, 位移）', 'Use a point table (angle, displacement)'],
  tableHint: ['每行一个点：转角(°), 位移；转角从 0 到 360 之间逐个增大', 'One point per line: angle (°), displacement; angles increasing within 0–360'],
  follower: ['从动件', 'Follower'], translating: ['直动', 'Translating'], oscillating: ['摆动', 'Oscillating'],
  contact: ['接触', 'Contact'], roller: ['滚子', 'Roller'], flat: ['平底', 'Flat face'], knife: ['尖顶', 'Knife edge'],
  rb: ['基圆半径 r_b', 'Base radius r_b'], rr: ['滚子半径 r_r', 'Roller radius r_r'], e: ['偏距 e', 'Offset e'],
  a: ['中心距 a', 'Centre distance a'], L: ['摆杆长 L', 'Arm length L'], sigma: ['凸轮转向', 'Cam turns'],
  ccw: ['逆时针', 'Counter-clockwise'], cw: ['顺时针', 'Clockwise'], groove: ['槽凸轮（形封闭）', 'Groove cam (form-closed)'],
  width: ['接触宽度 b', 'Contact width b'], findRb: ['求最小基圆', 'Find smallest base circle'],
  rpm: ['转速', 'Speed'], mass: ['从动件当量质量', 'Follower equivalent mass'], inertia: ['从动件对支点转动惯量', 'Follower inertia about pivot'],
  k: ['弹簧刚度', 'Spring rate'], preload: ['弹簧预压量（s = 0 时）', 'Spring preload (at s = 0)'], load: ['工作载荷', 'Working load'],
  matRoller: ['滚子（或平底）材料', 'Roller (or face) material'], matCam: ['凸轮材料', 'Cam material'], E: ['弹性模量 E', 'Young\'s modulus E'], nu: ['泊松比 ν', 'Poisson\'s ratio ν'],
  steel: ['填常用钢（E 206 GPa, ν 0.3）', 'Fill common steel (E 206 GPa, ν 0.3)'],
  steelNote: ['请按实际材料核对', 'Check against your actual material'],
  phiRise: ['推程许用压力角', 'Allowed pressure angle, rise'], phiReturn: ['回程许用压力角', 'Allowed pressure angle, return'],
  rhoMin: ['最小曲率半径要求', 'Minimum radius of curvature'], stress: ['许用接触应力', 'Allowed contact stress'], torque: ['许用驱动力矩', 'Allowed drive torque'],
  limitsNote: ['限值由企业按自己的规范填写；没填的项目结果是“未知”，不算合格。', 'Limits come from your own standards; anything left empty is “unknown”, never a pass.'],
  checks: ['校核', 'Checks'], overall: ['总体', 'Overall'],
  pass: ['合格', 'Pass'], fail: ['不合格', 'Fail'], unknown: ['未知', 'Unknown'], na: ['不适用', 'N/A'], info: ['—', '—'],
  play: ['播放', 'Play'], pause: ['暂停', 'Pause'], camAngle: ['凸轮转角', 'Cam angle'],
  s: ['位移 s', 'Displacement s'], v: ['类速度 ds/dθ', 'ds/dθ'], acc: ['类加速度 d²s/dθ²', 'd²s/dθ²'], j: ['类跃度 d³s/dθ³', 'd³s/dθ³'],
  vel: ['速度', 'Velocity'], accel: ['加速度', 'Acceleration'], phi: ['压力角', 'Pressure angle'], rho: ['实际廓线曲率半径', 'Profile radius of curvature'],
  force: ['压在凸轮上的力', 'Force on the cam'], torqueC: ['凸轮轴力矩', 'Camshaft torque'],
  computing: ['计算中…', 'Computing…'], error: ['出错了', 'Something is wrong'],
  fictional: ['示例参数为虚构，仅作演示', 'Example numbers are fictional, for demonstration'],
  print: ['打印 / 存为 PDF', 'Print / save as PDF'], back: ['返回', 'Back'],
  joints: ['接头冲击', 'Joints'], noJoints: ['各段之间速度、加速度都连续', 'Velocity and acceleration continuous at every joint'],
  pitch: ['理论廓线', 'Pitch curve'], profile: ['实际廓线', 'Profile'], base: ['基圆', 'Base circle'],
  speedNote: ['填了转速和质量才能算受力、跳离和接触应力', 'Give the speed and the mass to get forces, jump and contact stress'],
}

export function t(key) {
  const w = W[key]
  if (!w) return key
  return lang.value === 'zh' ? w[0] : w[1]
}
