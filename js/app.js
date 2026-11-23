/* AI热榜导航 · 交互逻辑（纯前端，无依赖） */
'use strict';

const SITES = window.SITES || [];
const STATS = window.STATS || {};

/* ───────── 分类定义 ───────── */
const ICONS = {
  all: '<path fill="currentColor" d="M3 3h8v8H3zm10 0h8v8h-8zM3 13h8v8H3zm10 0h8v8h-8z"/>',
  daily: '<path fill="currentColor" d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2zM7 7h10v2H7zm0 4h10v2H7zm0 4h6v2H7z"/>',
  github: '<path fill="currentColor" d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.55 0-.27-.01-1.17-.02-2.12-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.03 1.76 2.69 1.25 3.35.96.1-.75.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.04 0 0 .96-.31 3.15 1.18a10.9 10.9 0 0 1 5.78 0c2.19-1.49 3.15-1.18 3.15-1.18.62 1.58.23 2.75.11 3.04.73.81 1.18 1.83 1.18 3.09 0 4.42-2.7 5.39-5.28 5.67.41.36.78 1.06.78 2.14 0 1.54-.01 2.79-.01 3.17 0 .3.2.67.8.55A11.5 11.5 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z"/>',
  trending: '<path fill="currentColor" d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 14V6z"/>',
  research: '<path fill="currentColor" d="M12 3 1 9l4 2.18v6L12 21l7-3.82v-6l2-1.09V17h2V9L12 3z"/>',
  llm: '<path fill="currentColor" d="M20 9V7a2 2 0 0 0-2-2h-2.2A3 3 0 0 0 13 2h-2a3 3 0 0 0-2.8 3H6a2 2 0 0 0-2 2v2a3 3 0 0 0-1 2.24V15a3 3 0 0 0 2 2.83V20a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2.17A3 3 0 0 0 22 15v-3.76A3 3 0 0 0 20 9zM9.5 12.5A1.5 1.5 0 1 1 11 14a1.5 1.5 0 0 1-1.5-1.5zm5 0A1.5 1.5 0 1 1 16 14a1.5 1.5 0 0 1-1.5-1.5z"/>',
  nav: '<path fill="currentColor" d="M12 10.9a1.1 1.1 0 1 0 1.1 1.1 1.1 1.1 0 0 0-1.1-1.1zM12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm4.24 14.24-6-2.3 2.3-6 6 2.3z"/>',
  benchmark: '<path fill="currentColor" d="M5 20h3v-8H5zm5.5 0h3V5h-3zM16 20h3v-13h-3z"/>',
  media: '<path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11z"/>',
  resource: '<path fill="currentColor" d="M21 5c-1.11-.35-2.33-.5-3.5-.5-1.95 0-4.05.4-5.5 1.5-1.45-1.1-3.55-1.5-5.5-1.5S2.45 4.9 1 6v14.65c0 .25.25.5.5.5.1 0 .15-.05.25-.05C3.1 20.45 5.05 20 6.5 20c1.95 0 4.05.4 5.5 1.5 1.35-.85 3.8-1.5 5.5-1.5 1.65 0 3.35.3 4.75 1.05.1.05.15.05.25.05.25 0 .5-.25.5-.5V6c-.6-.45-1.25-.75-2-1zM12 18.5l-5-1.46V7.3l5 1.47zm6-1.46-4 1.17V8.77l4-1.17z"/>',
  community: '<path fill="currentColor" d="M16 11a3 3 0 1 0-3-3 3 3 0 0 0 3 3zm-8 0a3 3 0 1 0-3-3 3 3 0 0 0 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h9v-2.5c0-.85.3-1.63.83-2.3A11 11 0 0 0 8 13zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5C23 14.17 18.33 13 16 13z"/>'
};

const CATEGORIES = [
  { id: 'all',       label: '全部',           icon: 'all' },
  { id: 'daily',     label: 'AI日报 · 资讯',   icon: 'daily' },
  { id: 'github',    label: 'GitHub 高星开源', icon: 'github' },
  { id: 'trending',  label: 'GitHub趋势榜',    icon: 'trending' },
  { id: 'research',  label: '学术 · 前沿实验室', icon: 'research' },
  { id: 'llm',       label: '大模型平台',       icon: 'llm' },
  { id: 'nav',       label: 'AI导航 · 工具',   icon: 'nav' },
  { id: 'benchmark', label: '评测 · 榜单',      icon: 'benchmark' },
  { id: 'media',     label: '科技媒体',        icon: 'media' },
  { id: 'resource',  label: '提示词 · 知识库',  icon: 'resource' },
  { id: 'community', label: '开发者社区',      icon: 'community' },
];

