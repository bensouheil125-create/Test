// ==================== PS MULTI TIMER APP ====================
// Pricing: 50 DA per 15 minutes = 0.05556 DA/second

const PRICE_PER_SECOND = 50 / (15 * 60); // ~0.05556 DA/s
const LS_STATE_KEY = 'multi-timer-app-state';
const LS_SETTINGS_KEY = 'multi-timer-settings-v1';
const LS_REVENUE_KEY = 'multi-timer-revenue-v1';

// ==================== STATE ====================
let timers = [];
let nextId = 1;
let settings = {
  gridCols: 'auto',
  cardSize: 'medium',
  clockFont: 'Share Tech Mono',
  accentColor: '#00d4ff',
  bgImage: '',
  bgOpacity: 0.9,
  fontSize: 1,
  psFontSize: 1.1,
  ringtone: 'classic'
};
let revenue = {}; // { "2026-05-21": 150, ... }
let currentTab = 'timers'; // 'timers' | 'calendar'
let calendarMonth = new Date().getMonth();
let calendarYear = new Date().getFullYear();
let selectedDay = null;
let intervalId = null;
let dragSrcIndex = null;

// ==================== PERSISTENCE ====================
function saveState() {
  const state = timers.map(t => ({
    ...t,
    // Don't save DOM references
  }));
  localStorage.setItem(LS_STATE_KEY, JSON.stringify({ timers: state, nextId }));
}

function loadState() {
  try {
    const raw = localStorage.getItem(LS_STATE_KEY);
    if (raw) {
      const data = JSON.parse(raw);
      timers = data.timers || [];
      nextId = data.nextId || 1;
      // Restore running timers - calculate elapsed during absence
      timers.forEach(t => {
        if (t.status === 'running' && t.lastStartedAt) {
          const elapsed = (Date.now() - t.lastStartedAt) / 1000;
          t.accumulatedElapsed += elapsed;
          if (t.type === 'countdown') {
            const totalElapsed = t.accumulatedElapsed;
            if (totalElapsed >= t.initialDuration) {
              t.accumulatedElapsed = t.initialDuration;
              t.status = 'stopped';
              t.lastStartedAt = null;
            } else {
              t.lastStartedAt = Date.now();
            }
          } else {
            t.lastStartedAt = Date.now();
          }
        }
      });
    }
  } catch(e) { console.error('Load state error:', e); }
}

function saveSettings() {
  localStorage.setItem(LS_SETTINGS_KEY, JSON.stringify(settings));
}

function loadSettings() {
  try {
    const raw = localStorage.getItem(LS_SETTINGS_KEY);
    if (raw) settings = { ...settings, ...JSON.parse(raw) };
  } catch(e) {}
}

function saveRevenue() {
  localStorage.setItem(LS_REVENUE_KEY, JSON.stringify(revenue));
}

function loadRevenue() {
  try {
    const raw = localStorage.getItem(LS_REVENUE_KEY);
    if (raw) revenue = JSON.parse(raw);
  } catch(e) {}
}

// ==================== TIMER LOGIC ====================
function createTimer(type, duration) {
  const timer = {
    id: 'timer_' + Date.now() + '_' + Math.random().toString(36).substr(2,5),
    name: 'PS ' + nextId,
    type: type, // 'stopwatch' | 'countdown'
    status: 'stopped',
    initialDuration: duration || 900, // default 15min for countdown
    accumulatedElapsed: 0,
    lastStartedAt: null,
    priceOffset: 0 // for price continuity on extend
  };
  nextId++;
  timers.push(timer);
  saveState();
  render();
}

function getElapsed(timer) {
  let elapsed = timer.accumulatedElapsed;
  if (timer.status === 'running' && timer.lastStartedAt) {
    elapsed += (Date.now() - timer.lastStartedAt) / 1000;
  }
  return elapsed;
}

function getDisplayTime(timer) {
  const elapsed = getElapsed(timer);
  if (timer.type === 'countdown') {
    const remaining = Math.max(0, timer.initialDuration - elapsed);
    return remaining;
  }
  return elapsed;
}

function getPrice(timer) {
  const elapsed = getElapsed(timer);
  return (elapsed * PRICE_PER_SECOND) + timer.priceOffset;
}

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
}

