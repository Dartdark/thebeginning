// Renders reports/business_plan_2026-10-30.html (business plan v3, rewritten 2026-10-30) to the PDF with the pre-installed
// Chromium. The HTML is the source: edit it, then run  node reports/render_business_plan.js
const { chromium } = require('playwright');
const path = require('path');
const SRC = 'file://' + path.resolve('reports/business_plan_2026-10-30.html');
const OUT = 'reports/Trading_Business_Plan_2026-10-30.pdf';
const FOOT = '<div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#8a93a6;width:100%;padding:0 0.6in;display:flex;' +
  'justify-content:space-between"><span>Algorithmic futures trading plan · v3 · October 30, 2026</span>' +
  '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>';
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto(SRC, { waitUntil: 'networkidle' });
  await pg.pdf({ path: OUT, format: 'Letter', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<div></div>', footerTemplate: FOOT });
  await b.close(); console.log('wrote', OUT);
})();
