/* ═══════════════════════════════════════════════════════════════════
   Cithara — Client-side Application Logic
   ═══════════════════════════════════════════════════════════════════ */

// ─── CSRF Helper ─────────────────────────────────────────────────
function getCookie(name) {
  let v = null;
  if (document.cookie) {
    document.cookie.split(';').forEach(c => {
      c = c.trim();
      if (c.startsWith(name + '='))
        v = decodeURIComponent(c.substring(name.length + 1));
    });
  }
  return v;
}
const CSRF = () => getCookie('csrftoken');

// ─── API Helpers ─────────────────────────────────────────────────
async function api(url, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(opts.method))
    headers['X-CSRFToken'] = CSRF();
  const res = await fetch(url, { ...opts, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || err.error || JSON.stringify(err));
  }
  return res.json();
}

const apiGet    = (url)       => api(url);
const apiPost   = (url, body) => api(url, { method: 'POST',   body: JSON.stringify(body) });
const apiPatch  = (url, body) => api(url, { method: 'PATCH',  body: JSON.stringify(body) });
const apiDelete = (url)       => api(url, { method: 'DELETE' }).catch(() => ({}));

// ─── Toast Notifications (FR — graceful error display) ───────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `
    <span class="toast__icon">${icons[type] || icons.info}</span>
    <span class="toast__message">${message}</span>
    <button class="toast__close" onclick="this.parentElement.remove()">×</button>`;
  container.appendChild(toast);
  setTimeout(() => { toast.classList.add('toast--leaving'); setTimeout(() => toast.remove(), 300); }, 4000);
}

// ═══════════════════════════════════════════════════════════════════
//  LIBRARY PAGE
// ═══════════════════════════════════════════════════════════════════
const SONGS_PER_PAGE = 9;
let libState = { songs: [], filtered: [], page: 1, sort: '-date_generated', search: '' };

async function initLibrary() {
  const grid = document.getElementById('song-grid');
  if (!grid) return;

  const libraryId = grid.dataset.libraryId;
  try {
    const songs = await apiGet('/api/songs/');
    libState.songs = songs.filter(s => String(s.library) === String(libraryId) && !s.is_deleted);
    applyFilters();
  } catch (e) {
    showToast('Failed to load songs: ' + e.message, 'error');
  }

  // Search
  const searchInput = document.getElementById('library-search');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      libState.search = searchInput.value.toLowerCase();
      libState.page = 1;
      applyFilters();
    });
  }

  // Sort
  const sortSelect = document.getElementById('library-sort');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      libState.sort = sortSelect.value;
      libState.page = 1;
      applyFilters();
    });
  }
}

function applyFilters() {
  let songs = [...libState.songs];

  // Search filter
  if (libState.search) {
    songs = songs.filter(s =>
      s.title.toLowerCase().includes(libState.search) ||
      s.genre.toLowerCase().includes(libState.search) ||
      s.mood.toLowerCase().includes(libState.search)
    );
  }

  // Sort
  if (libState.sort === '-date_generated')
    songs.sort((a, b) => new Date(b.date_generated) - new Date(a.date_generated));
  else if (libState.sort === 'date_generated')
    songs.sort((a, b) => new Date(a.date_generated) - new Date(b.date_generated));
  else if (libState.sort === 'title')
    songs.sort((a, b) => a.title.localeCompare(b.title));

  libState.filtered = songs;
  renderSongGrid();
  renderPagination();
}

function renderSongGrid() {
  const grid = document.getElementById('song-grid');
  const empty = document.getElementById('empty-state');
  if (!grid) return;

  if (libState.filtered.length === 0) {
    grid.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }
  if (empty) empty.style.display = 'none';

  const start = (libState.page - 1) * SONGS_PER_PAGE;
  const page = libState.filtered.slice(start, start + SONGS_PER_PAGE);

  grid.innerHTML = page.map(song => `
    <div class="card song-card" id="song-${song.id}">
      <a href="/song/${song.id}/" class="song-card__link">
        <div class="song-card__header">
          <span class="song-card__title">${esc(song.title)}</span>
          <span class="song-card__date">${fmtDate(song.date_generated)}</span>
        </div>
        <div class="song-card__badges">
          <span class="badge badge--genre">${esc(song.genre)}</span>
          <span class="badge badge--mood">${esc(song.mood)}</span>
          <span class="badge badge--occasion">${esc(song.occasion)}</span>
        </div>
        <div class="song-card__meta">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
          </svg>
          ${fmtDuration(song.duration)}
        </div>
      </a>
      <div class="song-card__actions">
        <button class="song-card__play-btn" title="Play" onclick="playSong(${song.id}, '${esc(song.audio_url || '')}', '${esc(song.title)}')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        </button>
        <button class="btn btn--icon btn--ghost" title="Download" onclick="downloadSong(${song.id}, '${esc(song.title)}')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4m4-5l5 5 5-5m-5 5V3"/></svg>
        </button>
        <button class="btn btn--icon btn--ghost" title="Share" onclick="shareSong(${song.id})">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        </button>
        <button class="btn btn--icon btn--danger" title="Delete" onclick="deleteSong(${song.id})">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18m-2 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
        </button>
      </div>
    </div>
  `).join('');
}

function renderPagination() {
  const container = document.getElementById('pagination');
  if (!container) return;
  const totalPages = Math.ceil(libState.filtered.length / SONGS_PER_PAGE);
  if (totalPages <= 1) { container.innerHTML = ''; return; }
  let html = '';
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="pagination__btn ${i === libState.page ? 'pagination__btn--active' : ''}"
              onclick="goToPage(${i})">${i}</button>`;
  }
  container.innerHTML = html;
}

