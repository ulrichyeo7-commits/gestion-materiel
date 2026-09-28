const EST_LOCAL = [
    "127.0.0.1",
    "localhost"
].includes(
    window.location.hostname
);


const API_BASE_URL = EST_LOCAL
    ? "http://127.0.0.1:8000/api"
    : "https://gestion-materiel-api.onrender.com/api";