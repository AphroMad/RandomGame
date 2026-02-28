// ===== GAME.JS =====
// Handles all in-game logic

import { getFrName, frCache, allPokemon, loadPokemon } from './data.js';

// ===== CONFIG =====
const MAX_TIME = 10;

// ===== STATE =====
let players = [];
let decks = [];
let pokemonPerPlayer = 10;
let gameMode = 'qcm';
let imageMode = 'real';
let globalTurn = 0;
let totalTurns = 0;
let currentPlayerIdx = 0;
let currentRound = 0;
let currentPokemon = null;
let currentOptions = [];
let answered = false;
let timerInterval = null;
let questionStartTime = 0;
let timeLeft = MAX_TIME;
let correctAnswers = []; // tracks correct count per player

// ===== INIT FROM SESSION =====
async function init() {
  const raw = sessionStorage.getItem('gameConfig');
  if (!raw) {
    window.location.href = 'index.html';
    return;
  }

  // MUST populate allPokemon before renderQCM can pick random wrong answers
  await loadPokemon();

  const config = JSON.parse(raw);
  players = config.players;
  decks = config.decks;
  pokemonPerPlayer = config.pokemonPerPlayer;
  gameMode = config.gameMode;
  imageMode = config.imageMode;
  totalTurns = players.length * pokemonPerPlayer;
  correctAnswers = players.map(() => 0);

  renderScoreboard();
  loadQuestion();
}

// ===== SCOREBOARD =====
function renderScoreboard() {
  document.getElementById('scoreboard').innerHTML = players.map((p, i) => `
    <div class="score-chip ${i === currentPlayerIdx ? 'active-player' : ''}">
      <div class="chip-dot" style="background:${p.color}"></div>
      <div class="chip-name">${p.name}</div>
      <div class="chip-score">${Number.isInteger(p.score) ? p.score : p.score.toFixed(1)}</div>
    </div>
  `).join('');
}

// ===== QUESTION =====
async function loadQuestion() {
  answered = false;
  clearInterval(timerInterval);
  document.getElementById('result-msg').textContent = '';
  document.getElementById('next-btn').style.display = 'none';

  currentPlayerIdx = globalTurn % players.length;
  currentRound = Math.floor(globalTurn / players.length);

  const player = players[currentPlayerIdx];
  const pokemon = decks[currentPlayerIdx][currentRound];
  const nameFr = await getFrName(pokemon.id);
  currentPokemon = { ...pokemon, nameFr };

  // Turn banner
  document.getElementById('turn-dot').style.background = player.color;
  document.getElementById('turn-name').textContent = player.name;
  document.getElementById('turn-round').textContent =
    `Pokémon ${currentRound + 1}/${pokemonPerPlayer} — ${player.name}`;
  const badge = document.getElementById('mode-badge');
  badge.textContent = gameMode === 'qcm' ? '🔤 QCM' : '⌨️ Saisie libre';
  badge.className = 'mode-badge ' + gameMode;

  renderScoreboard();

  // Pokémon image
  const imgClass = imageMode === 'real' ? 'poke-img revealed' : 'poke-img';
  document.getElementById('poke-card').innerHTML = `
    <span class="poke-id">#${String(currentPokemon.id).padStart(3, '0')}</span>
    <img class="${imgClass}" src="${currentPokemon.img}" alt="?" />
  `;

  if (gameMode === 'qcm') {
    await renderQCM();
  } else {
    renderInput(player);
  }

  startTimer();
}

// ===== QCM MODE =====
function pickRandom(arr, n) {
  const copy = [...arr];
  const out = [];
  for (let i = 0; i < n && copy.length; i++) {
    const idx = Math.floor(Math.random() * copy.length);
    out.push(copy.splice(idx, 1)[0]);
  }
  return out;
}