const PAGE_SIZE = 48;
const $ = (s, p) => (p || document).querySelector(s);
const $$ = (s, p) => Array.from((p || document).querySelectorAll(s));
const fmtStars = n => n >= 1e6 ? (n / 1e6).toFixed(2) + 'M' : n >= 1e3 ? (n / 1e3).toFixed(1) + 'k' : String(n || 0);
const fmtInt = n => (n || 0).toLocaleString('en-US');
const escHtml = s => String(s).replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
const escReg = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const domainOf = url => { try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return url; } };
const faviconOf = url => {
  try {
    const u = new URL(url);
    const host = u.hostname.toLowerCase();
    if (host === 'github.com') {
      const parts = u.pathname.split('/').filter(Boolean);
      if (parts.length >= 2) return 'https://github.com/' + encodeURIComponent(parts[0]) + '.png?size=64';
    }
    return 'https://www.google.com/s2/favicons?domain=' + encodeURIComponent(host.replace(/^www\./, '')) + '&sz=64';
  } catch { return ''; }
};

/* ───────── 状态 ───────── */
const state = {
  mode: 'nav',
  q: '',
  cat: 'all',
  region: 'all',
  source: 'all',
  sort: 'score',
  view: localStorage.getItem('aihn_view') || 'grid',
  shown: PAGE_SIZE,
};

/* ───────── 主题切换 ───────── */
(function initTheme() {
  const saved = localStorage.getItem('aihn_theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.dataset.theme = saved || (prefersDark ? 'dark' : 'light');
})();
$('#themeToggle').addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('aihn_theme', next);
});

/* ───────── Hero 统计 ───────── */
(function fillStats() {
  const total = STATS.total || SITES.length;
  const gh = STATS.github || SITES.filter(s => s.source === 'GitHub').length;
  const curated = STATS.curated || (total - gh);
  $('#heroStats').innerHTML = [
    [fmtInt(total), '收录站点'],
    [fmtInt(curated), '人工精选'],
    [fmtInt(gh), 'GitHub 高星开源'],
    ['32.3M+', '累计 Stars'],
  ].map(([n, l]) => `<span class="stat-pill"><span class="stat-num">${n}</span><span class="stat-label">${l}</span></span>`).join('');
  $('#ftTotal').textContent = fmtInt(total);
})();

/* ───────── 分类 Chips ───────── */
const catCounts = SITES.reduce((m, s) => { m[s.cat] = (m[s.cat] || 0) + 1; return m; }, {});
$('#chipsRow').innerHTML = CATEGORIES.map(c => {
  const n = c.id === 'all' ? SITES.length : (catCounts[c.id] || 0);
  return `<button class="chip${c.id === 'all' ? ' is-active' : ''}" data-cat="${c.id}" role="tab" aria-selected="${c.id === 'all'}">
    <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">${ICONS[c.icon]}</svg>${escHtml(c.label)}<span class="chip-count">${fmtInt(n)}</span>
  </button>`;
}).join('');

/* 页脚分类速达 */
$('#footerCats').innerHTML = CATEGORIES.filter(c => c.id !== 'all')
  .map(c => `<button data-cat="${c.id}">${escHtml(c.label)}</button>`).join('');

/* ───────── 过滤 + 排序 ───────── */
const SORTERS = {
  score:   (a, b) => b.score - a.score || b.heat - a.heat,
  heat:    (a, b) => b.heat - a.heat || b.score - a.score,
  quality: (a, b) => b.quality - a.quality || b.score - a.score,
  stars:   (a, b) => (b.stars || 0) - (a.stars || 0) || b.score - a.score,
  updated: (a, b) => String(b.updated || '').localeCompare(String(a.updated || '')) || (b.stars || 0) - (a.stars || 0),
};

function getFiltered() {
  const tokens = state.q.toLowerCase().split(/\s+/).filter(Boolean);
  let out = SITES.filter(s => {
    if (state.cat !== 'all' && s.cat !== state.cat) return false;
    if (state.region !== 'all' && s.region !== state.region) return false;
    if (state.source !== 'all' && s.source !== state.source) return false;
    if (!tokens.length) return true;
    const hay = (s.name + ' ' + s.desc + ' ' + (s.tags || []).join(' ') + ' ' + (s.subcat || '') + ' ' + domainOf(s.url)).toLowerCase();
    return tokens.every(t => hay.includes(t));
  });
  out.sort(SORTERS[state.sort] || SORTERS.score);
  return out;
}

function highlight(text) {
  const tokens = state.q.toLowerCase().split(/\s+/).filter(Boolean);
  let html = escHtml(text);
  for (const t of tokens) {
    if (!t) continue;
    html = html.replace(new RegExp('(' + escReg(escHtml(t)) + ')', 'gi'), '<mark>$1</mark>');
  }
  return html;
}

/* ───────── 卡片渲染 ───────── */
const heatPill = h => h >= 85 ? `<span class="pill pill-heat-high" title="热度评分">🔥 ${h}</span>`
                    : h >= 70 ? `<span class="pill pill-heat-mid" title="热度评分">🔥 ${h}</span>`
                    : `<span class="pill pill-heat-low" title="热度评分">🔥 ${h}</span>`;
