document.addEventListener("DOMContentLoaded", function () {
    // Vérifier si l'écran est petit (moins de 768px)
    if (window.innerWidth <= 768) {
        const footerContainer = document.querySelector(".footer-container");
        const footerList = document.querySelector(".footer-list");

        // Créer un bouton pour afficher/masquer le menu
        const menuButton = document.createElement("button");
        menuButton.innerText = "Menu";
        menuButton.classList.add("footer-menu-btn");
        
        // Insérer le bouton avant la liste du footer
        footerContainer.insertBefore(menuButton, footerList);

        // Cacher la liste au début
        footerList.style.display = "none";

        // Ajouter un événement au clic pour afficher/masquer le menu
        menuButton.addEventListener("click", function () {
            if (footerList.style.display === "none") {
                footerList.style.display = "block";
            } else {
                footerList.style.display = "none";
            }
        });
    }
});
