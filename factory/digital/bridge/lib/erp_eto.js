// 按单设计（ETO，第 139 轮）在 ERPNext 里的写入：只用 ERPNext 自带单据，不改源码。
//   eto_quote：作业号 = Project；这一单专用的物料（编号 = 作业号，名称 = 客户要的东西）；报价单（自定义字段 wq_job 记作业号，
//              数量阶梯与付款条件写进条款）。重复执行时已有的 Project、物料不重建。
// 共有文件（问渠与 freecad-ai-parts 两边一样）；erp.js 加载后，方法里的 this 是 ERP 实例。
const erpToday = () => new Date().toISOString().slice(0, 10);

module.exports = () => ({
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
});
