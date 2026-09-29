// FreeCAD 发布 → ERPNext：物料版本号加一；BOM 用量变了就建新版 BOM；STEP、图纸、G 代码作为附件挂到物料上
const erp = global.get('wqErp');
const m = msg.payload;
if (!m || !m.data || m.mode !== erp.mode) return null;
const job = m.type === 'design.release' ? erp.onRelease(m) : erp.onGcode(m);
job.then((out) => {
  node.status({ fill: 'green', shape: 'dot', text: m.data.item + ' rev ' + m.data.revision });
  node.send([out]);
}).catch((e) => { node.status({ fill: 'red', shape: 'ring', text: e.message.slice(0, 50) }); node.error(e.message, msg); });
return null;
