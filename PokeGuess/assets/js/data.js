// ===== DATA.JS =====
// Handles Pokémon data fetching with sessionStorage caching

const CACHE_KEY_POKEMON = 'pokeguess_pokemon';
const CACHE_KEY_FR = 'pokeguess_fr_names';

export let allPokemon = [];
export let frCache = {};

export async function loadPokemon() {
  // Try sessionStorage cache first
  const cached = sessionStorage.getItem(CACHE_KEY_POKEMON);
  if (cached) {
    allPokemon.push(...JSON.parse(cached)); // ← was: allPokemon = JSON.parse(cached)
    const cachedFr = sessionStorage.getItem(CACHE_KEY_FR);
    if (cachedFr) Object.assign(frCache, JSON.parse(cachedFr)); // ← was: frCache = JSON.parse(cachedFr)
    return allPokemon;
  }

  const res = await fetch('https://pokeapi.co/api/v2/pokemon?limit=1025');
  const data = await res.json();
  allPokemon.push(...data.results.map((p, i) => ({
    id: i + 1,
    name: p.name,
    img: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${i + 1}.png`
  })));

  sessionStorage.setItem(CACHE_KEY_POKEMON, JSON.stringify(allPokemon));
  return allPokemon;
}

export async function getFrName(id) {
  if (frCache[id]) return frCache[id];

  const res = await fetch(`https://pokeapi.co/api/v2/pokemon-species/${id}/`);
  const data = await res.json();
  const fr = data.names.find(n => n.language.name === 'fr');
  const name = fr ? fr.name : (data.names.find(n => n.language.name === 'en')?.name || String(id));
  frCache[id] = name;

  // Persist fr cache incrementally
  sessionStorage.setItem(CACHE_KEY_FR, JSON.stringify(frCache));
  return name;
}
