$(document).ready(function () {
    let rowIndex = 1; // Compteur pour attribuer des indices uniques aux nouvelles lignes

    // Fonction pour mettre à jour le montant total
    function updateTotal() {
        let total = 0;
        $(".produit-row").each(function () {
            const quantity = parseFloat($(this).find(".quantite-input").val()) || 0;
            const price = parseFloat($(this).find(".price-input").val()) || 0;
            const discount = parseFloat($(this).find(".remise-input").val()) || 0;
            // Calcul du total pour chaque ligne
            total += quantity * price * (1 - discount / 100);
        });

        // Appliquer la remise globale
        const globalDiscount = parseFloat($("#remise_globale").val()) || 0;
        total *= (1 - globalDiscount / 100);

        // Mettre à jour le champ "Montant Total"
        $("#total-global").val(total.toFixed(2));
    }

    // Ajout d'une nouvelle ligne produit
    $("#add-product").click(function () {
        const newRow = $(".produit-row:first").clone(); // Cloner la première ligne
        newRow.find("input, select").each(function () {
            const name = $(this).attr("name");
            const id = $(this).attr("id");
            if (name) $(this).attr("name", name.replace(/\d+/, rowIndex)); // Mettre à jour les noms
            if (id) $(this).attr("id", id.replace(/\d+/, rowIndex));       // Mettre à jour les IDs

            // Réinitialiser les valeurs avec des valeurs par défaut
            if ($(this).hasClass("quantite-input")) {
                $(this).val(1); // Quantité par défaut : 1
            } else if ($(this).hasClass("remise-input")) {
                $(this).val(0); // Remise par défaut : 0
            } else {
                $(this).val(""); // Réinitialiser les autres champs
            }
        });

        newRow.find(".price-input").val(""); // Réinitialiser le prix
        $("#produits-container").append(newRow); // Ajouter la nouvelle ligne
        rowIndex++; // Incrémenter le compteur
    });

    // Mettre à jour le prix lorsque le produit sélectionné change
    $(document).on("change", ".produit-select", function () {
        const price = $(this).find(":selected").data("price");
        $(this).closest(".produit-row").find(".price-input").val(price); // Affecter le prix au champ correspondant
        updateTotal(); // Recalculer le total
    });

    // Recalculer le total lorsqu'un champ quantité, remise ou remise globale change
    $(document).on("input", ".quantite-input, .remise-input, #remise_globale", updateTotal);

    // Supprimer une ligne produit
    $(document).on("click", ".remove-row", function () {
        if ($(".produit-row").length > 1) {
            // Supprime uniquement la ligne du bouton cliqué
            $(this).closest(".produit-row").remove();
            updateTotal(); // Recalculer le total après suppression
        } else {
            alert("Vous ne pouvez pas supprimer cette ligne."); // Message d'avertissement si c'est la dernière ligne
        }
    });
});


//   SUPPRIMER LE MESSAGE D'ERREUR APRES ACTUALISATION DE LA PAGE


// Supprime les messages après 5 secondes
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
      const alertMessages = document.querySelectorAll(".alert");
      alertMessages.forEach(function (message) {
        message.remove();
      });
    }, 10000);
  });
  
  
