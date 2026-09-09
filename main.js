// Lazy-load and play muted loops only while on screen. Poster shows until then.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var vids = document.querySelectorAll('video[data-src]');
  if (reduce || !('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) {
        if (!v.src) { v.src = v.dataset.src; v.load(); }
        v.play().catch(function () {});
      } else if (v.src) {
        v.pause();
      }
    });
  }, { rootMargin: '200px 0px', threshold: 0.1 });
  vids.forEach(function (v) { io.observe(v); });
})();

// Agent attribution with no backend: ?ref=somchai becomes "(via somchai)" in the WhatsApp prefill.
(function () {
  var ref = new URLSearchParams(location.search).get('ref');
  if (!ref) return;
  ref = ref.replace(/[^\w\- ]/g, '').slice(0, 40);
  if (!ref) return;
  document.querySelectorAll('a[data-wa]').forEach(function (a) {
    var u = new URL(a.href);
    u.searchParams.set('text', (u.searchParams.get('text') || '') + ' (via ' + ref + ')');
    a.href = u.toString();
  });
})();
