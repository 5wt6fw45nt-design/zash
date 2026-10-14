// Fechas en hora de Madrid, que es la que entiende el usuario.

export function madrid(ts, timeZone = 'Europe/Madrid') {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat('en-CA', {
      timeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hourCycle: 'h23',
    })
      .formatToParts(ts)
      .map((p) => [p.type, p.value]),
  );
  return { date: `${parts.year}-${parts.month}-${parts.day}`, hm: `${parts.hour}:${parts.minute}` };
}

export function humanDate(ts, timeZone = 'Europe/Madrid') {
  return new Intl.DateTimeFormat('es-ES', { timeZone, day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' }).format(ts);
}

const toMin = (hm) => {
  const [h, m] = hm.split(':').map(Number);
  return h * 60 + m;
};

/** true si `hm` está en la hora siguiente a `target` (para no mandar resúmenes a deshoras tras un reinicio). */
export function inWindow(hm, target, minutes = 60) {
  const d = toMin(hm) - toMin(target);
  return d >= 0 && d < minutes;
}
