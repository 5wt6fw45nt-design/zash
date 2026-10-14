// País de quien está hablando con el bot, mientras se le contesta (formato de números, moneda).
// Los envíos masivos (resúmenes, avisos) no pasan por aquí y usan el formato de España.
import { AsyncLocalStorage } from 'node:async_hooks';

const store = new AsyncLocalStorage();
export const withCountry = (country, fn) => store.run(country, fn);
export const currentCountry = () => store.getStore() || null;
export const currentLocale = () => store.getStore()?.locale || 'es-ES';
