/**
 * IELTS Boost Stage 50 — deployment-relative PWA manifest validation.
 * Correctly validates a manifest whose id/scope/start_url are relative to
 * the manifest URL, including GitHub Pages repository subpaths.
 */
export function inspectPwaManifest(manifest, manifestUrl, pageUrl) {
  const fail = reason => ({ valid: false, reason, scopeUrl: null, startUrl: null, idUrl: null, currentWithinScope: false, iconsValid: false });
  if (!manifest || typeof manifest !== 'object') return fail('Manifest JSON is missing or invalid.');
  let base, page, scopeUrl, startUrl, idUrl;
  try {
    base = new URL(String(manifestUrl), String(pageUrl));
    page = new URL(String(pageUrl));
    scopeUrl = new URL(String(manifest.scope || './'), base);
    startUrl = new URL(String(manifest.start_url || './'), base);
    idUrl = new URL(String(manifest.id || manifest.start_url || './'), base);
  } catch {
    return fail('Manifest URL, scope, start_url or id could not be resolved.');
  }
  const sameOrigin = target => target.origin === page.origin;
  const withinScope = target => sameOrigin(target) && target.pathname.startsWith(scopeUrl.pathname);
  const currentWithinScope = withinScope(page);
  const icons = Array.isArray(manifest.icons) ? manifest.icons : [];
  const has192 = icons.some(x => String(x.sizes || '').split(/\s+/).includes('192x192'));
  const has512 = icons.some(x => String(x.sizes || '').split(/\s+/).includes('512x512'));
  const iconsHaveSources = icons.length > 0 && icons.every(x => typeof x.src === 'string' && !!x.src.trim());
  const iconsValid = has192 && has512 && iconsHaveSources;
  const valid = !!manifest.short_name
    && manifest.display === 'standalone'
    && currentWithinScope
    && withinScope(startUrl)
    && withinScope(idUrl)
    && iconsValid;
  const reasons = [];
  if (!manifest.short_name) reasons.push('short_name is missing.');
  if (manifest.display !== 'standalone') reasons.push('display must be standalone.');
  if (!currentWithinScope) reasons.push('Current page is outside manifest scope.');
  if (!withinScope(startUrl)) reasons.push('start_url is outside manifest scope or origin.');
  if (!withinScope(idUrl)) reasons.push('id is outside manifest scope or origin.');
  if (!iconsValid) reasons.push('192x192 and 512x512 icons with sources are required.');
  return {
    valid,
    reason: reasons.join(' '),
    manifestUrl: base.href,
    scopeUrl: scopeUrl.href,
    scopePath: scopeUrl.pathname,
    startUrl: startUrl.href,
    idUrl: idUrl.href,
    currentWithinScope,
    iconsValid,
    iconSizes: { has192, has512 }
  };
}
