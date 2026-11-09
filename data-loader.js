/**
 * IELTS Boost data loader — Stage 43
 * Loads the content payload separately from the document shell.
 */
export async function loadAppData() {
  const url = new URL('./data/app-data.json', document.baseURI);
  let response;
  try {
    response = await fetch(url.href, { cache: 'default', credentials: 'same-origin' });
  } catch (cause) {
    const error = new Error('IELTS Boost kontent faylini yuklab bo‘lmadi. Internetni tekshir yoki offline cache mavjudligini tasdiqla.');
    error.code = 'APP_DATA_NETWORK';
    error.cause = cause;
    throw error;
  }
  if (!response.ok) {
    const error = new Error(`IELTS Boost kontent fayli yuklanmadi (HTTP ${response.status}).`);
    error.code = 'APP_DATA_HTTP';
    throw error;
  }
  let data;
  try {
    data = await response.json();
  } catch (cause) {
    const error = new Error('IELTS Boost kontent fayli JSON formatida o‘qilmadi.');
    error.code = 'APP_DATA_INVALID_JSON';
    error.cause = cause;
    throw error;
  }
  if (!data || typeof data !== 'object' || !data.plan || !Array.isArray(data.core?.days) || !Array.isArray(data.words)) {
    const error = new Error('IELTS Boost kontent faylining tuzilmasi kutilgan formatga mos emas.');
    error.code = 'APP_DATA_SCHEMA';
    throw error;
  }
  if (data.core.days.length !== 84) {
    const error = new Error(`84 kunlik dastur to‘liq yuklanmadi (${data.core.days.length}/84).`);
    error.code = 'APP_DATA_CURRICULUM';
    throw error;
  }
  return data;
}
