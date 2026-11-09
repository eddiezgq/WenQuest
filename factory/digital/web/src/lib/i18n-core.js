// 第 130 轮：数字工厂英文版的纯函数部分（不依赖 Vue、不读文件），网页和测试脚本（web/tools/i18n_check.mjs）共用。
// 做法（细则 D-1）：页面上的中文原文就是“钥匙”，英文表里有就用英文，没有就显示中文——不会空白、不会报错。

// 站点定默认语言（同第 129 轮）：国内站 wenquestech.online 默认中文，其余（美国站、wenquestrobotics.com 各子域名、localhost）默认英文
export function siteLang(host) {
  return /(^|\.)wenquestech\.online$/i.test(String(host || '')) ? 'zh' : 'en';
}

const CJK = /[　-〿㐀-鿿＀-￯]/;
export const hasCjk = (s) => CJK.test(String(s ?? ''));

// {名字} 换成 vars 里的值；没给的保持原样
export function fill(s, vars) {
  if (!vars) return s;
  return s.replace(/\{(\w+)\}/g, (m, k) => (Object.prototype.hasOwnProperty.call(vars, k) && vars[k] != null ? String(vars[k]) : m));
}

// 精确查表；查不到再按“词组表”逐段替换（数据里带数字的句子，如 CAN 帧解释、判据读数），替换完还剩中文就整句退回中文
// phrases：[[中文, 英文], …]，长的先换
export function translate(zh, dict, phrases) {
  if (zh == null) return '';
  const s = String(zh);
  if (!hasCjk(s)) return s;
  const hit = dict[s];
  if (hit) return hit;
  if (phrases && phrases.length) {
    let out = s;
    for (const [a, b] of phrases) if (out.includes(a)) out = out.split(a).join(b);
    if (!hasCjk(out)) return out;
  }
  return s;
}

export function sortPhrases(list) {
  return [...list].sort((a, b) => b[0].length - a[0].length);
}

// 中英合写的名字（工厂清单里常见：“驱动板光板 4 层（外协） Drive board bare PCB”、“示例·传感器厂 Sensor Maker (Demo)”）取英文部分：
// 最后一个含中文的词之后的部分；开头的非字母词（规格、编号）在后面又出现过的去掉（“贴片电阻 0402 Chip resistor 0402” → “Chip resistor 0402”）
export function enPart(name) {
  const s = String(name ?? '').trim();
  if (!hasCjk(s)) return s;
  const toks = s.split(/\s+/);
  let last = -1;
  toks.forEach((t, i) => { if (hasCjk(t)) last = i; });
  let rest = toks.slice(last + 1);
  while (rest.length > 1 && rest.slice(1).includes(rest[0])) rest = rest.slice(1);
  return rest.join(' ');
}
