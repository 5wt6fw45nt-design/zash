// Cliente mínimo de la Bot API. Sin librerías: fetch y poco más.

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export function createApi(token, fetchFn = fetch) {
  const base = `https://api.telegram.org/bot${token}/`;
  async function call(method, params = {}) {
    const res = await fetchFn(base + method, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(params),
    });
    const data = await res.json();
    if (data.ok) return data.result;
    const err = new Error(`${method}: ${data.description}`);
    err.code = data.error_code;
    err.retryAfter = data.parameters?.retry_after;
    throw err;
  }
  return { call };
}

export const message = (chatId, text, extra = {}) => ({
  chat_id: chatId,
  text,
  parse_mode: 'HTML',
  link_preview_options: { is_disabled: true },
  ...extra,
});

/**
 * Envía hasta `budget` mensajes de la cola. Cada envío es una petición externa y Cloudflare
 * limita cuántas caben en una ejecución, así que lo que no cabe sale en la siguiente (1 min).
 */
export async function drainOutbox(api, db, budget, perSecond = 25) {
  if (budget <= 0) return 0;
  let sent = 0;
  const done = [];
  for (const m of await db.peekOutbox(budget)) {
    try {
      await api.call('sendMessage', message(m.chat_id, m.text));
      sent++;
    } catch (e) {
      if (e.code === 429) break; // Telegram pide pausa: este y el resto, en la próxima tanda
      if (e.code === 403) await db.markBlocked(m.chat_id);
      else console.error('[outbox]', m.chat_id, e.message);
    }
    done.push(m.id);
    await sleep(1000 / perSecond);
  }
  await db.deleteOutboxMany(done); // un solo DELETE para toda la tanda (límite de consultas de D1)
  return sent;
}
