const usernameDisplay = document.getElementById(
    "username-display"
);

const userInitial = document.getElementById(
    "user-initial"
);

const boutonDeconnexion = document.getElementById(
    "logout-button"
);

const tabs = document.querySelectorAll(
    ".admin-tab"
);

const demandesSection = document.getElementById(
    "demandes-section"
);

const materielsSection = document.getElementById(
    "materiels-section"
);

const demandesList = document.getElementById(
    "admin-demandes-list"
);

const demandesLoading = document.getElementById(
    "admin-demandes-loading"
);

const demandesEmpty = document.getElementById(
    "admin-demandes-empty"
);

const demandesCount = document.getElementById(
    "admin-demandes-count"
);

const statusFilter = document.getElementById(
    "admin-status-filter"
);

const materielsList = document.getElementById(
    "admin-materiels-list"
);

const materielsLoading = document.getElementById(
    "admin-materiels-loading"
);

const materielsCount = document.getElementById(
    "admin-materiels-count"
);

const statPending = document.getElementById(
    "admin-stat-pending"
);

const statAccepted = document.getElementById(
    "admin-stat-accepted"
);

const statRefused = document.getElementById(
    "admin-stat-refused"
);

const statMaterials = document.getElementById(
    "admin-stat-materials"
);

const formulaireMateriel = document.getElementById(
    "material-form"
);

const materialFormPanel = document.querySelector(
    ".admin-material-form-panel"
);

const materialFormKicker = document.getElementById(
    "material-form-kicker"
);

const materialFormTitle = document.getElementById(
    "material-form-title"
);

const materialFormDescription = document.getElementById(
    "material-form-description"
);

const materialName = document.getElementById(
    "material-name"
);

const materialCategory = document.getElementById(
    "material-category"
);

const materialDescription = document.getElementById(
    "material-description"
);

const materialStock = document.getElementById(
    "material-stock"
);

const materialPhoto = document.getElementById(
    "material-photo"
);

const photoPreviewContainer = document.getElementById(
    "photo-preview-container"
);

const photoPreview = document.getElementById(
    "photo-preview"
);

const boutonAjoutMateriel = document.getElementById(
    "material-submit-button"
);

const texteAjoutMateriel = document.getElementById(
    "material-submit-text"
);

const spinnerAjoutMateriel = document.getElementById(
    "material-submit-spinner"
);

const boutonAnnulerMateriel = document.getElementById(
    "material-cancel-button"
);

const materialFormMessage = document.getElementById(
    "material-form-message"
);

const toast = document.getElementById(
    "admin-toast"
);


let demandes = [];

let materiels = [];

let materielEnEditionId = null;

let photoMaterielActuelle = "";


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

    const date = new Date(
        dateTexte
    );

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
            classe: "admin-status-pending",
            icone: "◷"
        },

        ACCEPTEE: {
            label: "Acceptée",
            classe: "admin-status-accepted",
            icone: "✓"
        },

        REFUSEE: {
            label: "Refusée",
            classe: "admin-status-refused",
            icone: "×"
        }

    };


    return (
        statuts[statut]
        || {
            label: statut,
            classe: "",
            icone: "?"
        }
    );
}


async function verifierAdministrateur() {

    const token = sessionStorage.getItem(
        "access_token"
    );


    if (!token) {
        deconnecterUtilisateur();
        return false;
    }


    try {

        const response = await apiFetch(
            "/auth/me/"
        );


        if (!response.ok) {

            deconnecterUtilisateur();

            return false;
        }


        const utilisateur = await response.json();


        if (!utilisateur.is_staff) {

            window.location.href = "dashboard.html";

            return false;
        }


        usernameDisplay.textContent = (
            utilisateur.username
        );


        userInitial.textContent = (
            utilisateur.username
                .charAt(0)
                .toUpperCase()
        );


        return true;


    } catch (erreur) {

        console.error(
            "Impossible de vérifier l'administrateur :",
            erreur
        );


        return false;
    }
}


function mettreAJourStatistiques() {

    statPending.textContent = (
        demandes.filter(
            demande => (
                demande.statut
                === "EN_ATTENTE"
            )
        ).length
    );


    statAccepted.textContent = (
        demandes.filter(
            demande => (
                demande.statut
                === "ACCEPTEE"
            )
        ).length
    );


    statRefused.textContent = (
        demandes.filter(
            demande => (
                demande.statut
                === "REFUSEE"
            )
        ).length
    );


    statMaterials.textContent = (
        materiels.length
    );
}