const qualityPill = q => q >= 82 ? `<span class="pill pill-quality-high" title="质量评分">✓ ${q}</span>`
                       : `<span class="pill pill-quality-mid" title="质量评分">✓ ${q}</span>`;
const regionPill = r => r === 'cn'
  ? '<span class="pill pill-region">🇨🇳 中文圈</span>'
  : '<span class="pill pill-region">🌍 全球</span>';

function cardHtml(s) {
  const domain = domainOf(s.url);
  const initial = escHtml((s.name || '?').trim().charAt(0).toUpperCase());
  const gh = s.source === 'GitHub';
  const sourceBadge = gh
    ? `<span class="card-source gh">GitHub</span>`
    : `<span class="card-source curated">精选</span>`;
  const starsHtml = s.stars > 0
    ? `<span class="stars" title="GitHub Stars">★ ${fmtStars(s.stars)}</span>`
    : '';
  const subcatHtml = s.subcat ? `<span class="pill pill-subcat" title="${escHtml(s.subcat)}">${escHtml(s.subcat)}</span>` : '';
  return `
  <a class="card" href="${escHtml(s.url)}" target="_blank" rel="noopener noreferrer" data-id="${s.id}">
    <button class="copy-btn" data-copy="${escHtml(s.url)}" aria-label="复制链接" title="复制链接">
      <svg viewBox="0 0 24 24" width="15" height="15"><path fill="currentColor" d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H8V7h11z"/></svg>
    </button>
    <div class="card-top">
      <img class="favicon" src="${faviconOf(s.url)}" alt="" loading="lazy" width="34" height="34"
           onerror="this.outerHTML='<span class=&quot;favicon-fallback&quot;>${initial}</span>'" />
      <div style="min-width:0">
        <div class="card-name" title="${escHtml(s.name)}">${highlight(s.name)}</div>
        <div class="card-domain">${escHtml(domain)}</div>
      </div>
      ${sourceBadge}
    </div>
    <p class="card-desc">${highlight(s.desc)}</p>
    <div class="card-foot">
      ${heatPill(s.heat)}${qualityPill(s.quality)}${regionPill(s.region)}${subcatHtml}${starsHtml}
    </div>
  </a>`;
}

function render() {
  const filtered = getFiltered();
  const grid = $('#cardsGrid');
  grid.classList.toggle('list-mode', state.view === 'list');
  const slice = filtered.slice(0, state.shown);
  grid.innerHTML = slice.map(cardHtml).join('');

  $('#resultCount').textContent = `共 ${fmtInt(filtered.length)} 个结果`;
  const hints = [];
  if (state.cat !== 'all') hints.push('分类：' + (CATEGORIES.find(c => c.id === state.cat) || {}).label);
  if (state.q) hints.push(`关键词：${state.q}`);
  if (state.region !== 'all') hints.push(state.region === 'cn' ? '中文圈' : '全球');
  if (state.source !== 'all') hints.push(state.source);
  $('#resultHint').textContent = hints.length ? '· ' + hints.join(' · ') : '按热度 × 质量排序推荐';

  $('#emptyState').hidden = filtered.length !== 0;
  $('#loadMoreBtn').hidden = state.shown >= filtered.length;
  $('#loadMoreBtn').textContent = state.shown >= filtered.length ? '没有更多了' : `加载更多（剩余 ${fmtInt(filtered.length - state.shown)}）`;
  return filtered.length;
}

/* ───────── 事件绑定 ───────── */
const searchInput = $('#searchInput');
const clearBtn = $('#clearBtn');
let searchTimer = null;
searchInput.addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.q = searchInput.value.trim();
    state.shown = PAGE_SIZE;
    clearBtn.hidden = !state.q;
    $('#hero').classList.toggle('is-collapsed', !!state.q);
    render();
  }, 120);
});
clearBtn.addEventListener('click', () => { searchInput.value = ''; state.q = ''; state.shown = PAGE_SIZE; clearBtn.hidden = true; $('#hero').classList.remove('is-collapsed'); render(); searchInput.focus(); });

$('#chipsRow').addEventListener('click', e => {
  const btn = e.target.closest('.chip'); if (!btn) return;
  state.cat = btn.dataset.cat; state.shown = PAGE_SIZE;
  $$('.chip').forEach(c => { const on = c === btn; c.classList.toggle('is-active', on); c.setAttribute('aria-selected', on); });
  render();
});
$('#footerCats').addEventListener('click', e => {
  const btn = e.target.closest('button[data-cat]'); if (!btn) return;
  state.cat = btn.dataset.cat; state.shown = PAGE_SIZE;
  $$('.chip').forEach(c => c.classList.toggle('is-active', c.dataset.cat === state.cat));
  window.scrollTo({ top: 0, behavior: 'smooth' });
  render();
});

