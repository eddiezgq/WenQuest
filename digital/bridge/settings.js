// Node-RED 设置（问渠数字工厂桥接）。环境变量见 README：WQ_ERPNEXT_API、WQ_ERP_API_KEY、WQ_ERP_API_SECRET、
// WQ_MQTT_HOST、WQ_MQTT_PORT、WQ_MODE、WQ_TZ、WQ_HUB_PUBLIC_URL。
const path = require('path');
const { ERP } = require('./lib/erp');
const wq = require('./lib/wq');

module.exports = {
  uiPort: process.env.PORT || 1880,
  flowFile: path.join(__dirname, 'flows.json'),
  userDir: process.env.NODE_RED_USER_DIR || path.join(__dirname, '.node-red'),
  credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET || 'wq-digital-factory',
  flowFilePretty: true,
  functionGlobalContext: { wqErp: new ERP(), wq },
  logging: { console: { level: 'info', metrics: false, audit: false } },
  editorTheme: { projects: { enabled: false }, page: { title: '问渠数字工厂 · 桥接 Node-RED' } },
};