function obtenirDemandesFiltrees() {

    const statut = statusFilter.value;


    if (!statut) {
        return demandes;
    }


    return demandes.filter(
        demande => (
            demande.statut === statut
        )
    );
}


function creerLigneMaterielHtml(
    ligne
) {

    const materiel = ligne.materiel;


    const imageHtml = (
        materiel.photo
            ? `
                <img
                    src="${
                        echapperHtml(
                            materiel.photo
                        )
                    }"
                    alt="${
                        echapperHtml(
                            materiel.nom
                        )
                    }"
                >
            `
            : `
                <div class="admin-line-placeholder">
                    💻
                </div>
            `
    );


    return `
        <div class="admin-request-line">

            <div class="admin-request-line-image">
                ${imageHtml}
            </div>


            <div class="admin-request-line-info">

                <strong>
                    ${
                        echapperHtml(
                            materiel.nom
                        )
                    }
                </strong>

                <span>
                    ${
                        echapperHtml(
                            materiel.categorie
                            || "Non classé"
                        )
                    }
                </span>

            </div>


            <div class="admin-request-line-stock">

                <span>
                    Demandé
                </span>

                <strong>
                    ${ligne.quantite}
                </strong>

            </div>


            <div class="admin-request-line-stock">

                <span>
                    Stock
                </span>

                <strong>
                    ${materiel.quantite_disponible}
                </strong>

            </div>

        </div>
    `;
}


function afficherDemandes() {

    const liste = obtenirDemandesFiltrees();


    demandesList.innerHTML = "";


    demandesCount.textContent = (
        `${liste.length} ${
            liste.length > 1
                ? "demandes"
                : "demande"
        }`
    );


    if (liste.length === 0) {

        demandesEmpty.classList.remove(
            "hidden"
        );

        return;
    }


    demandesEmpty.classList.add(
        "hidden"
    );


    for (const demande of liste) {

        const statut = obtenirInfosStatut(
            demande.statut
        );


        const quantiteTotale = (
            demande.lignes.reduce(
                (
                    total,
                    ligne
                ) => (
                    total
                    + ligne.quantite
                ),
                0
            )
        );


        const lignesHtml = (
            demande.lignes
                .map(
                    creerLigneMaterielHtml
                )
                .join("")
        );


        const actionsHtml = (
            demande.statut === "EN_ATTENTE"
                ? `
                    <div class="admin-request-actions">

                        <button
                            type="button"
                            class="admin-action-button refuse"
                            data-action="REFUSER"
                            data-id="${demande.id}"
                        >
                            Refuser
                        </button>

                        <button
                            type="button"
                            class="admin-action-button accept"
                            data-action="ACCEPTER"
                            data-id="${demande.id}"
                        >
                            Accepter
                        </button>

                    </div>
                `
                : `
                    <div class="admin-request-treated">

                        Demande traitée le
                        ${
                            echapperHtml(
                                formaterDate(
                                    demande.date_traitement
                                )
                            )
                        }

                    </div>
                `
        );


        const carte = document.createElement(
            "article"
        );


        carte.className = "admin-request-card";


        carte.innerHTML = `

            <div class="admin-request-header">

                <div class="admin-request-user">

                    <div class="admin-request-avatar">
                        ${
                            echapperHtml(
                                demande.utilisateur
                                    .charAt(0)
                                    .toUpperCase()
                            )
                        }
                    </div>


                    <div>

                        <span class="admin-request-number">
                            Demande #${demande.id}
                        </span>

                        <strong>
                            ${
                                echapperHtml(
                                    demande.utilisateur
                                )
                            }
                        </strong>

                        <small>
                            ${
                                echapperHtml(
                                    formaterDate(
                                        demande.date_demande
                                    )
                                )
                            }
                        </small>

                    </div>

                </div>


                <span
                    class="
                        admin-status
                        ${statut.classe}
                    "
                >
                    ${statut.icone}
                    ${statut.label}
                </span>

            </div>


            <div class="admin-request-meta">

                <div>

                    <span>
                        Types de matériels
                    </span>

                    <strong>
                        ${demande.lignes.length}
                    </strong>

                </div>


                <div>

                    <span>
                        Quantité totale
                    </span>

                    <strong>
                        ${quantiteTotale}
                    </strong>

                </div>

            </div>


            <div class="admin-request-lines">

                ${lignesHtml}

            </div>


            ${actionsHtml}
        `;


        demandesList.appendChild(
            carte
        );
    }
}


