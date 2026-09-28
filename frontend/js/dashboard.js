const usernameDisplay = document.getElementById(
    "username-display"
);

const roleDisplay = document.getElementById(
    "role-display"
);

const welcomeUsername = document.getElementById(
    "welcome-username"
);

const userInitial = document.getElementById(
    "user-initial"
);

const boutonDeconnexion = document.getElementById(
    "logout-button"
);

const adminSection = document.getElementById(
    "admin-section"
);

const adminNavLink = document.getElementById(
    "admin-nav-link"
);

const materielsGrid = document.getElementById(
    "materiels-grid"
);

const catalogueLoading = document.getElementById(
    "catalogue-loading"
);

const catalogueEmpty = document.getElementById(
    "catalogue-empty"
);

const searchInput = document.getElementById(
    "search-input"
);

const categoryFilter = document.getElementById(
    "category-filter"
);

const catalogueResultCount = document.getElementById(
    "catalogue-result-count"
);

const materielCount = document.getElementById(
    "materiel-count"
);

const selectionCount = document.getElementById(
    "selection-count"
);

const selectionBadge = document.getElementById(
    "selection-badge"
);

const selectionEmpty = document.getElementById(
    "selection-empty"
);

const selectionList = document.getElementById(
    "selection-list"
);

const selectionSummary = document.getElementById(
    "selection-summary"
);

const summaryTypes = document.getElementById(
    "summary-types"
);

const summaryQuantity = document.getElementById(
    "summary-quantity"
);

const boutonEnvoyerDemande = document.getElementById(
    "submit-request-button"
);

const texteBoutonDemande = document.getElementById(
    "submit-request-text"
);

const spinnerDemande = document.getElementById(
    "submit-request-spinner"
);

const requestMessage = document.getElementById(
    "request-message"
);

const toast = document.getElementById(
    "toast"
);


let materiels = [];

const selection = new Map();

const quantitesChoisies = new Map();


