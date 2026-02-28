// ===== SETUP.JS =====
// Handles the home/setup page logic

import { loadPokemon } from './data.js';

const COLORS = ['#E3350D','#2A75BB','#27ae60','#9b59b6','#e67e22','#1abc9c','#e91e63','#ff9800'];

let numPlayers = 2;
let pokemonPerPlayer = 10;
let gameMode = 'qcm';
let imageMode = 'real';

// ===== RENDER PLAYER INPUTS =====
function renderPlayerInputs() {
  const container = document.getElementById('player-inputs');
  const existing = [...container.querySelectorAll('.player-name-input')].map(i => i.value);
  container.innerHTML = '';
  for (let i = 0; i < numPlayers; i++) {
    const row = document.createElement('div');
    row.className = 'player-row';
    const dot = document.createElement('div');
    dot.className = 'player-dot';
    dot.style.background = COLORS[i];
    const input = document.createElement('input');
    input.className = 'player-name-input';
    input.type = 'text';
    input.placeholder = `Joueur ${i + 1}`;
    input.value = existing[i] || '';
    row.appendChild(dot);
    row.appendChild(input);
    container.appendChild(row);
  }
}

// ===== EVENT LISTENERS =====
document.getElementById('players-down').onclick = () => {
  if (numPlayers > 1) { numPlayers--; document.getElementById('players-val').textContent = numPlayers; renderPlayerInputs(); }
};
document.getElementById('players-up').onclick = () => {
  if (numPlayers < 8) { numPlayers++; document.getElementById('players-val').textContent = numPlayers; renderPlayerInputs(); }
};

document.getElementById('round-opts').addEventListener('click', e => {
  const opt = e.target.closest('.round-opt');
  if (!opt) return;
  document.querySelectorAll('.round-opt').forEach(o => o.classList.remove('active'));
  opt.classList.add('active');
  pokemonPerPlayer = parseInt(opt.dataset.val);
});

function setupToggle(id, onActivate) {
  const btn = document.getElementById(id);
  btn.addEventListener('click', () => {
    const isActive = btn.dataset.active === 'true';
    btn.dataset.active = !isActive;
    btn.classList.toggle('active', !isActive);
    onActivate(!isActive);
  });
}

setupToggle('toggle-libre', active => { gameMode = active ? 'libre' : 'qcm'; });
setupToggle('toggle-shadow', active => { imageMode = active ? 'shadow' : 'real'; });

document.getElementById('start-btn').onclick = startGame;

// ===== START GAME =====
function pickRandom(arr, n) {
  const copy = [...arr];
  const out = [];
  for (let i = 0; i < n && copy.length; i++) {
    const idx = Math.floor(Math.random() * copy.length);
    out.push(copy.splice(idx, 1)[0]);
  }
  return out;
}

async function startGame() {
  const { allPokemon, getFrName } = await import('./data.js');

  const inputs = document.querySelectorAll('.player-name-input');
  const players = Array.from({ length: numPlayers }, (_, i) => ({
    name: inputs[i]?.value.trim() || `Joueur ${i + 1}`,
    color: COLORS[i],
    score: 0
  }));

  const decks = players.map(() => pickRandom(allPokemon, pokemonPerPlayer));

  const btn = document.getElementById('start-btn');
  btn.textContent = 'Chargement...';
  btn.disabled = true;

  // Pre-fetch all French names
  const allIds = [...new Set(decks.flat().map(p => p.id))];
  await Promise.all(allIds.map(id => getFrName(id)));

  // Save game config to sessionStorage and navigate
  sessionStorage.setItem('gameConfig', JSON.stringify({
    players,
    decks,
    pokemonPerPlayer,
    gameMode,
    imageMode
  }));

  window.location.href = 'game.html';
}

// ===== INIT =====
loadPokemon()
  .then(() => {
    document.getElementById('loading-wrap').style.display = 'none';
    document.getElementById('setup-form').style.display = 'flex';
    renderPlayerInputs();
  })
  .catch(err => {
    document.getElementById('loading-wrap').innerHTML =
      `<div style="color:var(--danger);text-align:center">❌ Erreur de chargement.<br>${err.message}</div>`;
  });
