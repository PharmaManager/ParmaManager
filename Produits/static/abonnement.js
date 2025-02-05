function toggleFeatures() {
    var features = document.getElementById('features');
    var footer = document.getElementById('footer');
    var button = document.getElementById('toggle-button');
    var introText = document.getElementById('intro-text');

    if (features.style.display === 'none' || features.classList.contains('hidden')) {
        features.classList.remove('hidden');
        features.style.display = 'flex';  // Assurez-vous que l'élément est affiché
        footer.classList.remove('hidden');
        footer.style.display = 'block';  // Assurez-vous que le footer est affiché
        introText.style.opacity = '0';  // Intro devient invisible
        button.querySelector('button').textContent = 'Cacher les fonctionnalités'; // Modifier le texte du bouton
        button.style.transform = 'translateY(230px)';
        // Fade in les éléments
        setTimeout(function() {
            features.style.opacity = '1';
            footer.style.opacity = '1';

            features.style.transform = 'translateY(-160px)';
            footer.style.transform = 'translateY(-60px)';

        }, 10);
    } else {
        features.classList.add('hidden');
        features.style.display = 'none';  // Masquer la section avec display: none
        footer.classList.add('hidden');
        footer.style.display = 'none';  // Masquer le footer avec display: none
        introText.style.opacity = '1';  // Intro redevient visible
        button.querySelector('button').textContent = 'Voir les fonctionnalités'; // Réinitialiser le texte du bouton
   
      
         // Réinitialiser la position lorsque caché
        features.style.transform = 'translateY(0)';
        footer.style.transform = 'translateY(0)';

    }
}

function startApp() {
    window.location.href = "/acceuil/";
}






document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/verifier-essai/")
        .then(response => response.json())
        .then(data => {
            const messageBox = document.createElement("div");
            messageBox.classList.add("essai-message");
  
            if (data.essai_expire) {
                messageBox.classList.add("expire");  // Ajouter la classe expire pour ajuster la position
                messageBox.innerHTML = `
                    <p>Votre essai gratuit a expiré !</p>
                    <a href="/payment/checkout/" class="btn-renew">Souscrire maintenant</a>
                `;
            } else {
                messageBox.innerHTML = `<p>Il vous reste ${data.jours_restants} jours d'essai gratuit.</p>`;
            }
  
            document.body.appendChild(messageBox);
        })
        .catch(error => console.error("Erreur lors de la vérification de l'essai :", error));
  });

  document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/verifier-abonnement/")
        .then(response => response.json())
        .then(data => {
            const messageElement = document.getElementById("message-abonnement");

            if (data.abonnement_expire) {
                // Si l'abonnement est expiré, redirection vers la page de paiement
                alert("Votre abonnement a expiré ! Vous allez être redirigé vers la page de paiement.");
                window.location.href = "/payment/checkout/";
            } else if (data.jours_restants !== undefined) {
                // Si l'utilisateur a un abonnement actif
                messageElement.innerText = `Il vous reste ${data.jours_restants} jours avant l'expiration de votre abonnement.`;

                // Appliquer la couleur en fonction du nombre de jours restants
                if (data.jours_restants <= 3) {
                    messageElement.style.color = "red";  // Rouge si 3 jours ou moins
                } else {
                    messageElement.style.color = "green";  // Vert si plus de 3 jours
                }
            } else {
                // Si aucun abonnement n'est souscrit (aucun message affiché)
                messageElement.innerText = '';  // Assurez-vous que le message est vide si pas d'abonnement
            }
        })
        .catch(error => console.error("Erreur lors de la vérification de l'abonnement :", error));
});

