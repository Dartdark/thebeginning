'use strict';
/* Presentation only. Numeric fields and units are declared, never guessed from CSV names. */
const ResearchDesk = (() => {
  const configs = ['BASE', 'ADD', 'REPLACE', 'EMPTY'];
  const metrics = {
    personal: [
      ['annual', 'Mean annual profit', 'money'], ['dd95', 'Annual drawdown · p95', 'money'],
      ['capital', 'Capital at 20% DD', 'money'], ['return_dd', 'Mean profit / p95 DD', 'ratio'], ['sharpe', 'Sharpe', 'ratio']
    ],
    funded: [
      ['year1', 'Year-one payout', 'money'], ['year2', 'Two-year cumulative payout', 'money'],
      ['blown', 'Failure rate', 'percent'], ['days6', 'Days to six payouts', 'days'],
      ['delta_year1', 'Year-one change vs BASE', 'money'], ['lo', 'Change · 90% lower', 'money'], ['hi', 'Change · 90% upper', 'money']
    ],
    evaluations: [['pass_rate', '21-day pass rate', 'percent'], ['starts', 'Complete starts', 'count']]
  };
  const number = value => !['string','number'].includes(typeof value) || String(value).trim() === '' || !Number.isFinite(Number(value)) ? null : Number(value);
  function format(value, type) {
    const n = number(value);
    if (n === null) return 'Not recorded';
    if (type === 'money') return new Intl.NumberFormat('en-US', {style:'currency', currency:'USD', maximumFractionDigits:0}).format(n);
    if (type === 'percent') return (n * 100).toFixed(2) + '%';
    if (type === 'ratio') return n.toFixed(3);
    return n.toLocaleString('en-US', {maximumFractionDigits:0});
  }
  // Reject ambiguous duplicates and missing configurations, rather than pick an attractive row.
  function selectRows(rows, set, home, context, cohort) {
    const kind = home === 'personal' ? 'personal' : home.split('-')[0];
    const account = home.split('-')[1];
    return configs.map(config => {
      const matched = rows.filter(row => row.context === context && row.config === set.configurations[config]
        && (kind === 'personal' || row.account === account) && (kind !== 'evaluations' || row.cohort === cohort));
      return {config, row:matched.length === 1 ? matched[0] : null, issue:matched.length > 1 ? 'Ambiguous duplicate rows' : matched.length === 0 ? 'Not recorded' : ''};
    });
  }
  const label = value => String(value || 'Not recorded').replace(/_/g, ' ');
  const count = value => Number.isInteger(value) && value >= 0 ? value : '—';
  function stamp(value) {
    const parsed = new Date(value);
    return value && !Number.isNaN(parsed.getTime()) ? parsed.toLocaleString() : 'Not recorded';
  }
  function documentButton(path, title, cls='quiet') {
    return path ? `<button class="${cls}" data-doc="${esc(path)}">${esc(title)}</button>` : `<span class="muted">${esc(title)}: not recorded</span>`;
  }
  function issues(desk) {
    return (desk.issues || []).length ? `<div class="notice error" role="status"><strong>Some research status is unavailable.</strong><ul>${desk.issues.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>Refresh after correcting the saved files.</div>` : '';
  }
  function overview(data) {
    const desk = data.desk || {}, records = desk.records || [], program = desk.program || {};
    const reports = data.documents.filter(d => d.kind === 'results');
    const recent = [...reports].sort((a,b) => b.updated-a.updated).slice(0,5);
    const parked = records.filter(r => ['needs_data','needs_full_text'].includes(r.verdict)).length;
    const rejected = records.filter(r => r.verdict === 'design_reject').length;
    const comparisons = desk.comparisons || [];
    const used = program.economic_definitions, cap = program.max_economic_definitions;
    const remaining = Number.isInteger(used) && Number.isInteger(cap) ? Math.max(0, cap-used) : null;
    const dirty = data.modified === true ? 'Local edits present' : data.modified === false ? 'Clean checkout' : 'Checkout status unknown';
    $('#main').innerHTML = page('Research overview', 'Follow completed work, inspect the evidence, and decide what earns further review.', '<a class="button primary" href="#results">Inspect saved comparisons</a>') + issues(desk) + `
      <section class="desk-snapshot" aria-label="Local research snapshot">
        <div><span class="snapshot-label">Local checkout</span><strong>${esc(data.branch)} <code>${esc(data.commit)}</code></strong><span>${esc(dirty)} · Loaded ${esc(stamp(desk.loaded_at))}</span></div>
        <p>Pull GitHub changes, then refresh here. This page reads local files; scheduler status and trading accounts are not connected.</p>
      </section>
      <dl class="desk-totals">
        <div><dt>Saved research reports</dt><dd>${reports.length}</dd><small>Source reviews and completed outcomes</small></div>
        <div><dt>Scout analyst records</dt><dd>${records.length}</dd><small>${parked} parked for data or full text</small></div>
        <div><dt>Stopped at design</dt><dd>${rejected}</dd><small>Explicit scout records; not all repository trials</small></div>
        <div><dt>Definitions remaining</dt><dd>${count(remaining)}<span> / ${count(cap)}</span></dd><small>Saved scout budget; earlier trial history stays separate</small></div>
      </dl>
      <div class="desk-columns">
        <section class="panel review-desk"><div class="panel-head"><h2>Review desk</h2><a href="#strategies">Browse analyst records</a></div>
          ${comparisons.map(set=>`<article class="desk-review"><div class="record-top"><span class="badge watch">NO PLACEMENT</span><span class="kind">SAVED ACCOUNT TEST</span></div><h3>${esc(set.title)}</h3><p>${esc(set.outcome)}</p><p class="desk-caption">${esc(set.sample)}</p><a class="text-action" href="#results">Inspect all four configurations</a></article>`).join('') || '<p class="empty">No account comparison is registered yet. Browse the reports for existing research.</p>'}
          <div class="desk-next"><h3>Verification queue</h3><p>Unverified strategy leads, their prerequisites and the smallest next check. Parked leads stay available without interrupting compatible research.</p><a class="text-action" href="#queue">Read the queue</a></div>
        </section>
        <section class="panel"><div class="panel-head"><h2>Scout checkpoint</h2><a href="#scout">Open scout</a></div><div class="checkpoint">
          <dl><div><dt>Saved program status</dt><dd>${esc(label(program.status))}</dd></div><div><dt>Hypotheses started</dt><dd>${count(program.hypotheses_started)} / ${count(program.max_hypotheses)}</dd></div><div><dt>Definitions used</dt><dd>${count(used)} / ${count(cap)}</dd></div><div><dt>Saved lease</dt><dd>${program.lease_recorded === true ? 'Recorded · inspect progress' : program.lease_recorded === false ? 'None recorded' : 'Unknown'}</dd></div></dl>
          <p class="desk-caption">This is the saved progress record read from your checkout. “Ready” does not mean an analyst is currently running.</p>
          <a class="text-action" target="_blank" rel="noopener" href="${esc(safeURL('agents/codex/research/scout/progress.json'))}">Progress source on GitHub</a>
        </div></section>
      </div>
      <section class="panel recent-research"><div class="panel-head"><h2>Recently saved reports</h2><a href="#library">Search all research</a></div>
        <p class="section-note">Sorted by local file modification time. This may reflect a pull or checkout, rather than the research date.</p>
        ${recent.map(d=>`<article class="activity-row"><div><button class="document-title" data-doc="${esc(d.path)}">${esc(d.title)}</button><p>${esc(d.summary || d.path)}</p></div><span class="badge reference">SOURCE REPORT</span></article>`).join('') || '<div class="empty">No reports are available in this checkout.</div>'}
      </section>`;
    bindDocs();
  }
  function strategies(data) {
    const desk = data.desk || {}, records = desk.records || [];
    $('#main').innerHTML = page('Strategy research', 'Inspect saved analyst records and their exact evidence before opening the underlying reports.', '<a class="button" href="#library">All evidence, plans & reports</a>') + issues(desk) + `
      <div class="toolbar desk-filters"><label>Find a record<input id="candidate-search" type="search" placeholder="Title, SSRN ID or finding"></label><label>Saved disposition<select id="candidate-status"><option value="">All dispositions</option>${[...new Set(records.map(r=>r.verdict))].sort().map(s=>`<option value="${esc(s)}">${esc(label(s))}</option>`).join('')}</select></label></div>
      <p id="candidate-count" class="count" aria-live="polite"></p><div class="candidate-layout"><section class="panel candidate-list" id="candidate-list" aria-label="Analyst records"></section><section class="panel candidate-detail" id="candidate-detail" aria-label="Selected analyst record"></section></div>`;
    let selected = records[0]?.record_path;
    function detail(record) {
      if (!record) { $('#candidate-detail').innerHTML = '<div class="empty">No matching record. Change the search or disposition filter. The full document library remains available.</div>'; return; }
      const questions = [['What is it about?', 'about'], ['What does it find?', 'findings'], ['Why could it make money?', 'mechanism'], ['Can we build on it?', 'build_on'], ['Can strategy code be made?', 'code_feasibility']];
      $('#candidate-detail').innerHTML = `<div class="record-top"><span class="badge ${record.verdict === 'design_reject' || record.verdict === 'dont_test' ? 'reject' : 'reference'}">${esc(label(record.verdict))}</span><span class="kind">${esc(record.ssrn_id ? 'SSRN '+record.ssrn_id : record.id)}</span></div><h2>${esc(record.title)}</h2><p>${esc(record.summary || 'No summary recorded.')}</p>
        <p class="desk-caption">Record updated ${esc(stamp(record.updated_at))} · ${esc(label(record.evidence_level))}</p>
        <h3>Saved research stages</h3><ol class="stage-list"><li><strong>Source</strong><span>${record.full_text_read ? 'Full text read · scope in report' : 'Full-text reading not recorded'}</span></li><li><strong>Evidence</strong><span>${record.evidence_path ? 'Evidence file present' : 'Not recorded'}</span></li><li><strong>Preregistration</strong><span>${record.plan_path ? 'Plan file present · commit order not checked here' : 'Not recorded'}</span></li><li><strong>Design test</strong><span>${record.verdict === 'design_reject' ? 'Stopped at design · see report' : 'Not recorded here · see report'}</span></li><li><strong>Independent review</strong><span>${esc(label(record.independent_verification))}</span></li></ol>
        <p class="desk-caption">File presence is not gate acceptance. Stage outcomes that are absent from this record remain unknown.</p>
        <div class="desk-actions">${documentButton(record.report_path,'Read source report','primary')}${documentButton(record.evidence_path,'Evidence')}${documentButton(record.plan_path,'Plan')}</div>
        <details class="question-details"><summary>Five-question analysis</summary><div>${questions.map(([title,key],i)=>`<section><h3>${i+1}. ${title}</h3><p>${esc(record[key] || 'Not recorded. Consult the report; no answer is inferred.')}</p></section>`).join('')}</div></details>
        <p class="desk-caption">Source version: ${esc(record.source_revision || 'Not recorded')}</p><a class="text-action" target="_blank" rel="noopener" href="${esc(safeURL(record.record_path))}">Original JSON record on GitHub</a>`;
      bindDocs();
    }
    function draw() {
      const q = $('#candidate-search').value.toLowerCase(), status = $('#candidate-status').value;
      const filtered = records.filter(r => (!status || r.verdict === status) && [r.title,r.ssrn_id,r.summary].join(' ').toLowerCase().includes(q));
      if (!filtered.some(r=>r.record_path===selected)) selected = filtered[0]?.record_path;
      $('#candidate-count').textContent = `${filtered.length} / ${records.length} saved analyst records · Source claims and our test outcomes remain distinct`;
      $('#candidate-list').innerHTML = filtered.map(r=>`<button class="candidate-item" data-record="${esc(r.record_path)}" aria-pressed="${r.record_path===selected}"><span>${esc(r.title)}</span><small>${esc(r.ssrn_id ? 'SSRN '+r.ssrn_id+' · ' : '')}${esc(label(r.verdict))}</small></button>`).join('') || '<div class="empty">No matching records.</div>';
      detail(filtered.find(r=>r.record_path===selected));
      document.querySelectorAll('[data-record]').forEach(el=>{el.onclick=()=>{selected=el.dataset.record;draw();$('#candidate-detail').focus({preventScroll:true});};});
      $('#candidate-detail').tabIndex = -1;
    }
    $('#candidate-search').oninput = draw; $('#candidate-status').onchange = draw; draw();
  }
  function results(data, openRaw) {
    const sets = data.desk?.comparisons || [];
    $('#main').innerHTML = page('Strategy results', 'Compare saved account outcomes with their original sizing, costs and evidence limits.', '<button id="raw-results">Browse raw CSV files</button>') + issues(data.desk || {}) + `
      <div class="toolbar desk-filters"><label>Saved comparison<select id="comparison-set">${sets.map(s=>`<option value="${esc(s.id)}">${esc(s.title)}</option>`).join('')}</select></label><label>Candidate context<select id="comparison-context"></select></label><label>Account home<select id="comparison-home"><option value="personal">Personal</option><option value="funded-50">50K funded</option><option value="funded-150">150K funded</option><option value="evaluations-50">50K evaluation</option><option value="evaluations-150">150K evaluation</option></select></label><label id="cohort-control" hidden>Evaluation cohort<select id="comparison-cohort"><option value="all">All common dates</option><option value="recent">2023 onward</option></select></label></div><div id="comparison-body" aria-live="polite"></div>`;
    $('#raw-results').onclick = openRaw;
    if (!sets.length) { $('#comparison-body').innerHTML = '<div class="empty">No comparison has a registered source report. Browse raw CSV files to inspect other saved outputs; units are preserved there.</div>'; return; }
    let generation=0;
    async function draw(reset=false) {
      const id=++generation, set=sets.find(s=>s.id===$('#comparison-set').value);
      if (reset) $('#comparison-context').innerHTML = set.contexts.map(c=>`<option>${esc(c)}</option>`).join('');
      const home=$('#comparison-home').value, kind=home==='personal' ? 'personal' : home.split('-')[0], context=$('#comparison-context').value, cohort=$('#comparison-cohort').value;
      $('#cohort-control').hidden = kind !== 'evaluations';
      $('#comparison-body').innerHTML = '<div class="loading">Reading the saved comparison…</div>';
      const body=$('#comparison-body');
      const current=()=>id===generation && $('#comparison-body')===body;
      let rows=[], error='';
      if (!set.files[kind]) error='This account output is unavailable. No results have been inferred.';
      else try { const x=await api('/api/result?path='+encodeURIComponent(set.files[kind])); if(x.truncated) throw Error('The saved file exceeds the viewer limit. Read the source CSV for a complete comparison.'); rows=x.rows; } catch(e) { error=e.message; }
      if(!current()) return;
      const selected=selectRows(rows,set,home,context,cohort), fields=metrics[kind];
      $('#comparison-body').innerHTML = `
        <section class="comparison-verdict"><div><span class="badge watch">${esc(set.id === 'primesync-accounts' ? 'NO PLACEMENT' : 'SAVED RESULT')}</span><h2>${esc(set.title)}</h2><p>${esc(set.outcome)}</p></div>${documentButton(set.report_path,'Read full report','primary')}</section>
        <dl class="comparison-provenance"><div><dt>History & sizing</dt><dd>${esc(set.sample)}<br>${esc(set.sizing)}</dd></div><div><dt>Execution costs</dt><dd>${esc(set.costs)}</dd></div></dl>
        <section class="panel comparison-panel"><div class="panel-head"><h2>${esc(context)} · ${esc($('#comparison-home').selectedOptions[0].textContent)}${kind==='evaluations' ? ' · '+esc($('#comparison-cohort').selectedOptions[0].textContent) : ''}</h2><span class="kind">USD UNLESS LABELED</span></div>
          ${error?`<div class="notice error" role="alert">${esc(error)} <button id="comparison-retry">Retry loading</button></div>`:''}
          <div class="table-wrap" tabindex="0" role="region" aria-label="Account comparison; scroll horizontally for all configurations"><table class="comparison-table"><caption>BASE / ADD / REPLACE / EMPTY · ${esc(set.comparison_note)}</caption><thead><tr><th scope="col">Saved metric</th>${selected.map(x=>`<th scope="col">${x.config}</th>`).join('')}</tr></thead><tbody>${fields.map(([key,title,type])=>`<tr><th scope="row">${esc(title)}</th>${selected.map(x=>`<td>${esc(x.issue || format(x.row?.[key],type))}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
          <p class="section-note">${esc(kind==='funded' ? 'Two-year payout includes year one. Failure rates and payout timing are simulation outputs, conditional on the recorded history.' : kind==='personal' ? 'Profit and p95 drawdown come from paired annual simulations. Capital = p95 drawdown / 20%; it is a modeled requirement.' : 'Complete historical 21-day starts; a pass rate is not a forecast for a newly purchased account.')}</p>
        </section>
        <section class="comparison-evidence"><h3>Verification & limitations</h3><p>${esc(set.verification)}</p><p>${esc(set.limits)}</p><details><summary>Method and original artifacts</summary><p>${esc(set.method)}</p><p>${esc(set.comparison_note)}</p><div class="desk-actions">${documentButton(set.plan_path,'Read preregistration')}<a class="text-action" target="_blank" rel="noopener" href="${esc(safeURL(set.files[kind] || set.report_path))}">Original ${set.files[kind]?'CSV':'report'} on GitHub</a></div></details></section>`;
      bindDocs(); if($('#comparison-retry')) $('#comparison-retry').onclick=()=>draw();
    }
    $('#comparison-set').onchange=()=>draw(true);
    ['#comparison-context','#comparison-home','#comparison-cohort'].forEach(s=>$(s).onchange=()=>draw());
    draw(true);
  }
  return {overview,strategies,results,format,selectRows};
})();
if(typeof module !== 'undefined') module.exports=ResearchDesk;