async function chargerDemandes() {

    demandesLoading.classList.remove(
        "hidden"
    );


    try {

        const response = await apiFetch(
            "/admin/demandes/"
        );


        if (!response.ok) {

            throw new Error(
                "Impossible de charger les demandes."
            );
        }


        demandes = await response.json();


        afficherDemandes();

        mettreAJourStatistiques();


    } catch (erreur) {

        console.error(
            "Erreur demandes admin :",
            erreur
        );


        afficherToast(
            "Impossible de charger les demandes.",
            "error"
        );


    } finally {

        demandesLoading.classList.add(
            "hidden"
        );
    }
}


async function traiterDemande(
    idDemande,
    action
) {

    const verbe = (
        action === "ACCEPTER"
            ? "accepter"
            : "refuser"
    );


    const confirmation = window.confirm(
        `Voulez-vous vraiment ${verbe} la demande #${idDemande} ?`
    );


    if (!confirmation) {
        return;
    }


    try {

        const response = await apiFetch(
            `/admin/demandes/${idDemande}/`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    action
                })
            }
        );


        const donnees = await response.json();


        if (!response.ok) {

            afficherToast(
                donnees.erreur
                || "Impossible de traiter la demande.",
                "error"
            );

            return;
        }


        afficherToast(
            action === "ACCEPTER"
                ? "Demande acceptée avec succès."
                : "Demande refusée.",
            "success"
        );


        await chargerDemandes();

        await chargerMateriels();


    } catch (erreur) {

        console.error(
            "Erreur de traitement :",
            erreur
        );


        afficherToast(
            "Le serveur est inaccessible.",
            "error"
        );
    }
}


function creerMaterielHtml(
    materiel
) {

    const imageHtml = (
        materiel.photo
            ? `
                <img
                    src="${
                        echapperHtml(
                            materiel.photo
                        )
                    }"
                    alt="${
                        echapperHtml(
                            materiel.nom
                        )
                    }"
                >
            `
            : `
                <div class="admin-material-placeholder">
                    💻
                </div>
            `
    );


    const enEdition = (
        materiel.id === materielEnEditionId
    );


    return `
        <article
            class="admin-material-card ${
                enEdition
                    ? "editing"
                    : ""
            }"
        >

            <div class="admin-material-image">
                ${imageHtml}
            </div>


            <div class="admin-material-info">

                <span>
                    ${
                        echapperHtml(
                            materiel.categorie
                            || "Non classé"
                        )
                    }
                </span>

                <strong>
                    ${
                        echapperHtml(
                            materiel.nom
                        )
                    }
                </strong>

                <small>
                    ${
                        materiel.quantite_disponible
                    }
                    disponible(s)
                </small>

            </div>


            <button
                type="button"
                class="admin-material-edit-button"
                data-material-action="edit"
                data-id="${materiel.id}"
                aria-label="Modifier ${
                    echapperHtml(
                        materiel.nom
                    )
                }"
                title="Modifier ce matériel"
            >
                ✎
            </button>

        </article>
    `;
}


function afficherMateriels() {

    materielsList.innerHTML = (
        materiels
            .map(
                creerMaterielHtml
            )
            .join("")
    );


    materielsCount.textContent = (
        `${materiels.length} ${
            materiels.length > 1
                ? "matériels"
                : "matériel"
        }`
    );


    statMaterials.textContent = (
        materiels.length
    );
}


async function chargerMateriels() {

    materielsLoading.classList.remove(
        "hidden"
    );


    try {

        const response = await apiFetch(
            "/admin/materiels/"
        );


        if (!response.ok) {

            throw new Error(
                "Impossible de charger les matériels."
            );
        }


        materiels = await response.json();


        afficherMateriels();

        mettreAJourStatistiques();


    } catch (erreur) {

        console.error(
            "Erreur matériels admin :",
            erreur
        );


        afficherToast(
            "Impossible de charger les matériels.",
            "error"
        );


    } finally {

        materielsLoading.classList.add(
            "hidden"
        );
    }
}


function definirChargementMateriel(
    chargement
) {

    boutonAjoutMateriel.disabled = chargement;

    boutonAnnulerMateriel.disabled = chargement;


    if (chargement) {

        texteAjoutMateriel.textContent = (
            materielEnEditionId === null
                ? "Ajout en cours..."
                : "Modification en cours..."
        );

        spinnerAjoutMateriel.classList.remove(
            "hidden"
        );

    } else {

        texteAjoutMateriel.textContent = (
            materielEnEditionId === null
                ? "Ajouter le matériel"
                : "Enregistrer les modifications"
        );

        spinnerAjoutMateriel.classList.add(
            "hidden"
        );
    }
}


