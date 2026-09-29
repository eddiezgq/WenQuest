// 三坐标测量值 → ERPNext 质量检验单：一件零件的全部特性到齐后建一张，关联到“零件检验”工序的作业卡
const erp = global.get('wqErp');
const m = msg.payload;
if (!m || !m.data || m.mode !== erp.mode) return null;
erp.onMeasurement(m).then((out) => {
  if (out.length) node.status({ fill: 'green', shape: 'dot', text: m.data.part_serial + ' 检验单已建' });
  node.send([out]);
}).catch((e) => { node.status({ fill: 'red', shape: 'ring', text: e.message.slice(0, 50) }); node.error(e.message, msg); });
return null;
