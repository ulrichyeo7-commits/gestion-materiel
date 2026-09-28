const usernameDisplay = document.getElementById(
    "username-display"
);

const roleDisplay = document.getElementById(
    "role-display"
);

const userInitial = document.getElementById(
    "user-initial"
);

const boutonDeconnexion = document.getElementById(
    "logout-button"
);

const demandesLoading = document.getElementById(
    "demandes-loading"
);

const demandesEmpty = document.getElementById(
    "demandes-empty"
);

const demandesList = document.getElementById(
    "demandes-list"
);

const demandesResultCount = document.getElementById(
    "demandes-result-count"
);

const statusFilters = document.getElementById(
    "status-filters"
);

const statTotal = document.getElementById(
    "stat-total"
);

const statPending = document.getElementById(
    "stat-pending"
);

const statAccepted = document.getElementById(
    "stat-accepted"
);

const statRefused = document.getElementById(
    "stat-refused"
);

const emptyIcon = demandesEmpty.querySelector(
    ".demandes-empty-icon"
);

const emptyTitle = demandesEmpty.querySelector(
    "h3"
);

const emptyText = demandesEmpty.querySelector(
    "p"
);

const emptyAction = demandesEmpty.querySelector(
    ".empty-action"
);


const DELAI_REQUETE = 15000;

let demandes = [];

let statutActif = "";

let chargementReussi = false;

let initialisationEnCours = false;


