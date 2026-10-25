/* El Ouabdi Immobilier - bouton cœur des favoris.
   Lit l'état initial dans <body data-favoris="1,5,8"> et appelle la vue toggle_favori (POST). */
(function () {
  var body = document.body;
  var modele = body.getAttribute("data-favori-url") || "";            // ex. /favoris/0/toggle/
  var csrf = (document.querySelector('meta[name="csrf-token"]') || {}).content || "";
  var ids = (body.getAttribute("data-favoris") || "").split(",").filter(Boolean);

  function dessiner(btn, actif) {
    btn.setAttribute("aria-pressed", actif ? "true" : "false");
    var icone = btn.querySelector("i");
    if (icone) {                                  // icône FontAwesome
      icone.classList.toggle("fa-solid", actif);
      icone.classList.toggle("fa-regular", !actif);
    } else {                                      // émoji
      btn.textContent = actif ? "❤️" : "🤍";
    }
  }

  function majBoutons() {
    document.querySelectorAll(".btn-favori").forEach(function (btn) {
      dessiner(btn, ids.indexOf(String(btn.getAttribute("data-id"))) !== -1);
    });
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".btn-favori");
    if (!btn || !modele) return;
    e.preventDefault();
    e.stopPropagation();
    var id = String(btn.getAttribute("data-id"));
    btn.disabled = true;
    fetch(modele.replace("/0/", "/" + id + "/"), {
      method: "POST",
      headers: { "X-CSRFToken": csrf, "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin"
    })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var present = ids.indexOf(id) !== -1;
        if (data.action === "ajouté" && !present) ids.push(id);
        if (data.action === "retiré") ids = ids.filter(function (x) { return x !== id; });
        majBoutons();
      })
      .catch(function () { /* échec silencieux : l'état affiché ne change pas */ })
      .then(function () { btn.disabled = false; });
  });

  majBoutons();
})();
