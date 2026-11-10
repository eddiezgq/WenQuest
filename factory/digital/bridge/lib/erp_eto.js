// 按单设计（ETO，第 139 轮）在 ERPNext 里的写入：只用 ERPNext 自带单据，不改源码。
//   eto_quote：作业号 = Project；这一单专用的物料（编号 = 作业号，名称 = 客户要的东西）；报价单（自定义字段 wq_job 记作业号，
//              数量阶梯与付款条件写进条款）。重复执行时已有的 Project、物料不重建。
//   eto_order：销售订单（挂 Project、引用报价单，付款计划按里程碑）。
//   eto_release：设计发布——新物料、物料清单（带工序，子件先建）并设为默认；同一指纹的物料清单已有就不重建。
// 共有文件（问渠与 freecad-ai-parts 两边一样）；erp.js 加载后，方法里的 this 是 ERP 实例。
const erpToday = () => new Date().toISOString().slice(0, 10);

const WHK = { make: 'semi', buy: 'purchased', raw: 'raw' };

module.exports = ({ WH }) => ({
  async eto_quote(pv, { out, created, opt }) {
    const company = await this.getCompany();
    const customer = await this.customerFor(pv.quotation.party);
    await this.ensureCustomField('Quotation', 'wq_job', { label: '作业号 Job', fieldtype: 'Data', insert_after: 'party_name', read_only: 1 });
    const jobNo = pv.job.job_no;
    // 作业号 = Project（ERPNext 默认按项目名称命名）
    let proj = (await this.list('Project', [['project_name', '=', pv.project.project_name]], ['name']))[0];
    if (proj) {
      proj = await this.get('Project', proj.name);
    } else {
      proj = await this.insert('Project', { project_name: pv.project.project_name, company, customer, status: 'Open',
        ...(pv.project.expected_end_date ? { expected_end_date: pv.project.expected_end_date } : {}),
        notes: pv.project.notes || '' });
      out.push(this.doc('Project', proj, 'created', opt));
    }
    created.push(['Project', proj.name]);
    // 这一单专用的物料：设计发布前没有物料清单（第 139b 段补）
    const it = pv.item;
    let item;
    if ((await this.list('Item', [['name', '=', it.item_code]])).length) {
      item = await this.get('Item', it.item_code);
    } else {
      item = await this.insert('Item', { item_code: it.item_code, item_name: it.item_name, item_group: it.item_group,
        stock_uom: it.stock_uom || 'Nos', is_stock_item: 1, include_item_in_manufacturing: 1, description: it.description || it.item_name });
      out.push(this.doc('Item', item, 'created', opt));
    }
    created.push(['Item', item.name]);
    const q = pv.quotation;
    const qt = await this.insert('Quotation', { quotation_to: 'Customer', party_name: customer, company,
      transaction_date: q.transaction_date || erpToday(), valid_till: q.valid_till, order_type: 'Sales', wq_job: jobNo,
      terms: q.terms, items: [{ item_code: it.item_code, qty: q.qty, rate: q.rate }], docstatus: 1 });
    out.push(this.doc('Quotation', qt, 'submitted', opt));
    created.push(['Quotation', qt.name]);
  },

  async eto_order(pv, { out, created, opt }) {
    const company = await this.getCompany();
    const so = pv.sales_order;
    const customer = await this.customerFor(so.customer);
    const doc = await this.insert('Sales Order', { customer, company, transaction_date: so.transaction_date, delivery_date: so.delivery_date,
      order_type: 'Sales', project: so.project, docstatus: 1,
      items: [{ item_code: so.item_code, qty: so.qty, rate: so.rate, delivery_date: so.delivery_date, warehouse: WH.fg,
        ...(so.quotation ? { prevdoc_docname: so.quotation } : {}) }],
      ...((so.payment_schedule || []).length ? { payment_schedule: so.payment_schedule.map((p) => ({ due_date: p.due_date,
        invoice_portion: p.invoice_portion, payment_amount: p.payment_amount, description: p.description })) } : {}) });
    out.push(this.doc('Sales Order', doc, 'submitted', opt));
    created.push(['Sales Order', doc.name]);
  },

  async eto_release(pv, { out, created, opt }) {
    const company = await this.getCompany();
    await this.ensureCustomField('BOM', 'wq_fingerprint', { label: '设计指纹 Design fingerprint', fieldtype: 'Data', insert_after: 'item', read_only: 1 });
    for (const it of pv.items) {
      if ((await this.list('Item', [['name', '=', it.code]])).length) continue;
      const doc = await this.insert('Item', { item_code: it.code, item_name: it.name, item_group: it.item_group, stock_uom: it.uom,
        is_stock_item: 1, include_item_in_manufacturing: 1, description: `${it.name}（按单设计 ${pv.job.job_no}）`,
        is_purchase_item: it.kind === 'make' ? 0 : 1, default_material_request_type: it.kind === 'make' ? 'Manufacture' : 'Purchase',
        item_defaults: [{ company, default_warehouse: WH[WHK[it.kind]], ...(it.supplier ? { default_supplier: it.supplier } : {}) }],
        ...(it.supplier ? { supplier_items: [{ supplier: it.supplier }] } : {}),
        ...(it.price !== null && it.price !== undefined ? { valuation_rate: it.price } : {}),
        ...(it.lead ? { lead_time_days: it.lead } : {}) });
      out.push(this.doc('Item', doc, 'created', opt));
      created.push(['Item', doc.name]);
    }
    const made = {};
    for (const b of pv.boms) {        // 子件先建
      const have = await this.list('BOM', [['item', '=', b.item], ['wq_fingerprint', '=', pv.fingerprint], ['docstatus', '=', 1]], ['name']);
      if (have.length) {
        made[b.item] = have[0].name;
        // 已经建过（同一指纹）：只确保它是默认；也发一条回总线，提议照样有“执行完”的标记
        const doc = b.item === pv.job.job_no ? await this.update('BOM', have[0].name, { is_default: 1 }) : await this.get('BOM', have[0].name);
        out.push(this.doc('BOM', doc, 'updated', opt));
        created.push(['BOM', doc.name]);
        continue;
      }
      const items = [];
      for (const c of b.components) {
        const row = { item_code: c.item_code, qty: c.qty, uom: c.uom };
        if (made[c.item_code]) row.bom_no = made[c.item_code];
        else if (!c.new && (await this.list('BOM', [['item', '=', c.item_code], ['is_default', '=', 1], ['docstatus', '=', 1]], ['name'])).length) {
          row.bom_no = await this.defaultBom(c.item_code);
        }
        items.push(row);
      }
      const doc = await this.insert('BOM', { item: b.item, quantity: 1, company, is_active: 1, is_default: 1, with_operations: 1,
        rm_cost_as_per: 'Valuation Rate', wq_fingerprint: pv.fingerprint, project: pv.job.job_no,
        operations: b.operations.map((o, i) => ({ ...o, sequence_id: i + 1 })), items, docstatus: 1 });
      made[b.item] = doc.name;
      out.push(this.doc('BOM', doc, 'submitted', opt));
      created.push(['BOM', doc.name]);
    }
  },
});
