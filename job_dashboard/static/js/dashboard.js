/* ─────────────────────────────────────────────────────
   Job Hunt Dashboard – Main JS
   Single /api/bootstrap call on load; search results cached server-side.
   ───────────────────────────────────────────────────── */

const API = {
  bootstrap:  () => `/api/bootstrap`,
  search:     (q, loc, sources) => `/api/jobs/search?q=${enc(q)}&location=${enc(loc)}&sources=${enc(sources)}`,
  saveJob:    () => `/api/jobs/save`,
  savedJobs:  (status) => `/api/jobs/saved${status ? `?status=${status}` : ''}`,
  updateJob:  (id) => `/api/jobs/saved/${id}`,
  deleteJob:  (id) => `/api/jobs/saved/${id}`,
  resumes:    () => `/api/resumes`,
  upload:     () => `/api/resumes/upload`,
  activateR:  (id) => `/api/resumes/${id}/activate`,
  deleteR:    (id) => `/api/resumes/${id}`,
  downloadR:  (id) => `/api/resumes/${id}/download`,
  stats:      () => `/api/stats`,
};

const enc = encodeURIComponent;

/* ── CSRF token ── */
function getCsrf() {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : (document.querySelector('meta[name="csrf-token"]')?.content ?? '');
}

async function apiFetch(url, opts = {}) {
  const headers = { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf(), ...(opts.headers || {}) };
  const res = await fetch(url, { ...opts, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

/* ── Toast ── */
function toast(msg, type = 'info') {
  const c = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  t.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${msg}</span>`;
  c.appendChild(t);
  requestAnimationFrame(() => t.classList.add('show'));
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, 3500);
}

/* ── Navigation ── */
let currentSection = 'dashboard';
function navigate(section) {
  document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(`section-${section}`)?.classList.add('active');
  document.querySelector(`[data-nav="${section}"]`)?.classList.add('active');
  document.getElementById('topbar-title').textContent = {
    dashboard: 'Dashboard',
    search: 'Search Jobs',
    saved: 'Saved Jobs',
    resume: 'My Resumes',
  }[section] || section;
  currentSection = section;
  if (section === 'dashboard') loadDashboard();
  if (section === 'saved') loadSavedJobs();
  if (section === 'resume') loadResumes();
}

/* ── State ── */
const state = {
  jobs: [],
  sources: [],
  activeSources: new Set(),
  savedJobs: [],
  resumes: [],
  stats: null,
  searchQuery: '',
  searchLocation: '',
  currentJob: null,
};

/* ── Bootstrap – ONE request to seed entire UI ── */
async function bootstrap() {
  try {
    const data = await apiFetch(API.bootstrap());
    state.sources = data.sources || [];
    state.activeSources = new Set(state.sources.map(s => s.name));
    state.stats = data.stats || {};
    renderSourceChips();
    renderStats(state.stats);
    renderPipeline(state.stats);
    renderActiveResume(state.stats.active_resume);
    renderSearchHistory();
    // Update saved badge
    document.getElementById('saved-badge').textContent = state.stats.total_saved || 0;
  } catch (e) {
    toast('Could not load dashboard data: ' + e.message, 'error');
  }
}

/* ── Source Chips ── */
function renderSourceChips() {
  const c = document.getElementById('source-chips');
  c.innerHTML = state.sources.map(s => `
    <div class="source-chip active" data-source="${s.name}" style="background:${hexAlpha(s.logo_color, 0.15)};border-color:${hexAlpha(s.logo_color, 0.4)};color:${s.logo_color}">
      <span class="dot" style="background:${s.logo_color}"></span>${s.display_name}
    </div>
  `).join('');
  c.querySelectorAll('.source-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const src = chip.dataset.source;
      if (state.activeSources.has(src)) {
        state.activeSources.delete(src);
        chip.classList.remove('active');
        chip.style.background = '';
        chip.style.borderColor = '';
        chip.style.color = '';
      } else {
        state.activeSources.add(src);
        const s = state.sources.find(x => x.name === src);
        chip.classList.add('active');
        chip.style.background = hexAlpha(s.logo_color, 0.15);
        chip.style.borderColor = hexAlpha(s.logo_color, 0.4);
        chip.style.color = s.logo_color;
      }
    });
  });
}

/* ── Search ── */
async function searchJobs() {
  const q = document.getElementById('search-query').value.trim();
  const loc = document.getElementById('search-location').value.trim();
  if (!q) { toast('Enter a job title or role to search', 'error'); return; }
  state.searchQuery = q;
  state.searchLocation = loc;

  const sources = [...state.activeSources].join(',');
  const grid = document.getElementById('jobs-grid');
  const countEl = document.getElementById('result-count');
  grid.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><span>Searching across platforms…</span></div>';
  countEl.textContent = '';

  try {
    const data = await apiFetch(API.search(q, loc, sources));
    state.jobs = data.jobs || [];
    renderJobs();
    const cacheNote = data.cached ? ' (cached)' : '';
    countEl.textContent = `${state.jobs.length} results${cacheNote}`;
    if (state.jobs.length === 0) toast('No jobs found. Try different keywords.', 'info');
    else toast(`Found ${state.jobs.length} jobs across ${state.activeSources.size} sources${cacheNote}`, 'success');
    updateSearchHistory(q);
    renderSearchHistory();
  } catch (e) {
    grid.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠</div><h3>Search failed</h3><p>${e.message}</p></div>`;
    toast(e.message, 'error');
  }
}

function renderJobs() {
  const grid = document.getElementById('jobs-grid');
  if (!state.jobs.length) {
    grid.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><h3>No results found</h3><p>Try broader keywords or enable more sources.</p></div>';
    return;
  }
  grid.innerHTML = state.jobs.map((j, i) => jobCardHTML(j, i)).join('');
  grid.querySelectorAll('.job-card').forEach((card, i) => {
    card.style.animationDelay = `${i * 30}ms`;
    card.querySelector('.btn-save')?.addEventListener('click', (e) => {
      e.stopPropagation();
      saveJob(state.jobs[i]);
    });
    card.addEventListener('click', () => openJobModal(state.jobs[i]));
  });
}

function jobCardHTML(j, idx) {
  const initials = (j.company || '?').slice(0, 2).toUpperCase();
  const src = state.sources.find(s => s.name === j.source) || { logo_color: '#6366f1' };
  const salary = salaryText(j);
  const tags = (j.tags || []).slice(0, 4);
  return `
  <div class="job-card" data-idx="${idx}">
    <div class="job-card-header">
      <div class="company-logo" style="background:${src.logo_color}">${initials}</div>
      <div style="flex:1;min-width:0">
        <div class="job-title">${esc(j.title)}</div>
        <div class="job-company">${esc(j.company)}</div>
      </div>
      <span class="job-source-badge" style="background:${src.logo_color}">${esc(j.source_display || j.source)}</span>
    </div>
    <div class="job-meta">
      <span>📍 ${esc(j.location)}</span>
      ${salary ? `<span class="salary-badge">💰 ${salary}</span>` : ''}
    </div>
    ${j.description ? `<div class="job-description">${esc(j.description)}</div>` : ''}
    ${tags.length ? `<div class="job-tags">${tags.map(t => `<span class="job-tag">${esc(t)}</span>`).join('')}</div>` : ''}
    <div class="job-actions">
      <button class="btn btn-primary btn-sm btn-save">💾 Save</button>
      ${j.url ? `<a href="${encodeURI(j.url)}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" onclick="event.stopPropagation()">🔗 Apply</a>` : ''}
    </div>
  </div>`;
}

/* ── Save Job ── */
async function saveJob(job) {
  try {
    await apiFetch(API.saveJob(), { method: 'POST', body: JSON.stringify(job) });
    toast(`"${job.title}" saved!`, 'success');
    // Refresh badge without a full stats reload
    const badge = document.getElementById('saved-badge');
    badge.textContent = parseInt(badge.textContent || '0') + 1;
  } catch (e) {
    toast(e.message, e.message.includes('Already') ? 'info' : 'error');
  }
}

/* ── Job Modal ── */
function openJobModal(job) {
  state.currentJob = job;
  const src = state.sources.find(s => s.name === job.source) || { logo_color: '#6366f1' };
  document.getElementById('modal-title').textContent = job.title;
  document.getElementById('modal-body').innerHTML = `
    <div class="detail-row">
      <div class="detail-item"><div class="detail-label">Company</div><div class="detail-value">${esc(job.company)}</div></div>
      <div class="detail-item"><div class="detail-label">Location</div><div class="detail-value">${esc(job.location)}</div></div>
    </div>
    ${salaryText(job) ? `<div class="detail-row"><div class="detail-item"><div class="detail-label">Salary</div><div class="detail-value" style="color:var(--green)">${salaryText(job)}</div></div></div>` : ''}
    ${(job.tags || []).length ? `<div style="margin-bottom:12px"><div class="detail-label" style="margin-bottom:6px">Skills / Tags</div><div class="job-tags">${(job.tags || []).map(t => `<span class="job-tag tag-blue">${esc(t)}</span>`).join('')}</div></div>` : ''}
    <div style="margin-bottom:4px"><div class="detail-label">Description</div></div>
    <div style="font-size:13px;color:var(--text-secondary);line-height:1.7;max-height:200px;overflow-y:auto">${esc(job.description || 'No description available.')}</div>
    <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">
      <span style="font-size:11px;padding:3px 8px;border-radius:10px;background:${hexAlpha(src.logo_color,0.15)};color:${src.logo_color};border:1px solid ${hexAlpha(src.logo_color,0.3)}">${esc(job.source_display || job.source)}</span>
      ${job.posted_at ? `<span style="font-size:11px;color:var(--text-muted)">${formatDate(job.posted_at)}</span>` : ''}
    </div>
  `;
  document.getElementById('modal-apply-link').href = encodeURI(job.url || '#');
  document.getElementById('modal-apply-link').style.display = job.url ? 'inline-flex' : 'none';
  openModal('job-modal');
}

/* ── Saved Jobs ── */
async function loadSavedJobs() {
  const container = document.getElementById('kanban-board');
  container.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
  try {
    const data = await apiFetch(API.savedJobs());
    state.savedJobs = data.jobs || [];
    renderKanban();
  } catch (e) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠</div><h3>${e.message}</h3></div>`;
  }
}

const COLUMNS = [
  { key: 'saved',        label: 'Saved',        color: '#8b949e' },
  { key: 'applied',      label: 'Applied',       color: '#58a6ff' },
  { key: 'interviewing', label: 'Interviewing',  color: '#d29922' },
  { key: 'offer',        label: 'Offer',         color: '#3fb950' },
  { key: 'rejected',     label: 'Rejected',      color: '#f85149' },
];

function renderKanban() {
  const board = document.getElementById('kanban-board');
  const byStatus = {};
  COLUMNS.forEach(c => { byStatus[c.key] = []; });
  state.savedJobs.forEach(j => { if (byStatus[j.status]) byStatus[j.status].push(j); });

  board.innerHTML = COLUMNS.map(col => `
    <div class="kanban-column">
      <div class="kanban-header">
        <div class="col-dot" style="background:${col.color}"></div>
        <div class="col-title">${col.label}</div>
        <div class="col-count">${byStatus[col.key].length}</div>
      </div>
      <div class="kanban-cards" id="col-${col.key}">
        ${byStatus[col.key].length === 0
          ? '<div style="color:var(--text-muted);font-size:12px;padding:8px 4px">No jobs here yet</div>'
          : ''}
        ${byStatus[col.key].map(j => `
          <div class="kanban-card" data-id="${j.id}" onclick="openSavedJobModal(${j.id})">
            <div class="kc-title">${esc(j.title)}</div>
            <div class="kc-company">${esc(j.company)}</div>
            <div class="kc-date">${j.applied_at ? '✅ Applied ' + formatDate(j.applied_at) : formatDate(j.created_at)}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function openSavedJobModal(id) {
  const job = state.savedJobs.find(j => j.id === id);
  if (!job) return;
  state.currentJob = job;
  document.getElementById('saved-modal-title').textContent = job.title;
  document.getElementById('saved-modal-company').textContent = job.company;
  document.getElementById('saved-modal-location').textContent = job.location || '—';
  document.getElementById('saved-modal-source').textContent = job.source || '—';
  document.getElementById('saved-modal-status').value = job.status;
  document.getElementById('saved-modal-notes').value = job.notes || '';
  document.getElementById('saved-modal-apply-link').href = encodeURI(job.url || '#');
  document.getElementById('saved-modal-apply-link').style.display = job.url ? 'inline-flex' : 'none';
  openModal('saved-modal');
}

async function updateSavedJobStatus() {
  const job = state.currentJob;
  if (!job) return;
  const status = document.getElementById('saved-modal-status').value;
  const notes = document.getElementById('saved-modal-notes').value;
  try {
    await apiFetch(API.updateJob(job.id), { method: 'PATCH', body: JSON.stringify({ status, notes }) });
    toast('Job updated!', 'success');
    closeModal('saved-modal');
    loadSavedJobs();
    refreshStats();
  } catch (e) { toast(e.message, 'error'); }
}

async function deleteSavedJob() {
  const job = state.currentJob;
  if (!job) return;
  if (!confirm(`Remove "${job.title}" from saved jobs?`)) return;
  try {
    await apiFetch(API.deleteJob(job.id), { method: 'DELETE' });
    toast('Job removed', 'success');
    closeModal('saved-modal');
    loadSavedJobs();
    refreshStats();
  } catch (e) { toast(e.message, 'error'); }
}

/* ── Resumes ── */
async function loadResumes() {
  const list = document.getElementById('resume-list');
  list.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
  try {
    const data = await apiFetch(API.resumes());
    state.resumes = data.resumes || [];
    renderResumes();
  } catch (e) {
    list.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠</div><h3>${e.message}</h3></div>`;
  }
}

function renderResumes() {
  const list = document.getElementById('resume-list');
  if (!state.resumes.length) {
    list.innerHTML = '<div class="empty-state"><div class="empty-icon">📄</div><h3>No resumes uploaded yet</h3><p>Upload your resume to get started.</p></div>';
    return;
  }
  list.innerHTML = state.resumes.map(r => `
    <div class="resume-item ${r.is_active ? 'active-resume' : ''}" data-id="${r.id}">
      <div class="resume-file-icon">${r.file_type.toUpperCase()}</div>
      <div class="resume-info">
        <div class="resume-name">${esc(r.original_name)}</div>
        <div class="resume-meta">${formatBytes(r.file_size)} • Uploaded ${formatDate(r.created_at)}</div>
      </div>
      ${r.is_active
        ? '<span class="active-badge">Active</span>'
        : `<button class="btn btn-secondary btn-sm" onclick="activateResume(${r.id})">Set Active</button>`}
      <a href="${API.downloadR(r.id)}" class="btn btn-secondary btn-sm" download>⬇ Download</a>
      <button class="btn btn-danger btn-sm" onclick="deleteResume(${r.id})">🗑</button>
    </div>
  `).join('');
}

async function uploadResume(file) {
  if (!file) return;
  const allowed = ['pdf', 'docx', 'doc', 'txt'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) { toast('Only PDF, DOCX, DOC, TXT allowed', 'error'); return; }
  if (file.size > 5 * 1024 * 1024) { toast('File too large (max 5 MB)', 'error'); return; }

  const form = new FormData();
  form.append('resume', file);
  try {
    const res = await fetch(API.upload(), {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf() },
      body: form,
    });
    if (!res.ok) { const e = await res.json(); throw new Error(e.error || 'Upload failed'); }
    const data = await res.json();
    toast('Resume uploaded!', 'success');
    loadResumes();
    renderActiveResume(data.resume);
  } catch (e) { toast(e.message, 'error'); }
}

async function activateResume(id) {
  try {
    const data = await apiFetch(API.activateR(id), { method: 'PATCH' });
    toast('Resume set as active', 'success');
    loadResumes();
    renderActiveResume(data.resume);
  } catch (e) { toast(e.message, 'error'); }
}

async function deleteResume(id) {
  if (!confirm('Delete this resume?')) return;
  try {
    await apiFetch(API.deleteR(id), { method: 'DELETE' });
    toast('Resume deleted', 'success');
    loadResumes();
  } catch (e) { toast(e.message, 'error'); }
}

/* ── Dashboard ── */
async function loadDashboard() {
  // Stats already loaded by bootstrap; just re-render from state
  if (state.stats) {
    renderStats(state.stats);
    renderPipeline(state.stats);
    renderActiveResume(state.stats.active_resume);
  }
  renderSearchHistory();
}

async function refreshStats() {
  try {
    const data = await apiFetch(API.stats());
    state.stats = data;
    renderStats(data);
    renderPipeline(data);
    renderActiveResume(data.active_resume);
    document.getElementById('saved-badge').textContent = data.total_saved || 0;
  } catch (_) {}
}

function renderStats(data) {
  const status = data.by_status || {};
  document.getElementById('stat-total').textContent = data.total_saved || 0;
  document.getElementById('stat-applied').textContent = status.applied || 0;
  document.getElementById('stat-interviewing').textContent = status.interviewing || 0;
  document.getElementById('stat-offers').textContent = status.offer || 0;
}

function renderPipeline(data) {
  const status = data.by_status || {};
  const bars = document.getElementById('pipeline-bars');
  const labels = document.getElementById('pipeline-labels');
  const cols = COLUMNS.slice(0, 4);
  const vals = cols.map(c => status[c.key] || 0);
  const max = Math.max(...vals, 1);
  bars.innerHTML = cols.map((c, i) => `
    <div class="pipeline-bar" style="height:${Math.max(8, (vals[i]/max)*100)}%;background:${c.color}" title="${c.label}: ${vals[i]}"></div>
  `).join('');
  labels.innerHTML = cols.map(c => `<span style="flex:1;text-align:center;font-size:10px;color:var(--text-muted)">${c.label}</span>`).join('');
}

function renderActiveResume(resume) {
  const el = document.getElementById('active-resume-info');
  if (!resume) {
    el.innerHTML = '<span style="color:var(--text-muted);font-size:13px">No resume uploaded yet. <a href="#" onclick="navigate(\'resume\');return false" style="color:var(--accent)">Upload one →</a></span>';
  } else {
    el.innerHTML = `
      <div style="display:flex;align-items:center;gap:12px">
        <div class="resume-file-icon" style="width:36px;height:44px;font-size:10px">${resume.file_type.toUpperCase()}</div>
        <div>
          <div style="font-size:13px;font-weight:600">${esc(resume.original_name)}</div>
          <div style="font-size:11px;color:var(--text-secondary)">${formatBytes(resume.file_size)} • Active</div>
        </div>
        <span class="active-badge" style="margin-left:auto">Active</span>
      </div>
    `;
  }
}

function renderSearchHistory() {
  const el = document.getElementById('recent-searches');
  const saved = JSON.parse(localStorage.getItem('searchHistory') || '[]');
  if (!saved.length) { el.innerHTML = '<span style="color:var(--text-muted);font-size:12px">No searches yet</span>'; return; }
  el.innerHTML = saved.slice(0, 8).map(q => `<span class="history-chip" onclick="quickSearch('${esc(q)}')">${esc(q)}</span>`).join('');
}

function updateSearchHistory(q) {
  let hist = JSON.parse(localStorage.getItem('searchHistory') || '[]');
  hist = [q, ...hist.filter(h => h !== q)].slice(0, 20);
  localStorage.setItem('searchHistory', JSON.stringify(hist));
}

function quickSearch(q) {
  navigate('search');
  document.getElementById('search-query').value = q;
  searchJobs();
}

/* ── Modal helpers ── */
function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

/* ── Utility ── */
function esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function hexAlpha(hex, a) {
  const r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16), b = parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${a})`;
}
function salaryText(j) {
  if (j.salary_min && j.salary_max) return `$${fmtNum(j.salary_min)}–$${fmtNum(j.salary_max)}`;
  if (j.salary_min) return `$${fmtNum(j.salary_min)}+`;
  if (j.salary_max) return `Up to $${fmtNum(j.salary_max)}`;
  return '';
}
function fmtNum(n) {
  if (n >= 1000) return `${(n/1000).toFixed(0)}k`;
  return String(Math.round(n));
}
function formatDate(d) {
  if (!d) return '';
  try { return new Date(d).toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' }); }
  catch { return d; }
}
function formatBytes(b) {
  if (b < 1024) return `${b} B`;
  if (b < 1024*1024) return `${(b/1024).toFixed(1)} KB`;
  return `${(b/(1024*1024)).toFixed(1)} MB`;
}

/* ── Init ── */
document.addEventListener('DOMContentLoaded', async () => {
  // Sidebar nav
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => navigate(item.dataset.nav));
  });

  // Hamburger
  document.getElementById('hamburger')?.addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
  });

  // Search
  document.getElementById('search-btn').addEventListener('click', searchJobs);
  document.getElementById('search-query').addEventListener('keydown', e => { if (e.key === 'Enter') searchJobs(); });

  // Modal close
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => { if (e.target === overlay) overlay.classList.remove('open'); });
  });
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => btn.closest('.modal-overlay').classList.remove('open'));
  });

  // Saved job modal actions
  document.getElementById('update-job-btn').addEventListener('click', updateSavedJobStatus);
  document.getElementById('delete-job-btn').addEventListener('click', deleteSavedJob);

  // Save job from detail modal
  document.getElementById('modal-save-btn').addEventListener('click', () => {
    if (state.currentJob) saveJob(state.currentJob);
    closeModal('job-modal');
  });

  // Resume drag-and-drop upload
  const zone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('resume-file-input');
  zone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', e => { if (e.target.files[0]) uploadResume(e.target.files[0]); });
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) uploadResume(e.dataTransfer.files[0]);
  });

  // Quick-search dashboard buttons
  document.querySelectorAll('.quick-search-btn').forEach(btn => {
    btn.addEventListener('click', () => quickSearch(btn.dataset.q));
  });

  // ── Single bootstrap call – seeds sources, stats, resume in one hit ──
  await bootstrap();
  navigate('dashboard');
});
