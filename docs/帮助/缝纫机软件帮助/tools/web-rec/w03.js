const { clip } = require('./rec.js');
clip('web-03-ai', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await r.sewing(); await r.wait(2500);
  r.cue('“AI 助手”：一句话提要求，AI 起草，计算核心把关（本录像是没配大模型时的规则版，把关一样）');
  await p.locator('.ai .bar').click(); await r.wait(2500);
  await r.type(p.locator('.ai textarea'), '转速提到 6000');
  r.cue('只提转速：起草出来，计算核心重算——红灯多了，没通过'); await p.getByText('起草改法').click(); await r.wait(5000);
  await r.type(p.locator('.ai textarea'), '转速 6000，针杆组件质量 0.10，机壳一阶固有频率 240');
  r.cue('把针杆减轻、机壳做刚也写上：这回通过了，改前改后对照着看'); await p.getByText('起草改法').click(); await r.wait(5000);
  r.cue('点“采用”，才真正回填参数并重算'); await p.getByText('采用（回填参数并重算）').click(); await r.wait(3500);
  r.cue('“解释红黄灯”：先把旋梭定时调错，看它怎么讲'); await r.param('钩线机构', '旋梭定时', -20); await r.wait(800);
  await p.locator('.ai').scrollIntoViewIfNeeded(); await p.getByText('解释红黄灯').click(); await r.wait(5500);
  r.cue('“写设计说明”：说明里的每个数都由程序核对过，可以放进计算书'); await r.param('钩线机构', '旋梭定时', 0);
  await p.locator('.ai').scrollIntoViewIfNeeded(); await p.getByText('写设计说明').click(); await r.wait(3500);
  await p.getByText('放进计算书').click(); await r.wait(3000);
});
