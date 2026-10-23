// Gestion du bandeau de cookies et de Google Analytics
document.addEventListener("DOMContentLoaded", function() {
    const cookieBanner = document.getElementById("cookie-banner");
    const acceptBtn = document.getElementById("cookie-accept");
    const rejectBtn = document.getElementById("cookie-reject");

    // Vérifier si l'utilisateur a déjà fait un choix
    if (!localStorage.getItem("cookie_consent")) {
        cookieBanner.style.display = "block";
    }

    // Accepter les cookies
    acceptBtn.addEventListener("click", function() {
        localStorage.setItem("cookie_consent", "accepted");
        cookieBanner.style.display = "none";
        loadGoogleAnalytics();
    });

    // Refuser les cookies
    rejectBtn.addEventListener("click", function() {
        localStorage.setItem("cookie_consent", "rejected");
        cookieBanner.style.display = "none";
    });

    // Charger Google Analytics si déjà accepté
    if (localStorage.getItem("cookie_consent") === "accepted") {
        loadGoogleAnalytics();
    }

    // Fonction pour charger Google Analytics
    function loadGoogleAnalytics() {
        // Remplace 'G-XXXXXXXXXX' par ton ID de mesure Google Analytics
        const GA_ID = "G-VKSG8Q1R68";

        const script = document.createElement("script");
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
        document.head.appendChild(script);

        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', GA_ID);
    }
});