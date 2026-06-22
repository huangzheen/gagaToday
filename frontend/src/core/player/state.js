export function createPlayerState(startState) {
  return cloneState(startState);
}

export function toStatusBarStats(playerState) {
  return {
    name: playerState.name,
    age: playerState.age,
    language: {
      german: playerState.skills.german.cefr,
      english: playerState.skills.english.cefr,
    },
    mood: playerState.status.mood,
    energy: playerState.status.energy,
    money: Number(playerState.wallet.cash_eur.toFixed(2)),
    date: {
      year: playerState.date.year,
      month: playerState.date.month,
      day: playerState.date.day,
    },
    location: playerState.city,
  };
}

export function clamp(value, min = 0, max = 100) {
  return Math.max(min, Math.min(max, value));
}

export function cloneState(value) {
  return JSON.parse(JSON.stringify(value));
}
