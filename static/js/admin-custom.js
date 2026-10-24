/* El Ouabdi Immobilier - barre latérale réduite aux icônes à la première visite de l'admin.
   Elle s'élargit au survol de la souris. Le bouton « menu » (☰) la déplie, et ce choix est
   mémorisé par Jazzmin (cookie « jazzy_menu »). Ce script ne s'applique qu'une seule fois. */
(function () {
  function lireCookie(nom) {
    var m = document.cookie.match(new RegExp("(?:^|; )" + nom + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }

  function reduireMenu() {
    if (!document.querySelector(".app-sidebar")) return;
    if (lireCookie("jazzy_menu")) return; // choix déjà fait par l'utilisateur
    document.cookie = "jazzy_menu=closed; path=/; max-age=31536000; SameSite=Lax";
    document.body.classList.add("sidebar-collapse");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", reduireMenu);
  } else {
    reduireMenu();
  }
})();