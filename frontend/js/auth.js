const formulaireConnexion = document.getElementById(
    "login-form"
);

const champUsername = document.getElementById(
    "username"
);

const champPassword = document.getElementById(
    "password"
);

const boutonConnexion = document.getElementById(
    "login-button"
);

const texteBouton = document.getElementById(
    "login-button-text"
);

const spinner = document.getElementById(
    "login-spinner"
);

const message = document.getElementById(
    "message"
);

const boutonAfficherMotDePasse = document.getElementById(
    "toggle-password"
);


function afficherMessage(
    texte,
    type
) {
    message.textContent = texte;

    message.className = (
        `message message-${type}`
    );
}


function cacherMessage() {
    message.className = "message hidden";
}


function definirChargement(enChargement) {

    boutonConnexion.disabled = enChargement;

    if (enChargement) {
        texteBouton.textContent = (
            "Connexion..."
        );

        spinner.classList.remove(
            "hidden"
        );

    } else {
        texteBouton.textContent = (
            "Se connecter"
        );

        spinner.classList.add(
            "hidden"
        );
    }
}


boutonAfficherMotDePasse.addEventListener(
    "click",
    function () {

        const masque = (
            champPassword.type === "password"
        );

        champPassword.type = (
            masque
                ? "text"
                : "password"
        );

        boutonAfficherMotDePasse.textContent = (
            masque
                ? "🙈"
                : "👁"
        );
    }
);


formulaireConnexion.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        cacherMessage();

        const username = (
            champUsername.value.trim()
        );

        const password = (
            champPassword.value
        );

        if (!username || !password) {
            afficherMessage(
                "Veuillez renseigner tous les champs.",
                "error"
            );

            return;
        }

        definirChargement(true);

        try {

            const response = await fetch(
                `${API_BASE_URL}/auth/login/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": (
                            "application/json"
                        )
                    },

                    body: JSON.stringify({
                        username,
                        password
                    })
                }
            );


            if (!response.ok) {

                if (response.status === 401) {
                    afficherMessage(
                        "Nom d'utilisateur ou mot de passe incorrect.",
                        "error"
                    );

                } else {
                    afficherMessage(
                        "Impossible de vous connecter pour le moment.",
                        "error"
                    );
                }

                return;
            }


            const tokens = await response.json();


            sessionStorage.setItem(
                "access_token",
                tokens.access
            );

            sessionStorage.setItem(
                "refresh_token",
                tokens.refresh
            );


            const responseUtilisateur = await fetch(
                `${API_BASE_URL}/auth/me/`,
                {
                    headers: {
                        Authorization: (
                            `Bearer ${tokens.access}`
                        )
                    }
                }
            );


            if (!responseUtilisateur.ok) {

                sessionStorage.clear();

                afficherMessage(
                    "Impossible de récupérer votre profil.",
                    "error"
                );

                return;
            }


            const utilisateur = (
                await responseUtilisateur.json()
            );


            sessionStorage.setItem(
                "utilisateur",
                JSON.stringify(utilisateur)
            );


            afficherMessage(
                "Connexion réussie. Redirection...",
                "success"
            );


            setTimeout(
                function () {
                    window.location.href = (
                        "dashboard.html"
                    );
                },
                500
            );


        } catch (erreur) {

            console.error(
                "Erreur de connexion :",
                erreur
            );

            afficherMessage(
                "Le serveur est inaccessible. Vérifiez que le Backend est lancé.",
                "error"
            );

        } finally {

            definirChargement(false);

        }
    }
);


async function verifierSessionExistante() {

    const token = sessionStorage.getItem(
        "access_token"
    );

    if (!token) {
        return;
    }

    try {

        const response = await fetch(
            `${API_BASE_URL}/auth/me/`,
            {
                headers: {
                    Authorization: (
                        `Bearer ${token}`
                    )
                }
            }
        );

        if (response.ok) {
            window.location.href = (
                "dashboard.html"
            );
        }

    } catch (erreur) {
        console.error(
            "Vérification de session impossible.",
            erreur
        );
    }
}


verifierSessionExistante();