function goToPage(p) {
  libState.page = p;
  renderSongGrid();
  renderPagination();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ─── Song Actions ────────────────────────────────────────────────
async function deleteSong(id) {
  if (!confirm('Delete this song? It will be hidden from your library.')) return;
  try {
    await apiPatch(`/api/songs/${id}/`, { is_deleted: true });
    libState.songs = libState.songs.filter(s => s.id !== id);
    applyFilters();
    showToast('Song deleted', 'success');
  } catch (e) {
    showToast('Delete failed: ' + e.message, 'error');
  }
}

function shareSong(id) {
  const url = `${window.location.origin}/song/${id}/`;
  navigator.clipboard.writeText(url).then(
    () => showToast('Link copied to clipboard!', 'success'),
    () => showToast('Could not copy link', 'error')
  );
}

function downloadSong(songIdOrUrl, title) {
  // If a numeric song ID is passed, use the server-side download endpoint
  if (typeof songIdOrUrl === 'number' || /^\d+$/.test(songIdOrUrl)) {
    window.location.href = `/song/${songIdOrUrl}/download/`;
    return;
  }
  // Fallback: direct URL download (for sticky player)
  const url = songIdOrUrl;
  if (!url || url.includes('example.com')) {
    showToast('No audio file available (mock mode)', 'info');
    return;
  }
  const a = document.createElement('a');
  a.href = url;
  a.download = (title || 'song') + '.mp3';
  a.click();
}

// ═══════════════════════════════════════════════════════════════════
//  STICKY AUDIO PLAYER  (FR-12)
// ═══════════════════════════════════════════════════════════════════
let audio = null;
let currentSongId = null;

function initPlayer() {
  audio = new Audio();
  audio.addEventListener('timeupdate', updatePlayerProgress);
  audio.addEventListener('loadedmetadata', () => {
    const dur = document.getElementById('player-duration');
    if (dur) dur.textContent = fmtDuration(Math.floor(audio.duration));
  });
  audio.addEventListener('ended', () => {
    setPlayerIcon(false);
  });
  audio.addEventListener('error', () => {
    if (currentSongId) showToast('Cannot play this audio (mock URL or unavailable)', 'info');
  });

  const seek = document.getElementById('player-seek');
  if (seek) seek.addEventListener('input', () => {
    if (audio.duration) audio.currentTime = (seek.value / 100) * audio.duration;
  });

  const vol = document.getElementById('player-volume');
  if (vol) {
    vol.value = 80;
    audio.volume = 0.8;
    vol.addEventListener('input', () => { audio.volume = vol.value / 100; });
  }
}

function playSong(id, url, title) {
  const player = document.getElementById('sticky-player');
  if (!player) return;

  if (currentSongId === id && !audio.paused) {
    audio.pause();
    setPlayerIcon(false);
    return;
  }

  if (currentSongId !== id) {
    audio.src = url || '';
    currentSongId = id;
    document.getElementById('player-title').textContent = title || 'Unknown';
  }

  if (!url || url.includes('example.com')) {
    showToast('Mock mode — no real audio to play', 'info');
  }

  audio.play().catch(() => {});
  setPlayerIcon(true);
  player.classList.add('player--visible');
  document.body.classList.add('player-active');
}

function togglePlayer() {
  if (!audio) return;
  if (audio.paused) { audio.play().catch(() => {}); setPlayerIcon(true); }
  else              { audio.pause();                 setPlayerIcon(false); }
}

function setPlayerIcon(playing) {
  const btn = document.getElementById('player-play-btn');
  if (!btn) return;
  btn.innerHTML = playing
    ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>'
    : '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
}

function updatePlayerProgress() {
  if (!audio.duration) return;
  const pct = (audio.currentTime / audio.duration) * 100;
  const seek = document.getElementById('player-seek');
  const cur  = document.getElementById('player-current');
  if (seek) seek.value = pct;
  if (cur)  cur.textContent = fmtDuration(Math.floor(audio.currentTime));
}

// ═══════════════════════════════════════════════════════════════════
//  SONG DETAIL PAGE PLAYER  +  WAVEFORM VISUALIZATION
// ═══════════════════════════════════════════════════════════════════
let waveformCtx = null;   // AudioContext for Web Audio API
let waveformAnim = null;  // requestAnimationFrame handle

function initDetailPlayer() {
  const container = document.getElementById('detail-player');
  if (!container) return;

  const url   = container.dataset.audioUrl || '';
  const title = container.dataset.title || '';
  const songId = container.dataset.songId || '';
  const detailAudio = new Audio();
  detailAudio.src = url;

  const playBtn = document.getElementById('detail-play-btn');
  const seekBar = document.getElementById('detail-seek');
  const curTime = document.getElementById('detail-current');
  const durTime = document.getElementById('detail-duration');
  const canvas  = document.getElementById('waveform-canvas');

  // ── Waveform Animation Setup ──
  function drawWaveform() {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;

    function render() {
      waveformAnim = requestAnimationFrame(render);
      ctx.clearRect(0, 0, W, H);

      const barCount = 64;
      const barWidth = W / barCount;
      const time = Date.now() / 150; // Speed of the animation

      for (let i = 0; i < barCount; i++) {
        // Procedural dancing effect using sine waves and time
        const noise1 = Math.sin(i * 0.5 + time) * 0.5 + 0.5;
        const noise2 = Math.cos(i * 0.3 - time * 0.8) * 0.5 + 0.5;
        
        // Shape it so the middle tends to be higher, edges lower
        const distFromCenter = Math.abs((barCount / 2) - i) / (barCount / 2);
        const envelope = 1 - Math.pow(distFromCenter, 2);
        
        const value = ((noise1 + noise2) / 2) * envelope;
        const barHeight = Math.max(4, value * H * 0.85);

        // Gradient from accent to accent-light
        const pct = i / barCount;
        const r = Math.round(124 + pct * 44);
        const g = Math.round(58  + pct * 27);
        const b = Math.round(237 + pct * 10);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.85)`;

        const x = i * barWidth;
        const radius = barWidth * 0.3;
        ctx.beginPath();
        ctx.roundRect(x + 1, H - barHeight, barWidth - 2, barHeight, [radius, radius, 0, 0]);
        ctx.fill();
      }
    }
    render();
  }

  function drawIdleWaveform() {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    const barCount = 64;
    const barWidth = W / barCount;

    for (let i = 0; i < barCount; i++) {
      // Gentle sine-wave idle pattern
      const barHeight = 4 + Math.sin(i * 0.3) * 3 + Math.random() * 2;
      const pct = i / barCount;
      ctx.fillStyle = `rgba(${124 + pct * 44}, ${58 + pct * 27}, 237, 0.3)`;
      ctx.beginPath();
      ctx.roundRect(i * barWidth + 1, H - barHeight, barWidth - 2, barHeight, [2, 2, 0, 0]);
      ctx.fill();
    }
  }

  function stopWaveform() {
    if (waveformAnim) {
      cancelAnimationFrame(waveformAnim);
      waveformAnim = null;
    }
    drawIdleWaveform();
  }

  // Set canvas dimensions
  if (canvas) {
    const resizeCanvas = () => {
      canvas.width  = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      const ctx = canvas.getContext('2d');
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      canvas.width  = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    drawIdleWaveform();
  }

  const PLAY_ICON  = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
  const PAUSE_ICON = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>';

  // ── Standard player events ──
  detailAudio.addEventListener('loadedmetadata', () => {
    if (durTime) durTime.textContent = fmtDuration(Math.floor(detailAudio.duration));
  });

  detailAudio.addEventListener('timeupdate', () => {
    if (!detailAudio.duration) return;
    const pct = (detailAudio.currentTime / detailAudio.duration) * 100;
    if (seekBar) seekBar.value = pct;
    if (curTime) curTime.textContent = fmtDuration(Math.floor(detailAudio.currentTime));
  });

  detailAudio.addEventListener('ended', () => {
    if (playBtn) playBtn.innerHTML = PLAY_ICON;
    stopWaveform();
  });

  detailAudio.addEventListener('error', () => {
    if (playBtn) playBtn.innerHTML = PLAY_ICON;
    stopWaveform();
  });

  if (playBtn) {
    playBtn.addEventListener('click', () => {
      if (detailAudio.paused) {
        const isMockUrl = !url || url.includes('example.com');
        if (isMockUrl) {
          showToast('Mock mode — no real audio available for playback', 'info');
          return;
        }
        detailAudio.play().then(() => {
          playBtn.innerHTML = PAUSE_ICON;
          drawWaveform();
        }).catch(() => {
          showToast('Audio failed to load', 'error');
          playBtn.innerHTML = PLAY_ICON;
        });
      } else {
        detailAudio.pause();
        playBtn.innerHTML = PLAY_ICON;
        stopWaveform();
      }
    });
  }

  if (seekBar) {
    seekBar.addEventListener('input', () => {
      if (detailAudio.duration) detailAudio.currentTime = (seekBar.value / 100) * detailAudio.duration;
    });
  }
}

// ═══════════════════════════════════════════════════════════════════
//  CREATION STUDIO  (FR-03 / FR-04 / FR-05 / FR-06)
// ═══════════════════════════════════════════════════════════════════
const TIMEOUT_MS = 15 * 60 * 1000;  // 15 minutes
let studioPollTimer = null;
let studioTimeoutTimer = null;
let studioStartTime = null;

function initStudio() {
  const form = document.getElementById('studio-form');
  if (!form) return;

  // Character counter for prompt (FR-03: max 1000 chars)
  const prompt = document.getElementById('studio-prompt');
  const counter = document.getElementById('char-counter');
  if (prompt && counter) {
    prompt.addEventListener('input', () => {
      const len = prompt.value.length;
      counter.textContent = `${len} / 1000`;
      counter.className = 'char-counter' + (len > 900 ? (len >= 1000 ? ' char-counter--max' : ' char-counter--warn') : '');
    });
  }

  // UC-08: Prefill form from query params (Regenerate flow)
  const params = new URLSearchParams(window.location.search);
  const fieldMap = {
    prompt:   'studio-prompt',
    title:    'studio-title',
    genre:    'studio-genre',
    mood:     'studio-mood',
    occasion: 'studio-occasion',
    style:    'studio-style',
  };
  for (const [param, elId] of Object.entries(fieldMap)) {
    const val = params.get(param);
    if (val) {
      const el = document.getElementById(elId);
      if (el) el.value = val;
    }
  }
  // Update char counter if prompt was prefilled
  if (params.get('prompt') && prompt && counter) {
    const len = prompt.value.length;
    counter.textContent = `${len} / 1000`;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await submitGeneration(form);
  });
}

async function submitGeneration(form) {
  const data = Object.fromEntries(new FormData(form));
  data.library = parseInt(data.library, 10);

  const btn = form.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Generating…';

  showProgress('PENDING');
  studioStartTime = Date.now();
  updateTimer();

  try {
    const result = await apiPost('/api/generate/', data);

    if (result.status === 'SUCCESS') {
      showProgress('SUCCESS');
      showPreview(result);
      showToast('Song generated successfully!', 'success');
    } else {
      // Poll for status (FR-05)
      pollStatus(result.task_id);
    }
  } catch (e) {
    showProgress('FAILED');
    showToast('Generation failed: ' + e.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '✦ Generate Song';
  }
}

function pollStatus(taskId) {
  // FR-06: 15-minute timeout
  studioTimeoutTimer = setTimeout(() => {
    clearInterval(studioPollTimer);
    showProgress('FAILED');
    showToast('Generation timed out (15 minutes)', 'error');
  }, TIMEOUT_MS);

  studioPollTimer = setInterval(async () => {
    try {
      const result = await apiGet(`/api/generate/${taskId}/status/`);
      showProgress(result.status);

      if (result.status === 'SUCCESS') {
        clearInterval(studioPollTimer);
        clearTimeout(studioTimeoutTimer);
        showPreview(result);
        showToast('Song generated successfully!', 'success');
      } else if (result.status === 'FAILED') {
        clearInterval(studioPollTimer);
        clearTimeout(studioTimeoutTimer);
        showToast('Generation failed: ' + (result.error_message || 'Unknown error'), 'error');
      }
    } catch (e) {
      clearInterval(studioPollTimer);
      clearTimeout(studioTimeoutTimer);
      showProgress('FAILED');
      showToast('Polling error: ' + e.message, 'error');
    }
  }, 3000);
}

function showProgress(status) {
  const container = document.getElementById('progress-area');
  const idle = document.getElementById('studio-idle');
  if (!container) return;
  if (idle) idle.style.display = 'none';
  container.style.display = 'block';

  const statusMap = {
    'PENDING': 10,
    'TEXT_SUCCESS': 40,
    'FIRST_SUCCESS': 70,
    'SUCCESS': 100,
    'FAILED': 0
  };

  const pct = statusMap[status] ?? 0;
  const fill = document.getElementById('progress-fill');
  const statusLabel = document.getElementById('progress-status');
  if (fill) fill.style.width = pct + '%';
  if (statusLabel) statusLabel.textContent = status;

  // Update step indicators
  const steps = ['PENDING', 'TEXT_SUCCESS', 'FIRST_SUCCESS', 'SUCCESS'];
  steps.forEach((step, i) => {
    const el = document.getElementById('step-' + step);
    if (!el) return;
    const idx = steps.indexOf(status);
    if (i < idx)       el.className = 'progress-steps__step progress-steps__step--done';
    else if (i === idx) el.className = 'progress-steps__step progress-steps__step--active';
    else                el.className = 'progress-steps__step';
  });
}

function updateTimer() {
  const timerEl = document.getElementById('progress-timer');
  if (!timerEl || !studioStartTime) return;
  const elapsed = Date.now() - studioStartTime;
  timerEl.textContent = fmtDuration(Math.floor(elapsed / 1000));
  if (elapsed < TIMEOUT_MS) requestAnimationFrame(updateTimer);
}

function showPreview(result) {
  const preview = document.getElementById('preview-area');
  if (!preview) return;
  preview.style.display = 'block';
  preview.innerHTML = `
    <div class="card" style="margin-top: 1.5rem; text-align: center;">
      <h3 style="margin-bottom: 0.5rem; color: var(--success);">✓ Generation Complete</h3>
      <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.9rem;">
        Song has been saved to your library.
      </p>
      <div style="display: flex; gap: 0.75rem; justify-content: center;">
        <a href="/library/" class="btn btn--primary">View Library</a>
        <a href="/song/${result.song}/" class="btn btn--ghost">Song Details</a>
      </div>
    </div>`;
}

// ═══════════════════════════════════════════════════════════════════
//  STAR RATING WIDGET  (FR-16)
// ═══════════════════════════════════════════════════════════════════
function initRatingWidget() {
  const widget = document.getElementById('rating-widget');
  if (!widget) return;

  const songId = widget.dataset.songId;
  let currentRating = parseInt(widget.dataset.currentRating) || 0;
  const stars = widget.querySelectorAll('.star-rating__star');

  function renderStars(rating) {
    stars.forEach(star => {
      const val = parseInt(star.dataset.value);
      const svg = star.querySelector('svg');
      if (val <= rating) {
        svg.setAttribute('fill', '#fbbf24');
        svg.setAttribute('stroke', '#fbbf24');
      } else {
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
      }
    });
  }

  // Initial render
  renderStars(currentRating);

  // Hover preview
  stars.forEach(star => {
    star.addEventListener('mouseenter', () => {
      renderStars(parseInt(star.dataset.value));
    });
  });

  widget.querySelector('.star-rating').addEventListener('mouseleave', () => {
    renderStars(currentRating);
  });

  // Click to rate
  stars.forEach(star => {
    star.addEventListener('click', async () => {
      const val = parseInt(star.dataset.value);
      try {
        await apiPatch(`/api/songs/${songId}/`, { rating: val });
        currentRating = val;
        renderStars(val);
        showToast(`Rated ${val} star${val > 1 ? 's' : ''}!`, 'success');
      } catch (e) {
        showToast('Could not save rating: ' + e.message, 'error');
      }
    });
  });
}

// ═══════════════════════════════════════════════════════════════════
//  REGENERATE SONG  (UC-08)
// ═══════════════════════════════════════════════════════════════════
async function regenerateSong(songId) {
  try {
    const song = await apiGet(`/api/songs/${songId}/`);
    // Build query params to prefill the studio form
    const params = new URLSearchParams({
      prompt:   song.prompt   || '',
      title:    song.title    || '',
      genre:    song.genre    || '',
      mood:     song.mood     || '',
      occasion: song.occasion || '',
      style:    song.style    || '',
    });
    window.location.href = `/studio/?${params.toString()}`;
  } catch (e) {
    showToast('Could not load song data: ' + e.message, 'error');
  }
}

// ═══════════════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════════════
function esc(str) {
  const d = document.createElement('div');
  d.textContent = str || '';
  return d.innerHTML;
}

function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

function fmtDuration(secs) {
  if (!secs || secs <= 0) return '0:00';
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

// ═══════════════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initPlayer();
  initLibrary();
  initStudio();
  initDetailPlayer();
  initRatingWidget();
});