$('#sortGroup').addEventListener('click', e => {
  const btn = e.target.closest('.sort-btn'); if (!btn) return;
  state.sort = btn.dataset.sort; state.shown = PAGE_SIZE;
  $$('.sort-btn').forEach(b => b.classList.toggle('is-active', b === btn));
  render();
});
$('#regionSelect').addEventListener('change', e => { state.region = e.target.value; state.shown = PAGE_SIZE; render(); });
$('#sourceSelect').addEventListener('change', e => { state.source = e.target.value; state.shown = PAGE_SIZE; render(); });

$('#gridViewBtn').addEventListener('click', () => setView('grid'));
$('#listViewBtn').addEventListener('click', () => setView('list'));
function setView(v) {
  state.view = v; localStorage.setItem('aihn_view', v);
  $('#gridViewBtn').classList.toggle('is-active', v === 'grid');
  $('#listViewBtn').classList.toggle('is-active', v === 'list');
  render();
}
$('#gridViewBtn').classList.toggle('is-active', state.view === 'grid');
$('#listViewBtn').classList.toggle('is-active', state.view === 'list');

$('#heroCollapse').addEventListener('click', () => $('#hero').classList.add('is-collapsed'));
$('#resetFilters').addEventListener('click', () => {
  state.q = ''; state.cat = 'all'; state.region = 'all'; state.source = 'all'; state.sort = 'score'; state.shown = PAGE_SIZE;
  searchInput.value = ''; clearBtn.hidden = true;
  $('#regionSelect').value = 'all'; $('#sourceSelect').value = 'all';
  $$('.chip').forEach(c => c.classList.toggle('is-active', c.dataset.cat === 'all'));
  $$('.sort-btn').forEach(b => b.classList.toggle('is-active', b.dataset.sort === 'score'));
  $('#hero').classList.remove('is-collapsed');
  render();
});
$$('.suggest').forEach(b => b.addEventListener('click', () => { searchInput.value = b.dataset.q; state.q = b.dataset.q; state.shown = PAGE_SIZE; clearBtn.hidden = false; render(); }));

$('#loadMoreBtn').addEventListener('click', () => { state.shown += PAGE_SIZE; render(); });
const io = new IntersectionObserver(entries => {
  if (entries[0].isIntersecting && !$('#loadMoreBtn').hidden) { state.shown += PAGE_SIZE; render(); }
}, { rootMargin: '400px' });
io.observe($('#sentinel'));

/* 复制链接 + Toast */
const toastEl = $('#toast');
let toastTimer = null;
function showToast(msg) {
  toastEl.textContent = msg; toastEl.classList.add('is-show');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => toastEl.classList.remove('is-show'), 2200);
}
document.addEventListener('click', e => {
  const btn = e.target.closest('.copy-btn'); if (!btn) return;
  e.preventDefault(); e.stopPropagation();
  const url = btn.dataset.copy;
  const done = () => showToast('链接已复制到剪贴板 ✓');
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done).catch(done);
  else { const ta = document.createElement('textarea'); ta.value = url; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); } catch (_) {} ta.remove(); done(); }
});

/* 键盘快捷键 */
document.addEventListener('keydown', e => {
  const tag = (e.target.tagName || '').toLowerCase();
  const typing = tag === 'input' || tag === 'select' || tag === 'textarea';
  if (e.key === '/' && !typing) { e.preventDefault(); searchInput.focus(); }
  else if (e.key === 'Escape') {
    if (!modelModal.hidden) { closeModelModal(); }
    else if (!$('#topModal').hidden) { closeTop(); }
    else if (typing) { e.target.blur(); }
    else if (state.q) { searchInput.value = ''; state.q = ''; state.shown = PAGE_SIZE; clearBtn.hidden = true; $('#hero').classList.remove('is-collapsed'); render(); }
  }
});