async function renderQCM() {
  document.getElementById('qcm-area').style.display = 'block';
  document.getElementById('input-area').style.display = 'none';
  document.getElementById('qcm-grid').innerHTML = '<div style="color:#888;text-align:center;padding:10px;grid-column:span 2">Chargement...</div>';

  const wrong = pickRandom(
    allPokemon.filter(p => p.id !== currentPokemon.id),
    3
  );

  await Promise.all(wrong.map(p => getFrName(p.id)));

  const options = [currentPokemon, ...wrong].map(p => ({
    id: p.id,
    nameFr: frCache[p.id] || p.name
  }));

  currentOptions = options.sort(() => Math.random() - 0.5);

  document.getElementById('qcm-grid').innerHTML = currentOptions.map(opt => `
    <button class="qcm-btn" data-id="${opt.id}">${opt.nameFr}</button>
  `).join('');

  // Attach listeners (no inline onclick, cleaner with modules)
  document.querySelectorAll('.qcm-btn').forEach(btn => {
    btn.addEventListener('click', () => handleQCM(parseInt(btn.dataset.id)));
  });
}

function handleQCM(pokemonId) {
  if (answered) return;
  const isCorrect = pokemonId === currentPokemon.id;

  document.querySelectorAll('.qcm-btn').forEach(btn => {
    btn.disabled = true;
    const btnId = parseInt(btn.dataset.id);
    if (btnId === currentPokemon.id) btn.classList.add('correct');
    else if (btnId === pokemonId && !isCorrect) btn.classList.add('wrong');
  });

  processAnswer(isCorrect, false);
}

// ===== FREE INPUT MODE =====
function renderInput(player) {
  document.getElementById('qcm-area').style.display = 'none';
  document.getElementById('input-area').style.display = 'block';

  const input = document.getElementById('pokemon-input');
  const submitBtn = document.getElementById('submit-btn');
  input.value = '';
  input.className = '';
  input.disabled = false;
  input.placeholder = `${player.name}, c'est quel Pokémon ?`;
  submitBtn.disabled = false;
  submitBtn.onclick = submitFreeAnswer;
  input.onkeydown = e => { if (e.key === 'Enter') submitFreeAnswer(); };
  setTimeout(() => input.focus(), 50);
}

function normalize(str) {
  return str.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
}

function submitFreeAnswer() {
  if (answered) return;
  const val = document.getElementById('pokemon-input').value.trim();
  if (!val) return;
  const isCorrect = normalize(val) === normalize(currentPokemon.nameFr);

  const input = document.getElementById('pokemon-input');
  const submitBtn = document.getElementById('submit-btn');
  input.disabled = true;
  submitBtn.disabled = true;
  input.classList.add(isCorrect ? 'correct' : 'wrong');
  processAnswer(isCorrect, false);
}

// ===== TIMER =====
function startTimer() {
  timeLeft = MAX_TIME;
  questionStartTime = performance.now();
  updateTimerUI();
  timerInterval = setInterval(() => {
    timeLeft--;
    updateTimerUI();
    if (timeLeft <= 0) { clearInterval(timerInterval); if (!answered) processAnswer(false, true); }
  }, 1000);
}

function updateTimerUI() {
  const display = document.getElementById('timer-display');
  const bar = document.getElementById('timer-bar');
  if (!display || !bar) return;
  display.textContent = timeLeft + 's';
  bar.style.width = (timeLeft / MAX_TIME * 100) + '%';
  const urgent = timeLeft <= 5;
  bar.style.background = urgent ? 'var(--danger)' : 'var(--accent)';
  display.classList.toggle('urgent', urgent);
}