function echapperHtml(valeur) {

    return String(valeur ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function afficherUtilisateur(utilisateur) {

    usernameDisplay.textContent = (
        utilisateur.username
    );

    welcomeUsername.textContent = (
        utilisateur.username
    );

    userInitial.textContent = (
        utilisateur.username
            .charAt(0)
            .toUpperCase()
    );


    if (utilisateur.is_staff) {

        roleDisplay.textContent = (
            "Administrateur"
        );

        adminSection.classList.remove(
            "hidden"
        );

        adminNavLink.classList.remove(
            "hidden"
        );

    } else {

        roleDisplay.textContent = (
            "Utilisateur"
        );

        adminSection.classList.add(
            "hidden"
        );

        adminNavLink.classList.add(
            "hidden"
        );
    }
}


async function chargerUtilisateur() {

    const token = sessionStorage.getItem(
        "access_token"
    );


    if (!token) {

        deconnecterUtilisateur();

        return;
    }


    try {

        const response = await apiFetch(
            "/auth/me/"
        );


        if (!response.ok) {

            deconnecterUtilisateur();

            return;
        }


        const utilisateur = (
            await response.json()
        );


        sessionStorage.setItem(
            "utilisateur",
            JSON.stringify(utilisateur)
        );


        afficherUtilisateur(
            utilisateur
        );


    } catch (erreur) {

        console.error(
            "Impossible de charger l'utilisateur :",
            erreur
        );
    }
}


function initialiserQuantites() {

    for (const materiel of materiels) {

        if (
            !quantitesChoisies.has(
                materiel.id
            )
        ) {

            quantitesChoisies.set(
                materiel.id,
                1
            );
        }
    }
}


function chargerCategories() {

    const categories = [
        ...new Set(
            materiels
                .map(
                    materiel => (
                        materiel.categorie
                        || "Non classé"
                    )
                )
                .filter(Boolean)
        )
    ].sort();


    categoryFilter.innerHTML = `
        <option value="">
            Toutes les catégories
        </option>
    `;


    for (const categorie of categories) {

        const option = document.createElement(
            "option"
        );

        option.value = categorie;

        option.textContent = categorie;

        categoryFilter.appendChild(
            option
        );
    }
}


function obtenirMaterielsFiltres() {

    const recherche = (
        searchInput.value
            .trim()
            .toLowerCase()
    );


    const categorie = (
        categoryFilter.value
    );


    return materiels.filter(
        materiel => {

            const texte = [
                materiel.nom,
                materiel.description,
                materiel.categorie
            ]
                .join(" ")
                .toLowerCase();


            const correspondRecherche = (
                texte.includes(recherche)
            );


            const correspondCategorie = (
                !categorie
                || (
                    materiel.categorie
                    || "Non classé"
                ) === categorie
            );


            return (
                correspondRecherche
                && correspondCategorie
            );
        }
    );
}


function afficherCatalogue() {

    const liste = obtenirMaterielsFiltres();


    materielsGrid.innerHTML = "";


    catalogueResultCount.textContent = (
        `${liste.length} ${
            liste.length > 1
                ? "résultats"
                : "résultat"
        }`
    );


    if (liste.length === 0) {

        catalogueEmpty.classList.remove(
            "hidden"
        );

        return;
    }


    catalogueEmpty.classList.add(
        "hidden"
    );


    for (const materiel of liste) {

        const quantite = (
            quantitesChoisies.get(
                materiel.id
            ) || 1
        );


        const dejaSelectionne = (
            selection.has(
                materiel.id
            )
        );


        const carte = document.createElement(
            "article"
        );


        carte.className = "materiel-card";


        const imageHtml = materiel.photo
            ? `
                <img
                    src="${echapperHtml(materiel.photo)}"
                    alt="${echapperHtml(materiel.nom)}"
                    class="materiel-image"
                >
            `
            : `
                <div class="materiel-image-placeholder">
                    💻
                </div>
            `;


        carte.innerHTML = `

            <div class="materiel-image-container">

                ${imageHtml}

                <span class="stock-badge">
                    ${materiel.quantite_disponible}
                    en stock
                </span>

            </div>


            <div class="materiel-content">

                <span class="materiel-category">
                    ${
                        echapperHtml(
                            materiel.categorie
                            || "Non classé"
                        )
                    }
                </span>


                <h3>
                    ${
                        echapperHtml(
                            materiel.nom
                        )
                    }
                </h3>


                <p class="materiel-description">
                    ${
                        echapperHtml(
                            materiel.description
                            || "Aucune description."
                        )
                    }
                </p>


                <div class="materiel-request-zone">

                    <span class="quantity-label">
                        Quantité
                    </span>


                    <div class="quantity-control">

                        <button
                            type="button"
                            class="quantity-button"
                            data-action="decrease"
                            data-id="${materiel.id}"
                        >
                            −
                        </button>


                        <span class="quantity-value">
                            ${quantite}
                        </span>


                        <button
                            type="button"
                            class="quantity-button"
                            data-action="increase"
                            data-id="${materiel.id}"
                        >
                            +
                        </button>

                    </div>

                </div>


                <button
                    type="button"
                    class="
                        add-request-button
                        ${
                            dejaSelectionne
                                ? "selected"
                                : ""
                        }
                    "
                    data-action="add"
                    data-id="${materiel.id}"
                >

                    ${
                        dejaSelectionne
                            ? "✓ Dans la demande"
                            : "Ajouter à la demande"
                    }

                </button>

            </div>
        `;


        materielsGrid.appendChild(
            carte
        );
    }
}


function changerQuantite(
    idMateriel,
    variation
) {

    const materiel = materiels.find(
        element => (
            element.id === idMateriel
        )
    );


    if (!materiel) {
        return;
    }


    let quantite = (
        quantitesChoisies.get(
            idMateriel
        ) || 1
    );


    quantite += variation;


    if (quantite < 1) {
        quantite = 1;
    }


    if (
        quantite
        > materiel.quantite_disponible
    ) {

        quantite = (
            materiel.quantite_disponible
        );


        afficherToast(
            "Vous ne pouvez pas demander plus que le stock disponible.",
            "error"
        );
    }


    quantitesChoisies.set(
        idMateriel,
        quantite
    );


    afficherCatalogue();
}


function ajouterSelection(
    idMateriel
) {

    const materiel = materiels.find(
        element => (
            element.id === idMateriel
        )
    );


    if (!materiel) {
        return;
    }


    const quantite = (
        quantitesChoisies.get(
            idMateriel
        ) || 1
    );


    selection.set(
        idMateriel,
        {
            materiel,
            quantite
        }
    );


    mettreAJourSelection();

    afficherCatalogue();


    afficherToast(
        `${materiel.nom} ajouté à la demande.`,
        "success"
    );
}


function supprimerSelection(
    idMateriel
) {

    selection.delete(
        idMateriel
    );


    mettreAJourSelection();

    afficherCatalogue();
}


function modifierQuantiteSelection(
    idMateriel,
    variation
) {

    const element = selection.get(
        idMateriel
    );


    if (!element) {
        return;
    }


    let nouvelleQuantite = (
        element.quantite
        + variation
    );


    if (nouvelleQuantite < 1) {

        supprimerSelection(
            idMateriel
        );

        return;
    }


    if (
        nouvelleQuantite
        > element.materiel.quantite_disponible
    ) {

        nouvelleQuantite = (
            element.materiel
                .quantite_disponible
        );


        afficherToast(
            "Stock maximum atteint.",
            "error"
        );
    }


    element.quantite = nouvelleQuantite;


    selection.set(
        idMateriel,
        element
    );


    quantitesChoisies.set(
        idMateriel,
        nouvelleQuantite
    );


    mettreAJourSelection();

    afficherCatalogue();
}


function mettreAJourSelection() {

    const elements = [
        ...selection.values()
    ];


    selectionList.innerHTML = "";


    const nombreTypes = (
        elements.length
    );


    const quantiteTotale = (
        elements.reduce(
            (
                total,
                element
            ) => (
                total
                + element.quantite
            ),
            0
        )
    );


    selectionCount.textContent = (
        quantiteTotale
    );

    selectionBadge.textContent = (
        nombreTypes
    );

    summaryTypes.textContent = (
        nombreTypes
    );

    summaryQuantity.textContent = (
        quantiteTotale
    );


    if (nombreTypes === 0) {

        selectionEmpty.classList.remove(
            "hidden"
        );

        selectionSummary.classList.add(
            "hidden"
        );

        return;
    }


    selectionEmpty.classList.add(
        "hidden"
    );

    selectionSummary.classList.remove(
        "hidden"
    );


    for (const element of elements) {

        const item = document.createElement(
            "div"
        );


        item.className = "selection-item";


        const imageHtml = (
            element.materiel.photo
                ? `
                    <img
                        src="${
                            echapperHtml(
                                element.materiel.photo
                            )
                        }"
                        alt="${
                            echapperHtml(
                                element.materiel.nom
                            )
                        }"
                    >
                `
                : `
                    <div class="selection-image-placeholder">
                        💻
                    </div>
                `
        );


        item.innerHTML = `

            <div class="selection-item-top">

                <div class="selection-item-image">
                    ${imageHtml}
                </div>


                <div class="selection-item-info">

                    <strong>
                        ${
                            echapperHtml(
                                element.materiel.nom
                            )
                        }
                    </strong>

                    <span>
                        ${
                            echapperHtml(
                                element.materiel.categorie
                                || "Non classé"
                            )
                        }
                    </span>

                </div>


                <button
                    type="button"
                    class="remove-selection-button"
                    data-selection-action="remove"
                    data-id="${element.materiel.id}"
                    aria-label="Retirer"
                >
                    ×
                </button>

            </div>


            <div class="selection-item-bottom">

                <span>
                    Quantité demandée
                </span>


                <div class="quantity-control small">

                    <button
                        type="button"
                        class="quantity-button"
                        data-selection-action="decrease"
                        data-id="${element.materiel.id}"
                    >
                        −
                    </button>


                    <span class="quantity-value">
                        ${element.quantite}
                    </span>


                    <button
                        type="button"
                        class="quantity-button"
                        data-selection-action="increase"
                        data-id="${element.materiel.id}"
                    >
                        +
                    </button>

                </div>

            </div>
        `;


        selectionList.appendChild(
            item
        );
    }
}


function definirChargementDemande(
    enChargement
) {

    boutonEnvoyerDemande.disabled = (
        enChargement
    );


    if (enChargement) {

        texteBoutonDemande.textContent = (
            "Envoi en cours..."
        );

        spinnerDemande.classList.remove(
            "hidden"
        );

    } else {

        texteBoutonDemande.textContent = (
            "Envoyer la demande"
        );

        spinnerDemande.classList.add(
            "hidden"
        );
    }
}


function afficherMessageDemande(
    texte,
    type
) {

    requestMessage.textContent = texte;

    requestMessage.className = (
        `message message-${type}`
    );
}


function cacherMessageDemande() {

    requestMessage.className = (
        "message hidden"
    );
}


async function envoyerDemande() {

    if (selection.size === 0) {

        afficherMessageDemande(
            "Ajoutez au moins un matériel à votre demande.",
            "error"
        );

        return;
    }


    cacherMessageDemande();

    definirChargementDemande(
        true
    );


    const materielsDemandes = (
        [...selection.values()]
            .map(
                element => ({
                    materiel_id:
                        element.materiel.id,

                    quantite:
                        element.quantite
                })
            )
    );


    try {

        const response = await apiFetch(
            "/demandes/",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    materiels:
                        materielsDemandes
                })
            }
        );


        const donnees = (
            await response.json()
        );


        if (!response.ok) {

            const messageErreur = (
                donnees.erreur
                || donnees.detail
                || "Impossible d'envoyer la demande."
            );


            afficherMessageDemande(
                messageErreur,
                "error"
            );

            return;
        }


        selection.clear();

        mettreAJourSelection();

        afficherCatalogue();


        afficherMessageDemande(
            `Demande #${donnees.id} envoyée avec succès.`,
            "success"
        );


        afficherToast(
            "Votre demande a bien été envoyée.",
            "success"
        );


    } catch (erreur) {

        console.error(
            "Erreur lors de la création de la demande :",
            erreur
        );


        afficherMessageDemande(
            "Le serveur est inaccessible.",
            "error"
        );


    } finally {

        definirChargementDemande(
            false
        );
    }
}