/* ───────── 视图切换（导航 / AI 日报） ───────── */
function setViewMode(mode) {
  state.mode = mode;
  const isDigest = mode === 'digest';
  const isAgent = mode === 'agent';
  $('#digestView').hidden = !isDigest;
  $('#agentView').hidden = !isAgent;
  $('#viewNav').hidden = isDigest || isAgent;
  $('#chipsRow').style.display = (isDigest || isAgent) ? 'none' : '';
  $('#digestToggle').setAttribute('aria-pressed', String(isDigest));
  $('#agentToggle').setAttribute('aria-pressed', String(isAgent));
  document.body.dataset.view = mode;
  if (isDigest && !digestLoaded) loadDigest('data/digest.json');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
let digestLoaded = false;
let digestState = { current: null, history: [] };

/* ───────── AI 日报渲染 ───────── */
const IMPACT_TXT = { high: 'HIGH', medium: 'MED', low: 'LOW' };
function esc(s) { return escHtml(s == null ? '' : String(s)); }

function renderDigest(d) {
  $('#digestTitle').textContent = d.title || `AI热榜日报 · ${d.date || ''}`;
  $('#digestOverview').textContent = d.overview || '';
  $('#digestMeta').textContent = `AI热榜日报 · ${d.model || '模型生成'} · 生成于 ${(d.generated_at || '').replace('T', ' ')}`;
  const usage = d.usage && d.usage.total_tokens ? ` · ${fmtInt(d.usage.total_tokens)} tokens` : '';
  $('#digestStats').innerHTML = [
    [`<b>${esc(d.date || '—')}</b>`, '日报日期'],
    [`<b>${fmtInt(d.item_count || 0)}</b>`, '条目'],
    [`<b>${(d.sections || []).length}</b>`, '板块'],
    [`<b>${esc(d.model || '—')}</b>`, '生成模型'],
  ].map(([b, l]) => `<span class="digest-chip">${b}<span>${l}</span></span>`).join('') + (usage ? `<span class="digest-chip">${usage}</span>` : '');

  const sections = (d.sections || []).map(sec => `
    <section class="digest-section">
      <h3 class="digest-section-title"><span class="bar"></span>${esc(sec.title)}<span class="chip-count">${(sec.items || []).length}</span></h3>
      ${(sec.items || []).map(it => `
        <a class="digest-item" href="${esc(it.url)}" target="_blank" rel="noopener noreferrer">
          <span class="digest-impact ${esc(it.impact || 'low')}" aria-hidden="true"></span>
          <span>
            <span class="digest-item-title">${esc(it.title)}</span>
            <span class="digest-item-liner">${esc(it.one_liner || '')}</span>
            <span class="digest-item-source">${esc(it.source || '')} · ${esc(domainOf(it.url))}</span>
          </span>
          <span class="digest-impact-tag ${esc(it.impact || 'low')}">${IMPACT_TXT[it.impact] || 'LOW'}</span>
        </a>`).join('')}
    </section>`).join('');
  $('#digestSections').innerHTML = sections || '<p class="digest-error">日报为空</p>';

  // 更新模型配置弹窗里的“上次生成”
  const cfgLastGen = $('#cfgLastGen');
  if (cfgLastGen) cfgLastGen.textContent = `${d.generated_at ? d.generated_at.replace('T', ' ') : '—'} · ${d.model || ''}${usage}`;
  digestLoaded = true;
  digestState.current = d;
  window.__LATEST_DIGEST = d;
}

function renderDigestHistory() {
  const wrap = $('#digestHistory');
  if (!digestState.history.length) { wrap.innerHTML = ''; return; }
  wrap.innerHTML = '<span class="digest-history-label">往期：</span>' + digestState.history.slice(0, 14)
    .map(date => `<button class="digest-date${digestState.current && digestState.current.date === date ? ' is-active' : ''}" data-date="${esc(date)}">${esc(date)}</button>`).join('');
}

async function loadDigest(url, isHistory) {
  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const d = await res.json();
    renderDigest(d);
  } catch (e) {
    $('#digestOverview').innerHTML = `<span class="digest-error"><b>日报加载失败</b>（${esc(e.message)}）。<br/>若这是全新部署，日报会在首次 CI 运行后生成；也可本地运行 <code>python3 engine/run.py all</code>。</span>`;
    $('#digestSections').innerHTML = '';
    digestLoaded = true;
  }
  renderDigestHistory();
}

$('#digestToggle').addEventListener('click', () => setViewMode(document.body.dataset.view === 'digest' ? 'nav' : 'digest'));
$('#heroDigestBtn').addEventListener('click', () => setViewMode('digest'));
$('#digestHistory').addEventListener('click', e => {
  const btn = e.target.closest('.digest-date'); if (!btn) return;
  const date = btn.dataset.date;
  loadDigest(`data/digests/${date}.json`, true);
});
// 预取往期列表
fetch('data/digests/index.json', { cache: 'no-store' }).then(r => r.ok ? r.json() : null).then(idx => {
  if (idx && Array.isArray(idx.dates)) { digestState.history = idx.dates; renderDigestHistory(); }
}).catch(() => {});

/* ───────── 模型服务配置（本浏览器级覆盖 + 测试连接） ───────── */
const MODEL_CFG_KEY = 'aihn_model_cfg';
const modelModal = $('#modelModal');

function loadModelCfgOverride() {
  try { return JSON.parse(localStorage.getItem(MODEL_CFG_KEY) || 'null'); } catch { return null; }
}
function fillModelForm() {
  const o = loadModelCfgOverride() || {};
  $('#cfgEndpoint').value = o.endpoint || 'https://api.mosi.cn/v1/chat/completions';
  $('#cfgModel').value = o.model || 'nex-n2.6';
  $('#cfgTemperature').value = o.temperature != null ? o.temperature : '0.7';
  $('#cfgKey').value = ''; // 不回填模型密钥
  $('#cfgSearchKey').value = ''; // 搜索 Key 也不回填
  $('#cfgSearchEndpoint').value = o.searchEndpoint || 'https://api.tavily.com/search';
}
function openModelModal() { modelModal.hidden = false; document.body.style.overflow = 'hidden'; fillModelForm(); }
function closeModelModal() { modelModal.hidden = true; document.body.style.overflow = ''; }

