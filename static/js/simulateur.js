(function () {
  var root = document.getElementById("sim");
  if (!root) return;
  var lang = document.documentElement.lang === "ar" ? "ar-MA" : "fr-FR";
  var devise = root.getAttribute("data-devise") || "MAD";
  var fmt = new Intl.NumberFormat(lang, { maximumFractionDigits: 0 });
  var $ = function (id) { return document.getElementById(id); };
  var champs = ["s-prix", "s-apport", "s-duree", "s-taux"].map($);

  function montrer(id, valeur) {
    $(id).textContent = isFinite(valeur) ? fmt.format(Math.round(valeur)) + " " + devise : "–";
  }

  function calculer() {
    var prix = parseFloat($("s-prix").value) || 0;
    var apport = parseFloat($("s-apport").value) || 0;
    var annees = parseFloat($("s-duree").value) || 0;
    var taux = parseFloat($("s-taux").value) || 0;
    var emprunt = Math.max(prix - apport, 0);
    var n = Math.round(annees * 12);
    if (!emprunt || !n) {
      ["r-mensualite", "r-emprunt", "r-total", "r-interets"].forEach(function (id) { $(id).textContent = "–"; });
      return;
    }
    var r = taux / 100 / 12;
    var mensualite = r === 0 ? emprunt / n : (emprunt * r) / (1 - Math.pow(1 + r, -n));
    var total = mensualite * n;
    montrer("r-mensualite", mensualite);
    montrer("r-emprunt", emprunt);
    montrer("r-total", total);
    montrer("r-interets", total - emprunt);
  }

  champs.forEach(function (c) { c.addEventListener("input", calculer); });
  calculer();
})();
// --- GESTION DES FAVORIS ---
document.addEventListener("DOMContentLoaded", function() {
    const favorisBtns = document.querySelectorAll('.btn-favori');
    
    favorisBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const bienId = this.getAttribute('data-id');
            
            fetch(`/favoris/${bienId}/toggle/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.action === 'ajouté') {
                    this.innerHTML = '❤️';
                    this.style.color = 'red';
                } else {
                    this.innerHTML = '🤍';
                    this.style.color = 'black';
                }
            });
        });
    });
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});