async function chargerMateriels() {

    catalogueLoading.classList.remove(
        "hidden"
    );


    materielsGrid.innerHTML = "";


    try {

        const response = await apiFetch(
            "/materiels/"
        );


        if (!response.ok) {

            throw new Error(
                "Impossible de récupérer les matériels."
            );
        }


        materiels = (
            await response.json()
        );


        initialiserQuantites();

        chargerCategories();

        afficherCatalogue();


        materielCount.textContent = (
            materiels.length
        );


    } catch (erreur) {

        console.error(
            "Erreur de chargement des matériels :",
            erreur
        );


        catalogueEmpty.classList.remove(
            "hidden"
        );


        catalogueEmpty.querySelector(
            "h3"
        ).textContent = (
            "Impossible de charger les matériels"
        );


        catalogueEmpty.querySelector(
            "p"
        ).textContent = (
            "Vérifiez que le serveur Backend est bien démarré."
        );


    } finally {

        catalogueLoading.classList.add(
            "hidden"
        );
    }
}


function afficherToast(
    texte,
    type
) {

    toast.textContent = texte;

    toast.className = (
        `toast toast-${type}`
    );


    setTimeout(
        function () {

            toast.classList.add(
                "toast-visible"
            );

        },
        20
    );


    setTimeout(
        function () {

            toast.classList.remove(
                "toast-visible"
            );


            setTimeout(
                function () {

                    toast.className = (
                        "toast hidden"
                    );

                },
                300
            );

        },
        3000
    );
}