function echapperHtml(valeur) {

    return String(valeur ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formaterDate(dateTexte) {

    if (!dateTexte) {
        return "Non traitée";
    }


    const date = new Date(dateTexte);


    if (Number.isNaN(date.getTime())) {
        return "Date indisponible";
    }


    return new Intl.DateTimeFormat(
        "fr-FR",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    ).format(date);
}


function obtenirInfosStatut(statut) {

    const statuts = {
        EN_ATTENTE: {
            label: "En attente",
            classe: "status-pending",
            icone: "◷"
        },

        ACCEPTEE: {
            label: "Acceptée",
            classe: "status-accepted",
            icone: "✓"
        },

        REFUSEE: {
            label: "Refusée",
            classe: "status-refused",
            icone: "×"
        }
    };


    return (
        statuts[statut]
        || {
            label: statut || "Inconnu",
            classe: "",
            icone: "?"
        }
    );
}


async function apiFetchAvecDelai(
    endpoint,
    options = {}
) {

    const controleur = new AbortController();

    const minuteur = setTimeout(
        function () {
            controleur.abort();
        },
        DELAI_REQUETE
    );


    try {

        return await apiFetch(
            endpoint,
            {
                ...options,
                signal: controleur.signal
            }
        );

    } finally {

        clearTimeout(minuteur);
    }
}


function afficherUtilisateur(utilisateur) {

    const username = (
        utilisateur.username
        || "Utilisateur"
    );


    usernameDisplay.textContent = username;

    userInitial.textContent = (
        username.charAt(0).toUpperCase()
        || "U"
    );

    roleDisplay.textContent = (
        utilisateur.is_staff
            ? "Administrateur"
            : "Utilisateur"
    );
}


async function chargerUtilisateur() {

    const token = sessionStorage.getItem(
        "access_token"
    );


    if (!token) {
        deconnecterUtilisateur();
        return false;
    }


    try {

        const response = await apiFetchAvecDelai(
            "/auth/me/"
        );


        if (!response.ok) {
            deconnecterUtilisateur();
            return false;
        }


        const utilisateur = await response.json();


        sessionStorage.setItem(
            "utilisateur",
            JSON.stringify(utilisateur)
        );


        afficherUtilisateur(utilisateur);

        return true;

    } catch (erreur) {

        console.error(
            "Impossible de charger l'utilisateur :",
            erreur
        );

        return false;
    }
}


function mettreAJourStatistiques() {

    statTotal.textContent = demandes.length;

    statPending.textContent = demandes.filter(
        demande => demande.statut === "EN_ATTENTE"
    ).length;

    statAccepted.textContent = demandes.filter(
        demande => demande.statut === "ACCEPTEE"
    ).length;

    statRefused.textContent = demandes.filter(
        demande => demande.statut === "REFUSEE"
    ).length;
}


function obtenirDemandesFiltrees() {

    if (!statutActif) {
        return demandes;
    }


    return demandes.filter(
        demande => demande.statut === statutActif
    );
}


function afficherEtatVideFiltre() {

    emptyIcon.textContent = "🔎";

    emptyTitle.textContent = (
        "Aucune demande correspondante"
    );

    emptyText.textContent = (
        "Aucune de vos demandes ne correspond à ce statut."
    );

    emptyAction.classList.add("hidden");

    demandesEmpty.classList.remove("hidden");
}


function afficherEtatVideInitial() {

    emptyIcon.textContent = "📭";

    emptyTitle.textContent = "Aucune demande";

    emptyText.textContent = (
        "Vous n'avez encore effectué aucune demande de matériel."
    );

    emptyAction.textContent = "Consulter le catalogue";

    emptyAction.href = "dashboard.html";

    delete emptyAction.dataset.action;

    emptyAction.classList.remove("hidden");

    demandesEmpty.classList.remove("hidden");
}


function afficherErreurChargement(message) {

    chargementReussi = false;

    demandes = [];

    demandesList.innerHTML = "";

    demandesResultCount.textContent = "0 demande";

    mettreAJourStatistiques();

    emptyIcon.textContent = "⚠";

    emptyTitle.textContent = (
        "Impossible de charger vos demandes"
    );

    emptyText.textContent = message;

    emptyAction.textContent = "Réessayer";

    emptyAction.href = "#";

    emptyAction.dataset.action = "retry";

    emptyAction.classList.remove("hidden");

    demandesEmpty.classList.remove("hidden");
}


function creerMaterielHtml(ligne) {

    const materiel = ligne.materiel || {};

    const imageHtml = materiel.photo
        ? `
            <img
                src="${echapperHtml(materiel.photo)}"
                alt="${echapperHtml(materiel.nom)}"
            >
        `
        : `
            <div class="request-material-placeholder">
                💻
            </div>
        `;


    return `
        <div class="request-material">

            <div class="request-material-image">
                ${imageHtml}
            </div>

            <div class="request-material-info">

                <strong>
                    ${echapperHtml(materiel.nom || "Matériel")}
                </strong>

                <span>
                    ${echapperHtml(materiel.categorie || "Non classé")}
                </span>

            </div>

            <div class="request-material-quantity">

                <span>Quantité</span>

                <strong>
                    ${echapperHtml(ligne.quantite)}
                </strong>

            </div>

        </div>
    `;
}


function afficherDemandes() {

    const liste = obtenirDemandesFiltrees();


    demandesList.innerHTML = "";

    demandesEmpty.classList.add("hidden");

    demandesResultCount.textContent = (
        `${liste.length} ${
            liste.length > 1
                ? "demandes"
                : "demande"
        }`
    );


    if (liste.length === 0) {

        if (demandes.length === 0) {
            afficherEtatVideInitial();
        } else {
            afficherEtatVideFiltre();
        }

        return;
    }


    for (const demande of liste) {

        const statut = obtenirInfosStatut(
            demande.statut
        );

        const lignes = Array.isArray(demande.lignes)
            ? demande.lignes
            : [];

        const quantiteTotale = lignes.reduce(
            function (total, ligne) {

                const quantite = Number(
                    ligne.quantite
                );

                return (
                    total
                    + (
                        Number.isFinite(quantite)
                            ? quantite
                            : 0
                    )
                );
            },
            0
        );

        const lignesHtml = lignes
            .map(creerMaterielHtml)
            .join("");

        const dateTraitement = (
            demande.date_traitement
                ? formaterDate(
                    demande.date_traitement
                )
                : "En attente"
        );

        const carte = document.createElement(
            "article"
        );


        carte.className = "demande-card";

        carte.innerHTML = `
            <div class="demande-card-header">

                <div class="demande-identity">

                    <span class="demande-number">
                        Demande #${echapperHtml(demande.id)}
                    </span>

                    <span class="demande-date">
                        Envoyée le
                        ${echapperHtml(formaterDate(demande.date_demande))}
                    </span>

                </div>

                <span class="request-status ${statut.classe}">
                    ${statut.icone}
                    ${echapperHtml(statut.label)}
                </span>

            </div>

            <div class="demande-summary">

                <div>
                    <span>Types de matériels</span>
                    <strong>${lignes.length}</strong>
                </div>

                <div>
                    <span>Quantité totale</span>
                    <strong>${quantiteTotale}</strong>
                </div>

                <div>
                    <span>Traitement</span>
                    <strong class="date-value">
                        ${echapperHtml(dateTraitement)}
                    </strong>
                </div>

            </div>

            <button
                type="button"
                class="details-toggle"
                aria-expanded="false"
            >
                <span class="details-label">
                    Voir les détails
                </span>

                <span class="details-arrow">
                    ▾
                </span>
            </button>

            <div class="demande-details hidden">

                <div class="request-materials-title">
                    <strong>Matériels demandés</strong>
                    <span>
                        ${lignes.length} ${
                            lignes.length > 1
                                ? "articles"
                                : "article"
                        }
                    </span>
                </div>

                <div class="request-materials-list">
                    ${lignesHtml}
                </div>

            </div>
        `;


        demandesList.appendChild(carte);
    }
}


async function chargerDemandes() {

    const response = await apiFetchAvecDelai(
        "/demandes/"
    );


    if (!response.ok) {
        throw new Error(
            "Impossible de récupérer les demandes."
        );
    }


    const donnees = await response.json();


    if (!Array.isArray(donnees)) {
        throw new Error(
            "Le format de la réponse est invalide."
        );
    }


    demandes = donnees;

    chargementReussi = true;

    mettreAJourStatistiques();

    afficherDemandes();
}


function afficherChargement() {

    chargementReussi = false;

    demandesList.innerHTML = "";

    demandesEmpty.classList.add("hidden");

    demandesLoading.classList.remove("hidden");

    demandesResultCount.textContent = "Chargement...";
}


async function initialiserPage() {

    if (initialisationEnCours) {
        return;
    }


    initialisationEnCours = true;

    afficherChargement();


    try {

        const utilisateurCharge = (
            await chargerUtilisateur()
        );


        if (!utilisateurCharge) {

            if (
                sessionStorage.getItem(
                    "access_token"
                )
            ) {
                afficherErreurChargement(
                    "Le serveur est inaccessible. Vérifiez qu'il est démarré, puis réessayez."
                );
            }

            return;
        }


        await chargerDemandes();

    } catch (erreur) {

        console.error(
            "Erreur de chargement des demandes :",
            erreur
        );

        afficherErreurChargement(
            "Le serveur est inaccessible ou a renvoyé une réponse invalide. Réessayez dans un instant."
        );

    } finally {

        demandesLoading.classList.add("hidden");

        initialisationEnCours = false;
    }
}


statusFilters.addEventListener(
    "click",
    function (event) {

        const bouton = event.target.closest(
            "button[data-status]"
        );


        if (!bouton || !chargementReussi) {
            return;
        }


        statutActif = bouton.dataset.status;


        for (
            const filtre
            of statusFilters.querySelectorAll(
                "button[data-status]"
            )
        ) {
            filtre.classList.toggle(
                "active",
                filtre === bouton
            );
        }


        afficherDemandes();
    }
);


demandesList.addEventListener(
    "click",
    function (event) {

        const bouton = event.target.closest(
            ".details-toggle"
        );


        if (!bouton) {
            return;
        }


        const carte = bouton.closest(
            ".demande-card"
        );

        const details = carte.querySelector(
            ".demande-details"
        );

        const detailsOuverts = (
            details.classList.contains("hidden")
        );


        details.classList.toggle(
            "hidden",
            !detailsOuverts
        );

        bouton.setAttribute(
            "aria-expanded",
            String(detailsOuverts)
        );

        bouton.querySelector(
            ".details-label"
        ).textContent = detailsOuverts
            ? "Masquer les détails"
            : "Voir les détails";

        bouton.querySelector(
            ".details-arrow"
        ).textContent = detailsOuverts
            ? "▴"
            : "▾";
    }
);


emptyAction.addEventListener(
    "click",
    function (event) {

        if (emptyAction.dataset.action !== "retry") {
            return;
        }


        event.preventDefault();

        initialiserPage();
    }
);


boutonDeconnexion.addEventListener(
    "click",
    function () {
        deconnecterUtilisateur();
    }
);


initialiserPage();