$('#modelBtn').addEventListener('click', openModelModal);
$('#closeModelModal').addEventListener('click', closeModelModal);
modelModal.addEventListener('click', e => { if (e.target === modelModal) closeModelModal(); });

$('#cfgSaveBtn').addEventListener('click', () => {
  const endpoint = $('#cfgEndpoint').value.trim();
  const model = $('#cfgModel').value.trim();
  const temperature = parseFloat($('#cfgTemperature').value);
  const prior = loadModelCfgOverride() || {};
  const key = $('#cfgKey').value.trim() || prior.key || '';
  const searchKey = $('#cfgSearchKey').value.trim() || prior.searchKey || '';
  const searchEndpoint = $('#cfgSearchEndpoint').value.trim();
  if (endpoint && !/^https?:\/\/.+/.test(endpoint)) { showToast('接口地址需以 http(s):// 开头'); return; }
  const cfg = { endpoint: endpoint || 'https://api.mosi.cn/v1/chat/completions', model: model || 'nex-n2.6', temperature: isNaN(temperature) ? 0.7 : Math.min(2, Math.max(0, temperature)), searchEndpoint: searchEndpoint || 'https://api.tavily.com/search' };
  if (key) cfg.key = key; // 仅存浏览器
  if (searchKey) cfg.searchKey = searchKey; // 仅存浏览器
  localStorage.setItem(MODEL_CFG_KEY, JSON.stringify(cfg));
  showToast('自定义配置已保存到本浏览器 ✓');
});

$('#cfgResetBtn').addEventListener('click', () => {
  localStorage.removeItem(MODEL_CFG_KEY);
  fillModelForm();
  $('#cfgTestResult').textContent = '';
  $('#cfgTestResult').className = 'cfg-test-result';
  showToast('已恢复默认配置');
});

$('#cfgTestBtn').addEventListener('click', async () => {
  const saved = loadModelCfgOverride() || {};
  const endpoint = $('#cfgEndpoint').value.trim() || saved.endpoint || 'https://api.mosi.cn/v1/chat/completions';
  const model = $('#cfgModel').value.trim() || saved.model || 'nex-n2.6';
  const temperature = parseFloat($('#cfgTemperature').value);
  const key = $('#cfgKey').value.trim() || saved.key || '';
  const resultEl = $('#cfgTestResult');
  if (!key) {
    resultEl.textContent = '需要 API Key 才能直连测试。默认服务端密钥不会下发到浏览器，请在上方填入你自己的 Key（仅本地保存用于本次测试），或直接查看本页「默认服务端配置」。';
    resultEl.className = 'cfg-test-result err';
    return;
  }
  resultEl.textContent = `正在直连 ${endpoint} …`;
  resultEl.className = 'cfg-test-result pending';
  const t0 = performance.now();
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30000);
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${key}` },
      body: JSON.stringify({ model, temperature: isNaN(temperature) ? 0.3 : temperature, max_tokens: 32, messages: [{ role: 'user', content: 'Reply with exactly: OK' }] }),
      signal: controller.signal,
    });
    clearTimeout(timer);
    const dt = Math.round(performance.now() - t0);
    const raw = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status}：${raw.slice(0, 200)}`);
    const data = JSON.parse(raw);
    const reply = (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content || '').trim();
    resultEl.textContent = `✓ 连接成功 · ${dt} ms · 模型回复：${reply.slice(0, 120) || '(空内容，可能被推理链 token 占满，加大 max_tokens 即可)'}`;
    resultEl.className = 'cfg-test-result ok';
  } catch (e) {
    const dt = Math.round(performance.now() - t0);
    const msg = e.name === 'AbortError' ? '超时（>30s）' : (e.message || String(e));
    resultEl.textContent = `✗ 连接失败 · ${dt} ms · ${msg}\n提示：浏览器直连需目标端点允许 CORS；若端点不允许，请使用 engine/model_client.py 在服务端测试（python3 engine/run.py digest）。`;
    resultEl.className = 'cfg-test-result err';
  }
});