materielsGrid.addEventListener(
    "click",
    function (event) {

        const bouton = event.target.closest(
            "button[data-action]"
        );


        if (!bouton) {
            return;
        }


        const idMateriel = Number(
            bouton.dataset.id
        );


        const action = (
            bouton.dataset.action
        );


        if (action === "increase") {

            changerQuantite(
                idMateriel,
                1
            );
        }


        if (action === "decrease") {

            changerQuantite(
                idMateriel,
                -1
            );
        }


        if (action === "add") {

            ajouterSelection(
                idMateriel
            );
        }
    }
);


selectionList.addEventListener(
    "click",
    function (event) {

        const bouton = event.target.closest(
            "button[data-selection-action]"
        );


        if (!bouton) {
            return;
        }


        const idMateriel = Number(
            bouton.dataset.id
        );


        const action = (
            bouton.dataset.selectionAction
        );


        if (action === "remove") {

            supprimerSelection(
                idMateriel
            );
        }


        if (action === "increase") {

            modifierQuantiteSelection(
                idMateriel,
                1
            );
        }


        if (action === "decrease") {

            modifierQuantiteSelection(
                idMateriel,
                -1
            );
        }
    }
);


searchInput.addEventListener(
    "input",
    afficherCatalogue
);


categoryFilter.addEventListener(
    "change",
    afficherCatalogue
);


boutonEnvoyerDemande.addEventListener(
    "click",
    envoyerDemande
);


boutonDeconnexion.addEventListener(
    "click",
    function () {

        deconnecterUtilisateur();
    }
);


async function initialiserDashboard() {

    await chargerUtilisateur();

    await chargerMateriels();

    mettreAJourSelection();
}


initialiserDashboard();