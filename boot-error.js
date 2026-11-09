/** Accessible boot-failure UI. Never exposes secrets or raw stack traces. */
export function showBootError(error) {
  console.error('[IELTS Boost boot]', error?.code || 'UNKNOWN', error);
  const host = document.querySelector('#app') || document.body;
  host.innerHTML = `
    <section role="alert" aria-live="assertive" class="card" style="max-width:720px;margin:24px auto;padding:24px">
      <div class="eyebrow">IELTS BOOST · STARTUP CHECK</div>
      <h2>Platforma ma’lumotlarini yuklashda muammo yuz berdi</h2>
      <p>${String(error?.message || 'Noma’lum xatolik yuz berdi.').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]))}</p>
      <p class="muted small">Internetga ulanishni tekshir. Agar avval platformani ochgan bo‘lsang, sahifani qayta yukla. Offline fayllar cache’da bo‘lishi kerak.</p>
      <button type="button" class="btn primary" id="appBootRetry">Qayta yuklash</button>
    </section>`;
  document.querySelector('#appBootRetry')?.addEventListener('click', () => location.reload());
}
