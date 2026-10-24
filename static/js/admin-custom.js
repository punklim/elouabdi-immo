/* El Ouabdi Immobilier - barre latérale réduite aux icônes dès l'ouverture de l'admin.
   Elle s'élargit au survol de la souris, et le bouton « menu » (☰) permet de la déplier. */
(function () {
  function reduireMenu() {
    var b = document.body;
    if (!b || b.classList.contains("eo-init")) return;
    if (!document.querySelector(".main-sidebar")) return;
    b.classList.add("sidebar-mini", "sidebar-collapse", "eo-init");
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", reduireMenu);
  } else {
    reduireMenu();
  }
})();