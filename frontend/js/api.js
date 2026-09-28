async function rafraichirAccessToken() {
    const refreshToken = sessionStorage.getItem(
        "refresh_token"
    );

    if (!refreshToken) {
        return null;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/auth/refresh/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    refresh: refreshToken
                })
            }
        );

        if (!response.ok) {
            return null;
        }

        const donnees = await response.json();

        sessionStorage.setItem(
            "access_token",
            donnees.access
        );

        return donnees.access;

    } catch (erreur) {
        console.error(
            "Erreur de rafraîchissement du token :",
            erreur
        );

        return null;
    }
}


async function apiFetch(
    endpoint,
    options = {}
) {
    let accessToken = sessionStorage.getItem(
        "access_token"
    );

    const headers = {
        ...(options.headers || {})
    };

    if (accessToken) {
        headers.Authorization = (
            `Bearer ${accessToken}`
        );
    }

    let response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers
        }
    );

    if (response.status === 401) {
        accessToken = await rafraichirAccessToken();

        if (!accessToken) {
            deconnecterUtilisateur();
            return response;
        }

        headers.Authorization = (
            `Bearer ${accessToken}`
        );

        response = await fetch(
            `${API_BASE_URL}${endpoint}`,
            {
                ...options,
                headers
            }
        );
    }

    return response;
}


function deconnecterUtilisateur() {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    sessionStorage.removeItem("utilisateur");

    window.location.href = "login.html";
}