function formatPrice(price) {
  return price.toFixed(2) + ' دج';
}

function startTimer(timer, skipRender) {
  if (timer.status === 'running') return;
  timer.finished = false; // clear finished state
  timer.status = 'running';
  timer.lastStartedAt = Date.now();
  saveState();
  if (!skipRender) render();
}

function pauseTimer(timer, skipRender) {
  if (timer.status !== 'running') return;
  const elapsed = (Date.now() - timer.lastStartedAt) / 1000;
  timer.accumulatedElapsed += elapsed;
  timer.lastStartedAt = null;
  timer.status = 'paused';
  saveState();
  if (!skipRender) render();
}

function resetTimer(timer) {
  // Save revenue before reset
  const price = getPrice(timer);
  if (price > 0) {
    addRevenue(price);
  }
  timer.status = 'stopped';
  timer.lastStartedAt = null;
  timer.accumulatedElapsed = 0;
  timer.priceOffset = 0;
  if (timer.type === 'countdown') {
    timer.initialDuration = 900; // Reset to 15 min
  }
  saveState();
  render();
}

function deleteTimer(timerId) {
  const idx = timers.findIndex(t => t.id === timerId);
  if (idx >= 0) {
    const timer = timers[idx];
    const price = getPrice(timer);
    if (price > 0 && timer.status !== 'stopped') {
      addRevenue(price);
    }
    timers.splice(idx, 1);
    saveState();
    render();
  }
}

function startAll() { timers.forEach(t => startTimer(t, true)); render(); }
function pauseAll() { timers.forEach(t => pauseTimer(t, true)); render(); }
function resetAll() { timers.forEach(t => resetTimer(t)); }
function deleteAll() {
  timers.forEach(t => {
    const price = getPrice(t);
    if (price > 0) addRevenue(price);
  });
  timers = [];
  saveState();
  render();
}

// Extend countdown time (price continues from where it was)
function extendTime(timer, minutes) {
  timer.initialDuration += minutes * 60;
  // If finished, restart from where price left off
  if (timer.status === 'stopped' && getElapsed(timer) >= timer.initialDuration - (minutes * 60)) {
    // Already finished - don't auto start
  }
  saveState();
  render();
}

// Adjust elapsed time (+ or -) with price adjustment
function adjustTime(timer, minutes) {
  const seconds = minutes * 60;
  const wasRunning = timer.status === 'running';
  
  // If running, snapshot elapsed so we can adjust it
  if (wasRunning && timer.lastStartedAt) {
    const elapsed = (Date.now() - timer.lastStartedAt) / 1000;
    timer.accumulatedElapsed += elapsed;
    timer.lastStartedAt = Date.now(); // Reset reference point, keep running
  }
  
  const newElapsed = Math.max(0, timer.accumulatedElapsed + seconds);
  const diff = newElapsed - timer.accumulatedElapsed;
  timer.accumulatedElapsed = newElapsed;
  
  // Adjust price offset for reductions
  if (diff < 0) {
    timer.priceOffset += diff * PRICE_PER_SECOND;
    if (getPrice(timer) < 0) timer.priceOffset = -(timer.accumulatedElapsed * PRICE_PER_SECOND);
  }
  
  // Timer stays running - no pause!
  saveState();
  render();
}

// ==================== REVENUE ====================
function addRevenue(amount) {
  const today = new Date().toISOString().split('T')[0];
  revenue[today] = (revenue[today] || 0) + amount;
  saveRevenue();
}

function getTodayRevenue() {
  const today = new Date().toISOString().split('T')[0];
  return revenue[today] || 0;
}

function getWeekRevenue() {
  const now = new Date();
  const dayOfWeek = now.getDay();
  let total = 0;
  for (let i = 0; i < 7; i++) {
    const d = new Date(now);
    d.setDate(d.getDate() - dayOfWeek + i);
    const key = d.toISOString().split('T')[0];
    total += revenue[key] || 0;
  }
  return total;
}

