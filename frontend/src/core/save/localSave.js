const SAVE_KEY = 'gagaToday:playerState:mvp';

export function loadPlayerState() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function savePlayerState(playerState) {
  localStorage.setItem(SAVE_KEY, JSON.stringify(playerState));
}

export function clearPlayerState() {
  localStorage.removeItem(SAVE_KEY);
}
