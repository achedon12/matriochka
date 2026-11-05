/* Matriochka site. Small progressive enhancements; every page works without it. */
(function () {
  document.documentElement.classList.add("js");

  // Hero: pointing at a world in the legend lights up its doll.
  var dolls = document.querySelector(".dolls");
  if (dolls) {
    var light = function (w) {
      dolls.classList.toggle("hl", w !== null);
      dolls.querySelectorAll(".doll").forEach(function (d) {
        d.classList.toggle("on", d.getAttribute("data-w") === w);
      });
    };
    document.querySelectorAll(".legend a").forEach(function (a) {
      var w = a.getAttribute("data-w");
      a.addEventListener("mouseenter", function () { light(w); });
      a.addEventListener("focus", function () { light(w); });
      a.addEventListener("mouseleave", function () { light(null); });
      a.addEventListener("blur", function () { light(null); });
    });
  }

  // Bestiary: filter the creature groups by world.
  var buttons = document.querySelectorAll(".fbtn");
  if (buttons.length) {
    var groups = document.querySelectorAll(".mgroup[data-world]");
    var show = function (w) {
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-world") === w)); });
      groups.forEach(function (g) { g.hidden = !(w === "all" || g.getAttribute("data-world") === w); });
    };
    buttons.forEach(function (b) {
      b.addEventListener("click", function () { show(b.getAttribute("data-world")); });
    });
    var m = /^#(?:world|mob)-/.test(location.hash) ? document.querySelector(location.hash) : null;
    if (m) {
      var g = m.closest(".mgroup[data-world]");
      if (g) show("all");
    }
  }

  // Worlds: mark the world currently on screen in the side index.
  var toc = document.querySelectorAll(".toc a");
  if (toc.length && "IntersectionObserver" in window) {
    var byId = {};
    toc.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && byId[en.target.id]) {
          toc.forEach(function (a) { a.classList.remove("on"); a.removeAttribute("aria-current"); });
          byId[en.target.id].classList.add("on");
          byId[en.target.id].setAttribute("aria-current", "location");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    document.querySelectorAll(".world[id]").forEach(function (s) { io.observe(s); });
  }
})();