function getMonthRevenue(year, month) {
  let total = 0;
  const days = new Date(year, month + 1, 0).getDate();
  for (let d = 1; d <= days; d++) {
    const key = `${year}-${(month+1).toString().padStart(2,'0')}-${d.toString().padStart(2,'0')}`;
    total += revenue[key] || 0;
  }
  return total;
}

// ==================== AUDIO ====================
function playAlarm(timerName, ringtone) {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const type = ringtone || settings.ringtone;
  
  function beep(freq, start, duration, vol) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    osc.frequency.value = freq;
    osc.type = 'square';
    gain.gain.value = vol || 0.3;
    osc.start(ctx.currentTime + start);
    osc.stop(ctx.currentTime + start + duration);
  }
  
  if (type === 'classic') {
    // 3 sharp + 4 medium + 2 long
    for (let i = 0; i < 3; i++) beep(1200, i * 0.2, 0.1, 0.4);
    for (let i = 0; i < 4; i++) beep(800, 0.7 + i * 0.3, 0.2, 0.3);
    for (let i = 0; i < 2; i++) beep(600, 2.0 + i * 0.6, 0.5, 0.25);
  } else if (type === 'bell') {
    for (let i = 0; i < 5; i++) beep(1000, i * 0.4, 0.3, 0.3);
  } else if (type === 'siren') {
    for (let i = 0; i < 8; i++) beep(600 + (i % 2) * 400, i * 0.25, 0.2, 0.3);
  } else if (type === 'gentle') {
    for (let i = 0; i < 3; i++) beep(500, i * 0.5, 0.4, 0.2);
  }
  
  // Speech
  setTimeout(() => {
    if ('speechSynthesis' in window) {
      for (let i = 0; i < 2; i++) {
        setTimeout(() => {
          const u = new SpeechSynthesisUtterance(timerName + ' انتهى وقته');
          u.lang = 'ar-SA';
          u.rate = 1;
          speechSynthesis.speak(u);
        }, i * 2500);
      }
    }
  }, 3000);
}

// ==================== CHECK COUNTDOWN FINISH ====================
function checkCountdowns() {
  let needsRender = false;
  timers.forEach(timer => {
    if (timer.type === 'countdown' && timer.status === 'running') {
      const elapsed = getElapsed(timer);
      if (elapsed >= timer.initialDuration) {
        timer.accumulatedElapsed = timer.initialDuration;
        timer.lastStartedAt = null;
        timer.status = 'stopped';
        timer.finished = true;
        playAlarm(timer.name, settings.ringtone);
        needsRender = true;
      }
    }
  });
  if (needsRender) {
    saveState();
    render();
  }
}

// ==================== DRAG & DROP ====================
function handleDragStart(e, index) {
  dragSrcIndex = index;
  e.target.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e, index) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  document.querySelectorAll('.timer-card').forEach(c => c.classList.remove('drag-over'));
  e.currentTarget.classList.add('drag-over');
}

function handleDrop(e, index) {
  e.preventDefault();
  document.querySelectorAll('.timer-card').forEach(c => c.classList.remove('drag-over'));
  if (dragSrcIndex !== null && dragSrcIndex !== index) {
    const item = timers.splice(dragSrcIndex, 1)[0];
    timers.splice(index, 0, item);
    saveState();
    render();
  }
  dragSrcIndex = null;
}

function handleDragEnd(e) {
  e.target.classList.remove('dragging');
  document.querySelectorAll('.timer-card').forEach(c => c.classList.remove('drag-over'));
  dragSrcIndex = null;
}