function mettreAJourApercuPhoto(url) {

    if (!url) {

        photoPreview.removeAttribute("src");

        photoPreviewContainer.classList.add(
            "hidden"
        );

        return;
    }


    photoPreview.src = url;

    photoPreviewContainer.classList.remove(
        "hidden"
    );
}


function cacherMessageFormulaire() {

    materialFormMessage.textContent = "";

    materialFormMessage.className = (
        "message hidden"
    );
}


function reinitialiserFormulaireMateriel(
    masquerMessage = true
) {

    materielEnEditionId = null;

    photoMaterielActuelle = "";

    formulaireMateriel.reset();

    mettreAJourApercuPhoto("");

    materialFormKicker.textContent = (
        "NOUVEAU MATÉRIEL"
    );

    materialFormTitle.textContent = (
        "Ajouter un équipement"
    );

    materialFormDescription.textContent = (
        "Renseignez les informations du matériel à ajouter au catalogue."
    );

    texteAjoutMateriel.textContent = (
        "Ajouter le matériel"
    );

    boutonAnnulerMateriel.classList.add(
        "hidden"
    );


    if (masquerMessage) {
        cacherMessageFormulaire();
    }


    afficherMateriels();
}


function commencerEditionMateriel(idMateriel) {

    const materiel = materiels.find(
        element => element.id === idMateriel
    );


    if (!materiel) {

        afficherToast(
            "Ce matériel est introuvable.",
            "error"
        );

        return;
    }


    materielEnEditionId = materiel.id;

    photoMaterielActuelle = (
        materiel.photo
        || ""
    );

    materialName.value = materiel.nom || "";

    materialCategory.value = (
        materiel.categorie
        || ""
    );

    materialDescription.value = (
        materiel.description
        || ""
    );

    materialStock.value = (
        materiel.quantite_disponible
    );

    materialPhoto.value = "";

    mettreAJourApercuPhoto(
        photoMaterielActuelle
    );

    materialFormKicker.textContent = (
        "MODIFICATION"
    );

    materialFormTitle.textContent = (
        "Modifier l'équipement"
    );

    materialFormDescription.textContent = (
        "Mettez à jour les caractéristiques du matériel sélectionné."
    );

    texteAjoutMateriel.textContent = (
        "Enregistrer les modifications"
    );

    boutonAnnulerMateriel.classList.remove(
        "hidden"
    );

    cacherMessageFormulaire();

    afficherMateriels();

    materialFormPanel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

    materialName.focus({
        preventScroll: true
    });
}


function afficherMessageFormulaire(
    texte,
    type
) {

    materialFormMessage.textContent = texte;

    materialFormMessage.className = (
        `message message-${type}`
    );
}


function obtenirMessageErreurMateriel(
    response,
    donnees,
    estModification
) {

    if (
        estModification
        && response.status === 404
    ) {
        return (
            "Le service de modification est introuvable. "
            + "Redémarrez le serveur Backend avec la version actuelle du projet."
        );
    }


    if (response.status === 403) {
        return (
            "Vous n'avez pas l'autorisation de modifier ce matériel."
        );
    }


    if (response.status === 413) {
        return (
            "La photo sélectionnée est trop volumineuse."
        );
    }


    const messageGeneral = (
        donnees.erreur
        || donnees.detail
    );


    if (typeof messageGeneral === "string") {
        return messageGeneral;
    }


    const nomsChamps = {
        nom: "Nom",
        categorie: "Catégorie",
        description: "Description",
        quantite_disponible: "Quantité",
        photo: "Photo"
    };


    for (const [champ, erreurs] of Object.entries(donnees)) {

        const message = Array.isArray(erreurs)
            ? erreurs[0]
            : erreurs;


        if (typeof message === "string") {

            return `${
                nomsChamps[champ]
                || champ
            } : ${message}`;
        }
    }


    return estModification
        ? "Impossible de modifier le matériel. Vérifiez les informations saisies."
        : "Impossible d'ajouter le matériel. Vérifiez les informations saisies.";
}


