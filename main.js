// Lazy-load and play muted loops only while on screen. Poster shows until then.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var vids = document.querySelectorAll('video[data-src]');
  if (reduce || !('IntersectionObserver' in window)) return;

  var heroVids = Array.prototype.filter.call(vids, function (v) {
    return v.dataset.sync === 'hero';
  });
  var heroIntersecting = [];
  var heroGroup = [];
  var heroEndedBound = [];

  function isHeroIntersecting(v) { return heroIntersecting.indexOf(v) !== -1; }
  function isEndedBound(v) { return heroEndedBound.indexOf(v) !== -1; }

  function displayedActiveHeroVids() {
    return heroVids.filter(function (v) {
      return v.offsetParent !== null && isHeroIntersecting(v) && v.src;
    });
  }

  function heroReady(v) { return v.readyState >= 4; }

  function playHeroGroupTogether(group) {
    group.forEach(function (v) { v.currentTime = 0; });
    group.forEach(function (v) { v.play().catch(function () {}); });
  }

  function onHeroEnded() {
    if (!heroGroup.length) return;
    playHeroGroupTogether(heroGroup);
  }

  function bindEnded(v) {
    if (isEndedBound(v)) return;
    heroEndedBound.push(v);
    v.addEventListener('ended', onHeroEnded);
  }

  function startHeroSync() {
    var group = displayedActiveHeroVids();
    heroGroup = group;
    if (!group.length) return;

    if (group.length === 1) {
      var only = group[0];
      only.loop = true;
      only.play().catch(function () {});
      return;
    }

    group.forEach(function (v) { v.loop = false; });
    group.forEach(bindEnded);

    if (group.every(heroReady)) {
      playHeroGroupTogether(group);
      return;
    }
    var launched = false;
    function tryLaunch() {
      if (launched || !group.every(heroReady)) return;
      launched = true;
      playHeroGroupTogether(group);
    }
    group.forEach(function (v) {
      v.addEventListener('canplaythrough', tryLaunch);
    });
  }

  var io = new IntersectionObserver(function (entries) {
    var heroTouched = false;
    entries.forEach(function (e) {
      var v = e.target;
      var isHero = v.dataset.sync === 'hero';
      if (e.isIntersecting) {
        if (!v.src) { v.src = v.dataset.src; v.load(); }
        if (isHero) {
          if (!isHeroIntersecting(v)) heroIntersecting.push(v);
          heroTouched = true;
        } else {
          v.play().catch(function () {});
        }
      } else if (v.src) {
        v.pause();
        if (isHero) {
          var idx = heroIntersecting.indexOf(v);
          if (idx !== -1) heroIntersecting.splice(idx, 1);
          heroTouched = true;
        }
      }
    });
    if (heroTouched) startHeroSync();
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