// ==================== RENDER ====================
function render() {
  isRendering = true;
  applySettings();
  const app = document.getElementById('app');
  
  const totalPrice = timers.reduce((sum, t) => sum + Math.max(0, getPrice(t)), 0);
  
  app.innerHTML = `
    <div id="bg-overlay"></div>
    <div class="header">
      <div class="header-top">
        <div class="header-title">🎮 PS Multi Timer</div>
        <div class="header-total">الإجمالي: ${formatPrice(totalPrice)}</div>
        <button class="btn btn-ghost btn-icon" onclick="toggleSettings()" title="إعدادات">⚙️</button>
      </div>
      <div class="price-bar">
        <span>💰 ${PRICE_PER_SECOND.toFixed(4)} دج/ثانية</span>
        <span>| ${(PRICE_PER_SECOND*60).toFixed(2)} دج/دقيقة</span>
        <span>| 50 دج/15د</span>
        <span>| ${(PRICE_PER_SECOND*3600).toFixed(0)} دج/ساعة</span>
      </div>
      <div class="nav-tabs">
        <button class="nav-tab ${currentTab==='timers'?'active':''}" onclick="switchTab('timers')">⏱️ العدّادات</button>
        <button class="nav-tab ${currentTab==='calendar'?'active':''}" onclick="switchTab('calendar')">📅 التقويم</button>
      </div>
      ${currentTab === 'timers' ? `
      <div class="header-actions">
        <button class="btn btn-accent" onclick="createTimer('stopwatch')">+ Stopwatch</button>
        <button class="btn btn-accent" onclick="showCountdownModal()">+ Countdown</button>
        <button class="btn btn-success" onclick="startAll()">▶ تشغيل الكل</button>
        <button class="btn btn-warning" onclick="pauseAll()">⏸ إيقاف الكل</button>
        <button class="btn btn-ghost" onclick="resetAll()">🔄 إعادة الكل</button>
        <button class="btn btn-danger" onclick="if(confirm('حذف كل العدّادات؟'))deleteAll()">🗑 حذف الكل</button>
      </div>` : ''}
    </div>
    ${currentTab === 'timers' ? renderTimers() : renderCalendar()}
    ${renderSettingsPanel()}
    ${renderCountdownModal()}
  `;
  
  if (settings.bgImage) {
    const overlay = document.getElementById('bg-overlay');
    if (overlay) overlay.style.backgroundImage = `url(${settings.bgImage})`;
  }
  
  // Allow tick to run again after DOM is stable
  setTimeout(() => { isRendering = false; }, 50);
}

function renderTimers() {
  if (timers.length === 0) {
    return `<div style="text-align:center;padding:60px 20px;color:var(--text-dim);">
      <div style="font-size:3em;margin-bottom:16px;">🎮</div>
      <div style="font-size:1.2em;">أضف عدّاداً لتبدأ</div>
      <div style="margin-top:8px;">اضغط + Stopwatch أو + Countdown</div>
    </div>`;
  }
  
  let html = '<div class="timers-grid">';
  timers.forEach((timer, index) => {
    const elapsed = getElapsed(timer);
    const displayTime = timer.type === 'countdown' 
      ? formatTime(Math.max(0, timer.initialDuration - elapsed))
      : formatTime(elapsed);
    const price = Math.max(0, getPrice(timer));
    const isRunning = timer.status === 'running';
    const isFinished = timer.type === 'countdown' && timer.finished && timer.status === 'stopped';
    
    html += `
    <div class="timer-card ${isRunning ? 'running' : ''} ${isFinished ? 'finished' : ''}"
         draggable="true"
         ondragstart="handleDragStart(event, ${index})"
         ondragover="handleDragOver(event, ${index})"
         ondrop="handleDrop(event, ${index})"
         ondragend="handleDragEnd(event)">
      <button class="delete-single" onclick="if(confirm('حذف ${timer.name}؟'))deleteTimer('${timer.id}')" title="حذف">✕</button>
      <div class="card-header">
        <input class="timer-name" value="${timer.name}" 
               onchange="renameTimer('${timer.id}', this.value)"
               oninput="renameTimer('${timer.id}', this.value)"
               onclick="this.select()"
               placeholder="اسم العداد">
        <span class="timer-type-badge">${timer.type === 'countdown' ? '⏳' : '⏱️'} ${timer.type}</span>
      </div>
      <div class="timer-display">${displayTime}</div>
      <div class="timer-price">${formatPrice(price)}</div>
      <div class="timer-finished-text">⚠️ انتهى الوقت!</div>
      <div class="timer-controls">
        ${isRunning 
          ? `<button class="btn btn-warning btn-sm" onclick="pauseTimer(timers.find(t=>t.id==='${timer.id}'));render()">⏸ إيقاف</button>`
          : `<button class="btn btn-success btn-sm" onclick="startTimer(timers.find(t=>t.id==='${timer.id}'));render()">▶ تشغيل</button>`
        }
        <button class="btn btn-ghost btn-sm" onclick="resetTimer(timers.find(t=>t.id==='${timer.id}'));render()">🔄 إعادة</button>
      </div>
      <div class="time-adjust">
        <button class="btn btn-ghost btn-sm" onclick="adjustTime(timers.find(t=>t.id==='${timer.id}'), -5)">-5د</button>
        <button class="btn btn-ghost btn-sm" onclick="adjustTime(timers.find(t=>t.id==='${timer.id}'), -1)">-1د</button>
        <button class="btn btn-ghost btn-sm" onclick="adjustTime(timers.find(t=>t.id==='${timer.id}'), 1)">+1د</button>
        <button class="btn btn-ghost btn-sm" onclick="adjustTime(timers.find(t=>t.id==='${timer.id}'), 5)">+5د</button>
      </div>
      ${timer.type === 'countdown' ? `
      <div class="extend-buttons">
        <button class="btn btn-accent btn-sm" onclick="extendTime(timers.find(t=>t.id==='${timer.id}'), 5)">+5د</button>
        <button class="btn btn-accent btn-sm" onclick="extendTime(timers.find(t=>t.id==='${timer.id}'), 15)">+15د</button>
        <button class="btn btn-accent btn-sm" onclick="extendTime(timers.find(t=>t.id==='${timer.id}'), 30)">+30د</button>
        <button class="btn btn-accent btn-sm" onclick="extendTime(timers.find(t=>t.id==='${timer.id}'), 60)">+1س</button>
      </div>` : ''}
    </div>`;
  });
  html += '</div>';
  return html;
}