// ===== PROCESS ANSWER =====
function processAnswer(isCorrect, timedOut) {
  answered = true;
  clearInterval(timerInterval);

  const player = players[currentPlayerIdx];
  const elapsed = (performance.now() - questionStartTime) / 1000;
  const timeUsed = Math.min(elapsed, MAX_TIME);
  const rawPoints = isCorrect ? Math.max(0, (MAX_TIME - timeUsed) / MAX_TIME * 100) : 0;
  const pointsEarned = Math.round(rawPoints * 100) / 100;
  player.score = Math.round((player.score + pointsEarned) * 100) / 100;
  if (isCorrect) correctAnswers[currentPlayerIdx]++;

  // Reveal Pokémon
  const img = document.querySelector('.poke-img');
  if (img && imageMode === 'shadow') img.classList.add('revealed');

  // If timed out in QCM: highlight correct answer
  if (timedOut && gameMode === 'qcm') {
    document.querySelectorAll('.qcm-btn').forEach(btn => {
      btn.disabled = true;
      if (parseInt(btn.dataset.id) === currentPokemon.id) btn.classList.add('correct');
    });
  }
  if (timedOut && gameMode === 'libre') {
    const input = document.getElementById('pokemon-input');
    input.disabled = true;
    document.getElementById('submit-btn').disabled = true;
    input.classList.add('wrong');
  }

  const msg = document.getElementById('result-msg');
  if (timedOut) {
    msg.textContent = `⏰ Temps ! C'était ${currentPokemon.nameFr}`;
    msg.style.color = '#e67e22';
  } else if (isCorrect) {
    const displayPts = Number.isInteger(pointsEarned) ? pointsEarned : pointsEarned.toFixed(2);
    msg.textContent = `✅ +${displayPts} pts — Bravo ${player.name} !`;
    msg.style.color = '#27ae60';
  } else {
    msg.textContent = `❌ C'était ${currentPokemon.nameFr} !`;
    msg.style.color = '#c0392b';
  }

  renderScoreboard();

  const nextBtn = document.getElementById('next-btn');
  nextBtn.style.display = 'block';
  globalTurn++;

  if (globalTurn >= totalTurns) {
    nextBtn.textContent = '🏆 VOIR LES RÉSULTATS';
    nextBtn.onclick = showResults;
  } else {
    const nextPlayerIdx = globalTurn % players.length;
    nextBtn.textContent = `➜ Au tour de ${players[nextPlayerIdx].name}`;
    nextBtn.onclick = loadQuestion;
  }
}

// ===== RESULTS =====
function showResults() {
  document.getElementById('game').style.display = 'none';
  const resultsEl = document.getElementById('results');
  resultsEl.style.display = 'flex';
  resultsEl.style.flexDirection = 'column';

  // Attach correctAnswers count to each player for sorting
  const ranked = players
    .map((p, i) => ({ ...p, correct: correctAnswers[i] }))
    .sort((a, b) => b.score - a.score);

  function podiumCol(p, height, emoji) {
    return `
      <div class="podium-col">
        <div class="rank-emoji">${emoji}</div>
        <div class="podium-name">${p.name}</div>
        <div class="podium-pts">${Number.isInteger(p.score) ? p.score : p.score.toFixed(2)} pts</div>
        <div class="podium-bar" style="height:${height}px; background:${p.color}">
          ${p.correct}/${pokemonPerPlayer}
        </div>
      </div>`;
  }

  const podiumEl = document.getElementById('podium');
  if (ranked.length === 1) {
    podiumEl.innerHTML = `<div class="podium-col" style="max-width:200px;">${podiumCol(ranked[0], 160, '🏅').trim()}</div>`;
  } else if (ranked.length === 2) {
    const order = [ranked[1], ranked[0]];
    const heights = [110, 160];
    const emojis = ['🥈', '🥇'];
    podiumEl.innerHTML = order.map((p, i) => podiumCol(p, heights[i], emojis[i])).join('');
  } else {
    const order = [ranked[1], ranked[0], ranked[2]];
    const heights = [120, 165, 90];
    const emojis = ['🥈', '🥇', '🥉'];
    podiumEl.innerHTML = order.map((p, i) => podiumCol(p, heights[i], emojis[i])).join('');
  }

  spawnConfetti();
}

// ===== PLAY AGAIN =====
document.getElementById('play-again-btn').onclick = () => {
  clearConfetti();
  sessionStorage.removeItem('gameConfig');
  window.location.href = 'index.html';
};

// ===== CONFETTI =====
function spawnConfetti() {
  const container = document.getElementById('confetti');
  container.innerHTML = '';
  const colors = ['#c8f060','#f06870','#60d0f0','#ffffff','#c8f060','#f0b860'];
  for (let i = 0; i < 90; i++) {
    const el = document.createElement('div');
    el.className = 'confetti-piece';
    el.style.cssText = `
      left: ${Math.random() * 100}vw;
      background: ${colors[Math.floor(Math.random() * colors.length)]};
      width: ${7 + Math.random() * 9}px;
      height: ${7 + Math.random() * 9}px;
      animation-duration: ${2.5 + Math.random() * 3}s;
      animation-delay: ${Math.random() * 2}s;
    `;
    container.appendChild(el);
  }
}

function clearConfetti() {
  document.getElementById('confetti').innerHTML = '';
}

// ===== START =====
init();
