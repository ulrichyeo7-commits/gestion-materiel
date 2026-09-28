import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


VALEURS_VRAIES = {
    "1",
    "on",
    "true",
    "yes",
}

VALEURS_FAUSSES = {
    "0",
    "false",
    "no",
    "off",
}


def env_bool(nom, default=False):
    valeur = os.getenv(nom)

    if valeur is None or not valeur.strip():
        return default

    valeur_normalisee = valeur.strip().lower()

    if valeur_normalisee in VALEURS_VRAIES:
        return True

    if valeur_normalisee in VALEURS_FAUSSES:
        return False

    raise ImproperlyConfigured(
        f"La variable {nom} doit être un booléen "
        "(true/false, yes/no, on/off ou 1/0)."
    )


def env_int(nom, default=0, minimum=None):
    valeur = os.getenv(nom)

    if valeur is None or not valeur.strip():
        resultat = default
    else:
        try:
            resultat = int(valeur)
        except ValueError as erreur:
            raise ImproperlyConfigured(
                f"La variable {nom} doit être un entier."
            ) from erreur

    if minimum is not None and resultat < minimum:
        raise ImproperlyConfigured(
            f"La variable {nom} doit être supérieure "
            f"ou égale à {minimum}."
        )

    return resultat


def env_list(nom, default=""):
    return [
        element.strip()
        for element in os.getenv(
            nom,
            default,
        ).split(",")
        if element.strip()
    ]


def database_config(base_dir):
    database_url = os.getenv(
        "DATABASE_URL",
        "",
    ).strip()

    if not database_url:
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": Path(base_dir) / "db.sqlite3",
            }
        }

    try:
        configuration = dj_database_url.parse(
            database_url,
            conn_max_age=env_int(
                "DB_CONN_MAX_AGE",
                default=60,
                minimum=0,
            ),
            conn_health_checks=True,
        )
    except (KeyError, ValueError):
        raise ImproperlyConfigured(
            "La variable DATABASE_URL est invalide."
        ) from None

    if (
        configuration.get("ENGINE")
        != "django.db.backends.postgresql"
    ):
        raise ImproperlyConfigured(
            "DATABASE_URL doit utiliser le schéma "
            "postgresql:// ou postgres://."
        )

    champs_manquants = [
        champ
        for champ in (
            "NAME",
            "USER",
            "HOST",
        )
        if not configuration.get(champ)
    ]

    if champs_manquants:
        raise ImproperlyConfigured(
            "DATABASE_URL doit préciser le nom de la base, "
            "l'utilisateur et l'hôte PostgreSQL."
        )

    return {
        "default": configuration
    }