function renameTimer(id, newName) {
  const timer = timers.find(t => t.id === id);
  if (timer) { timer.name = newName; saveState(); }
}


// ==================== CALENDAR RENDER ====================
function renderCalendar() {
  const year = calendarYear;
  const month = calendarMonth;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDay = new Date(year, month, 1).getDay();
  const monthNames = ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];
  const dayNames = ['أحد','إثنين','ثلاثاء','أربعاء','خميس','جمعة','سبت'];
  const today = new Date();
  const monthTotal = getMonthRevenue(year, month);
  
  let html = `<div class="revenue-panel active">`;
  
  // Navigation
  html += `<div class="cal-nav">
    <button class="btn btn-ghost btn-sm" onclick="calendarMonth--;if(calendarMonth<0){calendarMonth=11;calendarYear--;}render()">→</button>
    <span class="cal-month-name">${monthNames[month]} ${year}</span>
    <button class="btn btn-ghost btn-sm" onclick="calendarMonth++;if(calendarMonth>11){calendarMonth=0;calendarYear++;}render()">←</button>
    <button class="btn btn-accent btn-sm" onclick="calendarMonth=${today.getMonth()};calendarYear=${today.getFullYear()};render()">اليوم</button>
  </div>`;
  
  // Summary
  html += `<div class="summary-section">
    <div class="summary-row"><span class="summary-label">إيراد اليوم</span><span class="summary-value">${formatPrice(getTodayRevenue())}</span></div>
    <div class="summary-row"><span class="summary-label">إيراد الأسبوع</span><span class="summary-value">${formatPrice(getWeekRevenue())}</span></div>
    <div class="summary-row"><span class="summary-label">إيراد الشهر</span><span class="summary-value">${formatPrice(monthTotal)}</span></div>
  </div>`;
  
  // Calendar grid
  html += `<div class="calendar-grid">`;
  dayNames.forEach(d => { html += `<div class="cal-header">${d}</div>`; });
  
  // Empty cells before first day
  for (let i = 0; i < firstDay; i++) {
    html += `<div class="cal-day" style="visibility:hidden;"></div>`;
  }
  
  for (let d = 1; d <= daysInMonth; d++) {
    const dateKey = `${year}-${(month+1).toString().padStart(2,'0')}-${d.toString().padStart(2,'0')}`;
    const dayRevenue = revenue[dateKey] || 0;
    const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
    const hasRev = dayRevenue > 0;
    
    html += `<div class="cal-day ${isToday?'today':''} ${hasRev?'has-revenue':''}" onclick="selectDay(${d})">
      <span>${d}</span>
      ${hasRev ? `<span class="day-amount">${dayRevenue.toFixed(0)}</span>` : ''}
    </div>`;
  }
  html += `</div>`;
  
  // Selected day detail
  if (selectedDay) {
    const dateKey = `${year}-${(month+1).toString().padStart(2,'0')}-${selectedDay.toString().padStart(2,'0')}`;
    const dayRev = revenue[dateKey] || 0;
    html += `<div class="day-detail">
      <div class="day-detail-nav">
        <button class="btn btn-ghost btn-sm" onclick="navigateDay(-1)">→</button>
        <strong>${selectedDay} ${monthNames[month]} ${year}</strong>
        <button class="btn btn-ghost btn-sm" onclick="navigateDay(1)">←</button>
      </div>
      <div class="summary-row">
        <span class="summary-label">إيراد هذا اليوم</span>
        <span class="summary-value">${formatPrice(dayRev)}</span>
      </div>
    </div>`;
  }
  
  // Weekly breakdown
  html += `<div class="summary-section" style="margin-top:16px;">
    <h4 style="margin-bottom:10px;color:var(--accent);">ملخص أسبوعي</h4>`;
  
  let weekNum = 1;
  let weekTotal = 0;
  for (let d = 1; d <= daysInMonth; d++) {
    const dateKey = `${year}-${(month+1).toString().padStart(2,'0')}-${d.toString().padStart(2,'0')}`;
    weekTotal += revenue[dateKey] || 0;
    const dow = new Date(year, month, d).getDay();
    if (dow === 6 || d === daysInMonth) {
      html += `<div class="summary-row">
        <span class="summary-label">الأسبوع ${weekNum}</span>
        <span class="summary-value">${formatPrice(weekTotal)}</span>
      </div>`;
      weekNum++;
      weekTotal = 0;
    }
  }
  html += `</div>`;
  
  html += `</div>`;
  return html;
}