/* ───────── 站点研究智能体：本地目录检索 + 用户自备联网搜索/模型 ───────── */
const AGENT_HISTORY_KEY = 'aihn_agent_history';
let agentHistory = [];
try { agentHistory = JSON.parse(sessionStorage.getItem(AGENT_HISTORY_KEY) || '[]'); } catch { agentHistory = []; }
function persistAgentHistory() { try { sessionStorage.setItem(AGENT_HISTORY_KEY, JSON.stringify(agentHistory.slice(-12))); } catch {} }
function agentBubble(role, text, pending=false) {
  const el = document.createElement('div'); el.className = `agent-message ${role}` + (pending ? ' pending' : '');
  const who = document.createElement('b'); who.textContent = role === 'user' ? '你' : 'AI 助手';
  const body = document.createElement('div'); body.textContent = text;
  el.append(who, body); $('#agentMessages').append(el); $('#agentMessages').scrollTop = $('#agentMessages').scrollHeight; return el;
}
function renderAgentHistory() {
  const box = $('#agentMessages'); box.innerHTML = '';
  agentBubble('assistant', '你好！我可以从本站目录检索并推荐 AI 站点，也可以结合网络搜索制作指定主题日报。');
  for (const m of agentHistory.slice(-12)) agentBubble(m.role === 'user' ? 'user' : 'assistant', m.content);
}
function retrieveSites(query, limit=14) {
  const terms = (query.toLowerCase().match(/[\w+#.-]+|[\u3400-\u9fff]{1,}/g) || []).filter(t => t.length > 1);
  const stop = new Set(['推荐','搜索','制作','日报','主题','最近','生成','一下','哪些','网站','站点','信息','给我','请你','帮我','内容','联网','一周','最近','过去','today','last','days','week']);
  const qs = terms.filter(t => !stop.has(t));
  return SITES.map(site => {
    const fields = [site.name, site.desc, site.cat, site.subcat, (site.tags||[]).join(' '), domainOf(site.url)].map(x => String(x||'').toLowerCase());
    let match = 0;
    qs.forEach(q => { if (fields[0].includes(q)) match += 8; else if (fields.slice(2,5).some(f=>f.includes(q))) match += 5; else if (fields[1].includes(q) || fields[5].includes(q)) match += 2; });
    if (qs.length && qs.every(q => fields.some(f => f.includes(q)))) match += 5;
    const score = Number(site.score||0) * .02 + Number(site.heat||0)*.01 + Number(site.quality||0)*.01;
    return {site, rank: match + score};
  }).filter(x=>x.rank>0).sort((a,b)=>b.rank-a.rank).slice(0,limit).map(x=>x.site);
}
async function tavilySearch(query, cfg) {
  if (!cfg.searchKey) return {error:'尚未设置联网搜索 API Key；仅使用本地目录。'};
  const endpoint = cfg.searchEndpoint || 'https://api.tavily.com/search';
  const res = await fetch(endpoint, {method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({api_key:cfg.searchKey,query,search_depth:'advanced',max_results:6,include_answer:false,include_raw_content:false})});
  if (!res.ok) throw new Error(`搜索服务 HTTP ${res.status}：${(await res.text()).slice(0,180)}`);
  const data=await res.json();
  return {results:(data.results||[]).map(x=>({title:x.title,url:x.url,content:x.content,published_date:x.published_date,score:x.score}))};
}
function agentContext(query, sites, web) {
  const s=sites.map((x,i)=>`${i+1}. ${x.name} | ${x.cat}/${x.subcat||''} | ${x.desc} | URL ${x.url} | 热度${x.heat} 质量${x.quality} 综合${x.score}${x.stars?` Stars ${x.stars}`:''}`).join('\n');
  const latest=window.__LATEST_DIGEST ? JSON.stringify(window.__LATEST_DIGEST).slice(0,5000) : '';
  const w=web && web.results ? web.results.map((x,i)=>`[Web ${i+1}] ${x.title} | ${x.published_date||''} | ${x.content||''}\nURL: ${x.url}`).join('\n') : '';
  return `用户请求：${query}\n\n本站目录检索 Top ${sites.length}（仅代表目录匹配及热度质量，不代表网页已实时验证）：\n${s||'无匹配项'}\n\n联网搜索结果（只有本段非空时才可称已联网搜索；逐条保留URL）：\n${w||'本轮未获得联网搜索结果。'}\n\n最新站内日报（可选上下文）：\n${latest||'未加载'}`;
}
async function runAgent(query) {
  const cfg=loadModelCfgOverride()||{};
  if (!cfg.key) throw new Error('请先点击 ⚙ 模型配置，填入并保存你自己的模型 API Key。本站不会向浏览器提供服务端密钥。');
  const sites=retrieveSites(query,14);
  let web={};
  if ($('#agentWebSearch').checked && cfg.searchKey) {
    try { web=await tavilySearch(query,cfg); }
    catch(e) { web={error:e.message}; }
  }
  const sys=`你是 AI 热榜导航的研究助手。你可以使用提供的本站目录检索结果进行站点推荐，也可综合明确标注的联网搜索结果撰写报告。\n硬性规则：不得捏造目录内容、站点属性、新闻事实、日期或来源；站点目录是 discovery index，不是实时验证。未提供 web results 或搜索失败时，必须明确说明没有完成联网搜索，不可声称掌握最新动态。对于主题日报，要明确日期范围、主题、摘要、重要性、原文URL；引用只用上下文内的真实URL，区分搜索摘要与已核实事实。优先中文、结构清晰、简洁但有用。站点推荐说明匹配理由并给出原始URL。用户要求建议时，给出5-10项；日报用「日期/主题、要点、来源链接、观察与限制」结构。`;
  const messages=[{role:'system',content:sys},...agentHistory.slice(-8).map(m=>({role:m.role,content:m.content})),{role:'user',content:agentContext(query,sites,web)}];
  const response=await fetch(cfg.endpoint||'https://api.mosi.cn/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${cfg.key}`},body:JSON.stringify({model:cfg.model||'nex-n2.6',temperature:cfg.temperature??0.5,max_tokens:6000,messages})});
  if(!response.ok) throw new Error(`模型服务 HTTP ${response.status}：${(await response.text()).slice(0,220)}`);
  const data=await response.json();
  const answer=data.choices?.[0]?.message?.content || data.choices?.[0]?.message?.reasoning_content || '';
  if(!answer) throw new Error('模型没有返回正文。可检查模型 Key、额度或 max_tokens。');
  return answer.trim();
}
$('#agentToggle').addEventListener('click',()=>setViewMode(document.body.dataset.view==='agent'?'nav':'agent'));
$('#heroAgentBtn')?.addEventListener('click',()=>setViewMode('agent'));
$('#agentView').addEventListener('click',e=>{const b=e.target.closest('.agent-prompt'); if(b){$('#agentInput').value=b.dataset.prompt; $('#agentInput').focus();}});
$('#newChatBtn').addEventListener('click',()=>{agentHistory=[];persistAgentHistory();renderAgentHistory();});
$('#agentForm').addEventListener('submit',async e=>{
  e.preventDefault(); const input=$('#agentInput'); const query=input.value.trim(); if(!query)return;
  input.value=''; agentBubble('user',query); const pending=agentBubble('assistant','正在检索本站目录'+($('#agentWebSearch').checked?'并尝试联网搜索':'')+'，再请模型整理…',true);
  try { const answer=await runAgent(query); pending.remove(); agentBubble('assistant',answer); agentHistory.push({role:'user',content:query},{role:'assistant',content:answer}); agentHistory=agentHistory.slice(-12); persistAgentHistory(); }
  catch(err){pending.remove(); agentBubble('assistant',`处理失败：${err.message}\n\n提示：自定义模型端点须允许浏览器 CORS；联网搜索也可能因端点策略失败。若被浏览器拦截，请在可访问该 API 的 agent/server 环境调用，勿把密钥发给公共网页。`);}
});
renderAgentHistory();

/* ───────── TOP 榜弹窗 ───────── */
const topModal = $('#topModal');
const topList = $('#topList');
let topTab = 'stars';

function openTop() { topModal.hidden = false; document.body.style.overflow = 'hidden'; renderTop(); }
function closeTop() { topModal.hidden = true; document.body.style.overflow = ''; }
$('#topBtn').addEventListener('click', openTop);
$('#closeTopModal').addEventListener('click', closeTop);
topModal.addEventListener('click', e => { if (e.target === topModal) closeTop(); });
$('#topTabs').addEventListener('click', e => {
  const btn = e.target.closest('.modal-tab'); if (!btn) return;
  topTab = btn.dataset.tab;
  $$('.modal-tab', $('#topTabs')).forEach(t => t.classList.toggle('is-active', t === btn));
  renderTop();
});

function topFavicon(url) { return `<img class="top-favicon" src="${faviconOf(url)}" alt="" loading="lazy" width="28" height="28" onerror="this.style.visibility='hidden'" />`; }

function renderTop() {
  let items;
  if (topTab === 'stars') items = SITES.filter(s => s.stars > 0).slice().sort((a, b) => b.stars - a.stars).slice(0, 20);
  else if (topTab === 'curated') items = SITES.filter(s => s.source === '精选').slice().sort((a, b) => b.score - a.score).slice(0, 20);
  else items = SITES.slice().sort((a, b) => b.score - a.score).slice(0, 20);

  topList.innerHTML = items.map((s, i) => {
    const rank = i + 1;
    const rankCls = rank <= 3 ? ` rank r${rank}` : ' rank';
    const scoreTxt = topTab === 'stars' ? '★ ' + fmtStars(s.stars) : String(s.score);
    return `<li><a class="top-item" href="${escHtml(s.url)}" target="_blank" rel="noopener noreferrer">
      <span class="${rankCls.trim()}">${rank}</span>
      ${topFavicon(s.url)}
      <span style="min-width:0">
        <span class="top-name">${escHtml(s.name)}</span><br/>
        <span class="top-desc">${escHtml(s.desc)}</span>
      </span>
      <span class="top-score">${escHtml(scoreTxt)}</span>
    </a></li>`;
  }).join('');
}

/* ───────── 首次渲染 ───────── */
render();
