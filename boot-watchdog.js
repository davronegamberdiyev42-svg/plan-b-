/* IELTS Boost boot watchdog — visible diagnostics instead of a silent blank screen. */
(() => {
  "use strict";
  let warningShown = false;
  const show = (heading, message, path) => {
    if (window.__IELTS_BOOST_APP_READY__ || warningShown) return;
    warningShown = true;
    const box = document.createElement("section");
    box.setAttribute("role", "alert");
    box.setAttribute("aria-live", "assertive");
    box.style.cssText = "margin:12px auto;max-width:900px;padding:16px;border:2px solid #b91c1c;border-radius:12px;background:#fff7ed;color:#7f1d1d;font:15px/1.5 system-ui,sans-serif;position:relative;z-index:99999";
    const title = document.createElement("strong");
    title.textContent = heading;
    const body = document.createElement("p");
    body.textContent = message;
    box.append(title, body);
    if (path) {
      const code = document.createElement("code");
      code.style.cssText = "display:block;overflow-wrap:anywhere;white-space:normal";
      code.textContent = path;
      box.append(code);
    }
    const tip = document.createElement("p");
    tip.textContent = "ZIP ichidagi index.html, assets/, data/, audio/ va qolgan papkalarni plan-b- repository’ning main branch root qismiga birgalikda joyla. ZIP faylining o‘zini yoki faqat index.html faylini yuklash yetarli emas. HTTPS GitHub Pages manzilidan och.";
    box.append(tip);
    document.body.prepend(box);
  };
  document.addEventListener("error", event => {
    const node = event.target;
    if (!node || !/^(SCRIPT|LINK)$/.test(node.tagName || "")) return;
    if (node.tagName === "LINK" && node.rel !== "stylesheet") return;
    show(
      node.tagName === "LINK" ? "IELTS Boost dizayn fayli topilmadi" : "IELTS Boost JavaScript fayli yuklanmadi",
      node.tagName === "LINK"
        ? "CSS faylini topib bo‘lmadi. Shu sabab ilova bezaksiz, oddiy matn ko‘rinishida chiqishi mumkin."
        : "Asosiy JavaScript yoki uning moduli topilmadi. Shu sabab dashboard va Kirish tugmasi ishlamasligi mumkin.",
      node.href || node.src || ""
    );
  }, true);
  window.addEventListener("error", event => {
    if (event.target === window && !window.__IELTS_BOOST_BOOT_FAILED__) {
      show("IELTS Boost JavaScript xatosi", event.message || "Ilova ishga tushayotganda xato yuz berdi.", event.filename || "");
    }
  });
  window.setTimeout(() => {
    if (!window.__IELTS_BOOST_APP_READY__ && !window.__IELTS_BOOST_BOOT_FAILED__) {
      show(
        "IELTS Boost ishga tushmadi",
        "Ilova 30 soniyada ishga tushmadi. Ko‘pincha CSS/JS/data fayllari repository root’dan topilmayotgan bo‘ladi.",
        new URL("./assets/js/app.js", location.href).href
      );
    }
  }, 30000);
})();