function selectDay(day) {
  selectedDay = day;
  render();
}

function navigateDay(dir) {
  if (!selectedDay) selectedDay = new Date().getDate();
  const daysInMonth = new Date(calendarYear, calendarMonth + 1, 0).getDate();
  selectedDay += dir;
  if (selectedDay > daysInMonth) {
    selectedDay = 1;
    calendarMonth++;
    if (calendarMonth > 11) { calendarMonth = 0; calendarYear++; }
  } else if (selectedDay < 1) {
    calendarMonth--;
    if (calendarMonth < 0) { calendarMonth = 11; calendarYear--; }
    selectedDay = new Date(calendarYear, calendarMonth + 1, 0).getDate();
  }
  render();
}

function switchTab(tab) {
  currentTab = tab;
  if (tab === 'calendar') {
    calendarMonth = new Date().getMonth();
    calendarYear = new Date().getFullYear();
  }
  render();
}


// ==================== SETTINGS PANEL ====================
function renderSettingsPanel() {
  const fonts = ['Share Tech Mono', 'Orbitron', 'monospace', 'Inter'];
  const fontLabels = ['Share Tech Mono', 'Orbitron', 'LCD', 'Classic'];
  const colors = ['#00d4ff', '#ff4757', '#2ed573', '#ffa502', '#a855f7', '#ec4899'];
  const ringtones = [
    { id: 'classic', name: 'كلاسيكي' },
    { id: 'bell', name: 'جرس' },
    { id: 'siren', name: 'صافرة' },
    { id: 'gentle', name: 'هادئ' }
  ];
  
  return `
  <div class="settings-overlay" id="settingsPanel">
    <div class="settings-panel">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
        <span class="settings-title">⚙️ الإعدادات</span>
        <button class="btn btn-ghost btn-sm" onclick="toggleSettings()">✕</button>
      </div>
      
      <div class="setting-group">
        <div class="setting-label">تخطيط الشبكة</div>
        <div class="setting-options">
          ${['auto','2','3','4','5'].map(v => 
            `<button class="setting-opt ${settings.gridCols===v?'active':''}" onclick="updateSetting('gridCols','${v}')">${v === 'auto' ? 'تلقائي' : v + ' أعمدة'}</button>`
          ).join('')}
        </div>
      </div>
      
      <div class="setting-group">
        <div class="setting-label">حجم البطاقة</div>
        <div class="setting-options">
          ${[['small','صغير'],['medium','متوسط'],['large','كبير']].map(([v,l]) => 
            `<button class="setting-opt ${settings.cardSize===v?'active':''}" onclick="updateSetting('cardSize','${v}')">${l}</button>`
          ).join('')}
        </div>
      </div>
      
      <div class="setting-group">
        <div class="setting-label">خط الساعة</div>
        <div class="setting-options">
          ${fonts.map((f,i) => 
            `<button class="setting-opt ${settings.clockFont===f?'active':''}" onclick="updateSetting('clockFont','${f}')">${fontLabels[i]}</button>`
          ).join('')}
        </div>
      </div>
      
      <div class="setting-group">
        <div class="setting-label">لون التمييز</div>
        <div class="setting-options">
          ${colors.map(c => 
            `<button class="color-opt ${settings.accentColor===c?'active':''}" style="background:${c}" onclick="updateSetting('accentColor','${c}')"></button>`
          ).join('')}
        </div>
      </div>

      <div class="setting-group">
        <div class="setting-label">رنة التنبيه</div>
        <div class="setting-options">
          ${ringtones.map(r => 
            `<button class="setting-opt ${settings.ringtone===r.id?'active':''}" onclick="updateSetting('ringtone','${r.id}')">${r.name}</button>`
          ).join('')}
        </div>
      </div>
      
      <div class="setting-group">
        <div class="setting-label">حجم الكتابة: ${settings.fontSize.toFixed(1)}</div>
        <div class="slider-group">
          <input type="range" min="0.7" max="2" step="0.1" value="${settings.fontSize}" 
                 onchange="updateSetting('fontSize', parseFloat(this.value))">
        </div>
      </div>

      <div class="setting-group">
        <div class="setting-label">حجم كتابة PS: ${settings.psFontSize.toFixed(1)}</div>
        <div class="slider-group">
          <input type="range" min="0.8" max="3" step="0.1" value="${settings.psFontSize}" 
                 onchange="updateSetting('psFontSize', parseFloat(this.value))">
        </div>
      </div>
      
      <div class="setting-group">
        <div class="setting-label">شفافية الخلفية: ${(settings.bgOpacity * 100).toFixed(0)}%</div>
        <div class="slider-group">
          <input type="range" min="0" max="1" step="0.05" value="${settings.bgOpacity}" 
                 onchange="updateSetting('bgOpacity', parseFloat(this.value))">
        </div>
      </div>
      
      <div class="setting-group">
        <div class="setting-label">صورة خلفية</div>
        <input type="file" accept="image/*" onchange="handleBgImage(event)" style="color:var(--text);font-size:0.85em;">
        ${settings.bgImage ? `<button class="btn btn-danger btn-sm" style="margin-top:6px;" onclick="updateSetting('bgImage','')">إزالة الخلفية</button>` : ''}
      </div>
    </div>
  </div>`;
}