async function enregistrerMateriel(
    event
) {

    event.preventDefault();


    const idMateriel = materielEnEditionId;

    const estModification = (
        idMateriel !== null
    );


    cacherMessageFormulaire();


    const nom = materialName.value.trim();

    const categorie = materialCategory.value.trim();

    const description = (
        materialDescription.value.trim()
    );

    const quantite = Number(
        materialStock.value
    );


    if (!nom) {

        afficherMessageFormulaire(
            "Le nom du matériel est obligatoire.",
            "error"
        );

        return;
    }


    if (
        Number.isNaN(quantite)
        || !Number.isInteger(quantite)
        || quantite < 0
    ) {

        afficherMessageFormulaire(
            "La quantité disponible est invalide.",
            "error"
        );

        return;
    }


    const formData = new FormData();


    formData.append(
        "nom",
        nom
    );

    formData.append(
        "categorie",
        categorie
    );

    formData.append(
        "description",
        description
    );

    formData.append(
        "quantite_disponible",
        quantite
    );


    if (materialPhoto.files.length > 0) {

        formData.append(
            "photo",
            materialPhoto.files[0]
        );
    }


    const endpoint = estModification
        ? `/admin/materiels/${idMateriel}/`
        : "/admin/materiels/";

    const methode = estModification
        ? "PATCH"
        : "POST";


    definirChargementMateriel(
        true
    );


    try {

        const response = await apiFetch(
            endpoint,
            {
                method: methode,
                body: formData
            }
        );


        let donnees = {};


        try {
            donnees = await response.json();
        } catch {
            donnees = {};
        }


        if (!response.ok) {

            afficherMessageFormulaire(
                obtenirMessageErreurMateriel(
                    response,
                    donnees,
                    estModification
                ),
                "error"
            );

            return;
        }


        reinitialiserFormulaireMateriel(
            false
        );


        afficherMessageFormulaire(
            estModification
                ? "Matériel modifié avec succès."
                : "Matériel ajouté avec succès.",
            "success"
        );


        afficherToast(
            estModification
                ? `${donnees.nom} a été modifié.`
                : `${donnees.nom} a été ajouté au catalogue.`,
            "success"
        );


        await chargerMateriels();


    } catch (erreur) {

        console.error(
            estModification
                ? "Erreur modification matériel :"
                : "Erreur ajout matériel :",
            erreur
        );


        afficherMessageFormulaire(
            "Le serveur est inaccessible.",
            "error"
        );


    } finally {

        definirChargementMateriel(
            false
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


tabs.forEach(
    bouton => {

        bouton.addEventListener(
            "click",
            function () {

                tabs.forEach(
                    tab => (
                        tab.classList.remove(
                            "active"
                        )
                    )
                );


                bouton.classList.add(
                    "active"
                );


                const tab = bouton.dataset.tab;


                if (tab === "demandes") {

                    demandesSection.classList.remove(
                        "hidden"
                    );

                    materielsSection.classList.add(
                        "hidden"
                    );

                } else {

                    demandesSection.classList.add(
                        "hidden"
                    );

                    materielsSection.classList.remove(
                        "hidden"
                    );
                }
            }
        );
    }
);


statusFilter.addEventListener(
    "change",
    afficherDemandes
);


demandesList.addEventListener(
    "click",
    function (event) {

        const bouton = event.target.closest(
            "button[data-action]"
        );


        if (!bouton) {
            return;
        }


        const idDemande = Number(
            bouton.dataset.id
        );


        const action = (
            bouton.dataset.action
        );


        traiterDemande(
            idDemande,
            action
        );
    }
);


materielsList.addEventListener(
    "click",
    function (event) {

        const bouton = event.target.closest(
            "button[data-material-action='edit']"
        );


        if (!bouton) {
            return;
        }


        const idMateriel = Number(
            bouton.dataset.id
        );


        if (!Number.isInteger(idMateriel)) {
            return;
        }


        commencerEditionMateriel(
            idMateriel
        );
    }
);


materialPhoto.addEventListener(
    "change",
    function () {

        const fichier = materialPhoto.files[0];


        if (!fichier) {

            mettreAJourApercuPhoto(
                photoMaterielActuelle
            );

            return;
        }


        const reader = new FileReader();


        reader.onload = function (event) {

            mettreAJourApercuPhoto(
                event.target.result
            );
        };


        reader.readAsDataURL(
            fichier
        );
    }
);


boutonAnnulerMateriel.addEventListener(
    "click",
    function () {
        reinitialiserFormulaireMateriel();
    }
);


formulaireMateriel.addEventListener(
    "submit",
    enregistrerMateriel
);


boutonDeconnexion.addEventListener(
    "click",
    deconnecterUtilisateur
);


async function initialiserAdministration() {

    const estAdmin = (
        await verifierAdministrateur()
    );


    if (!estAdmin) {
        return;
    }


    await Promise.all([
        chargerDemandes(),
        chargerMateriels()
    ]);
}


initialiserAdministration();