function toggleSettings() {
  const panel = document.getElementById('settingsPanel');
  if (panel) panel.classList.toggle('open');
}

function updateSetting(key, value) {
  settings[key] = value;
  saveSettings();
  render();
  // Re-open settings
  setTimeout(() => {
    const panel = document.getElementById('settingsPanel');
    if (panel) panel.classList.add('open');
  }, 10);
}

function handleBgImage(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      settings.bgImage = e.target.result;
      saveSettings();
      render();
      setTimeout(() => {
        const panel = document.getElementById('settingsPanel');
        if (panel) panel.classList.add('open');
      }, 10);
    };
    reader.readAsDataURL(file);
  }
}

function applySettings() {
  const root = document.documentElement;
  root.style.setProperty('--accent', settings.accentColor);
  root.style.setProperty('--font-clock', `'${settings.clockFont}', monospace`);
  root.style.setProperty('--font-size-multiplier', settings.fontSize);
  root.style.setProperty('--ps-font-size', settings.psFontSize + 'em');
  root.style.setProperty('--bg-opacity', settings.bgOpacity);
  
  const sizes = { small: '240px', medium: '300px', large: '380px' };
  root.style.setProperty('--card-size', sizes[settings.cardSize] || '300px');
  
  if (settings.gridCols === 'auto') {
    root.style.setProperty('--grid-cols', 'auto-fill');
  } else {
    root.style.setProperty('--grid-cols', settings.gridCols);
  }
}

// ==================== COUNTDOWN MODAL ====================
function renderCountdownModal() {
  return `
  <div class="modal-overlay" id="countdownModal">
    <div class="modal-box">
      <h3>⏳ عدّاد تنازلي جديد</h3>
      <label style="font-size:0.85em;color:var(--text-dim);">المدة (بالدقائق):</label>
      <input class="modal-input" type="number" id="countdownMinutes" value="15" min="1" max="600">
      <div style="display:flex;gap:8px;justify-content:center;margin-top:12px;">
        <button class="btn btn-accent" onclick="confirmCountdown()">إنشاء</button>
        <button class="btn btn-ghost" onclick="closeCountdownModal()">إلغاء</button>
      </div>
    </div>
  </div>`;
}

function showCountdownModal() {
  setTimeout(() => {
    const modal = document.getElementById('countdownModal');
    if (modal) modal.classList.add('open');
  }, 10);
}

function closeCountdownModal() {
  const modal = document.getElementById('countdownModal');
  if (modal) modal.classList.remove('open');
}

function confirmCountdown() {
  const input = document.getElementById('countdownMinutes');
  const minutes = parseInt(input.value) || 15;
  createTimer('countdown', minutes * 60);
  closeCountdownModal();
}

// ==================== MAIN LOOP ====================
let isRendering = false;

function tick() {
  if (isRendering) return;
  if (currentTab !== 'timers') return;
  
  // Check if any countdown finished
  let countdownFinished = false;
  timers.forEach(timer => {
    if (timer.type === 'countdown' && timer.status === 'running') {
      const elapsed = getElapsed(timer);
      if (elapsed >= timer.initialDuration) {
        timer.accumulatedElapsed = timer.initialDuration;
        timer.lastStartedAt = null;
        timer.status = 'stopped';
        timer.finished = true;
        playAlarm(timer.name, settings.ringtone);
        countdownFinished = true;
      }
    }
  });
  
  if (countdownFinished) {
    saveState();
    render();
    return;
  }
  
  // Update ONLY text content - no DOM structure or class changes
  const displays = document.querySelectorAll('.timer-card');
  timers.forEach((timer, i) => {
    if (displays[i]) {
      const elapsed = getElapsed(timer);
      const displayTime = timer.type === 'countdown'
        ? formatTime(Math.max(0, timer.initialDuration - elapsed))
        : formatTime(elapsed);
      const price = Math.max(0, getPrice(timer));
      
      const timeEl = displays[i].querySelector('.timer-display');
      const priceEl = displays[i].querySelector('.timer-price');
      if (timeEl) timeEl.textContent = displayTime;
      if (priceEl) priceEl.textContent = formatPrice(price);
    }
  });
  
  // Update total
  const totalEl = document.querySelector('.header-total');
  if (totalEl) {
    const totalPrice = timers.reduce((sum, t) => sum + Math.max(0, getPrice(t)), 0);
    totalEl.textContent = 'الإجمالي: ' + formatPrice(totalPrice);
  }
}

// ==================== SERVICE WORKER ====================
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(err => {
    console.log('SW registration failed (normal for file:// protocol):', err);
  });
}

// ==================== INIT ====================
function init() {
  loadSettings();
  loadState();
  loadRevenue();
  render();
  
  // Start update loop - once per second (display shows seconds)
  intervalId = setInterval(tick, 1000);
  
  // Save state every 2 seconds for power loss protection
  setInterval(saveState, 2000);
  
  // Save immediately when page is closing (power off, tab close, etc.)
  window.addEventListener('beforeunload', () => {
    saveState();
    saveRevenue();
  });
  
  // Handle visibility change - recalculate on return
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      // Recalculate elapsed times when user returns
      loadState();
      render();
    } else {
      // Save when user switches away
      saveState();
    }
  });
}

// Start app
document.addEventListener('DOMContentLoaded', init);
