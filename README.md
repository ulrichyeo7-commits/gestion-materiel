# Gestion de matériel

Application web de gestion des demandes de matériel. Les utilisateurs consultent le catalogue, composent une demande et suivent son traitement. Les administrateurs gèrent le catalogue, les stocks et l'acceptation ou le refus des demandes.

## Fonctionnalités

- authentification par jetons JWT ;
- catalogue des matériels disponibles avec photo et stock ;
- création d'une demande contenant plusieurs matériels ;
- historique et filtrage des demandes de l'utilisateur ;
- interface d'administration protégée ;
- acceptation ou refus des demandes avec mise à jour du stock ;
- ajout et modification des caractéristiques d'un matériel.

## Technologies

- Backend : Python, Django, Django REST Framework et Simple JWT
- Documentation API : OpenAPI 3 et Swagger UI avec drf-spectacular
- Base de données : SQLite en local, PostgreSQL en production
- Frontend : HTML, CSS et JavaScript natif

## Prérequis

- Python 3.12 ou une version plus récente ;
- un navigateur web moderne.

## Installation

Depuis la racine du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py createsuperuser
```

Sous Linux ou macOS, remplacez `.\.venv\Scripts\python.exe` par
`.venv/bin/python` et `Copy-Item .env.example .env` par
`cp .env.example .env`.

## Démarrage en local

Lancez le backend depuis un premier terminal :

```powershell
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Lancez ensuite le frontend depuis un second terminal :

```powershell
.\.venv\Scripts\python.exe -m http.server 5500 --directory frontend --bind 127.0.0.1
```

Ouvrez <http://127.0.0.1:5500>. Le frontend ne doit pas être ouvert directement avec le protocole `file://`.

L'interface Django d'administration est disponible sur <http://127.0.0.1:8000/admin/>.

## Documentation de l'API

La documentation interactive Swagger UI est disponible sur <http://127.0.0.1:8000/api/docs/>. Le schéma OpenAPI brut est exposé sur <http://127.0.0.1:8000/api/schema/>.

Pour tester une route protégée dans Swagger UI :

1. appelez `POST /api/auth/login/` avec votre nom d'utilisateur et votre mot de passe ;
2. copiez la valeur du jeton `access` renvoyé, et non celle du jeton `refresh` ;
3. cliquez sur **Authorize**, puis saisissez le jeton d'accès. Swagger UI ajoute automatiquement le préfixe `Bearer` au schéma JWT ; dans un client qui attend l'en-tête complet, utilisez `Bearer <jeton_access>`.

Depuis la racine du projet, la commande suivante génère le schéma dans le dossier temporaire de Windows et échoue en cas d'erreur ou d'avertissement :

```powershell
.\.venv\Scripts\python.exe backend\manage.py spectacular --file "$env:TEMP\gestion-materiel-openapi.yaml" --validate --fail-on-warn
```

Le fichier produit est temporaire et n'a pas besoin d'être ajouté au dépôt.

## Configuration

Le backend charge le fichier `.env` placé à la racine du projet. Le fichier
`.env.example` fournit une base pour le développement, sans contenir de secret
réel. Les variables déjà définies dans l'environnement d'exécution restent
prioritaires sur celles du fichier `.env`.

| Variable | Valeur si elle est absente | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | aucune | Clé secrète Django, toujours obligatoire. Utilisez une valeur longue, aléatoire et différente pour chaque environnement. |
| `DJANGO_DEBUG` | `False` | Active ou désactive le mode debug. Cette option doit rester à `False` hors développement. |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Noms d'hôte acceptés, sans schéma et séparés par des virgules. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | liste vide | Origines autorisées à appeler l'API depuis un navigateur, avec leur schéma et séparées par des virgules. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | liste vide | Origines de confiance pour les requêtes protégées par CSRF. Cette liste est distincte de la configuration CORS. |
| `DATABASE_URL` | valeur vide | URL PostgreSQL. Si elle est absente ou vide, Django utilise automatiquement SQLite dans `backend/db.sqlite3`. |
| `DB_CONN_MAX_AGE` | `60` | Durée maximale, en secondes, de réutilisation d'une connexion PostgreSQL. Cette valeur n'est utilisée que lorsque `DATABASE_URL` est renseignée. |
| `DJANGO_SECURE_SSL_REDIRECT` | `False` | Redirige les requêtes HTTP vers HTTPS. À activer uniquement lorsque HTTPS est opérationnel. |
| `DJANGO_SESSION_COOKIE_SECURE` | `False` | N'envoie le cookie de session que par HTTPS. |
| `DJANGO_CSRF_COOKIE_SECURE` | `False` | N'envoie le cookie CSRF que par HTTPS. |
| `DJANGO_USE_X_FORWARDED_PROTO` | `False` | Autorise Django à reconnaître HTTPS via `X-Forwarded-Proto`. À activer seulement derrière un proxy de confiance qui contrôle cet en-tête. |
| `DJANGO_SECURE_HSTS_SECONDS` | `0` | Durée HSTS en secondes. Une valeur nulle désactive HSTS. |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | `False` | Étend HSTS aux sous-domaines. |
| `DJANGO_SECURE_HSTS_PRELOAD` | `False` | Ajoute la directive de préchargement HSTS. |
| `DJANGO_MEDIA_ROOT` | `backend/media` | Dossier dans lequel le stockage local enregistre les fichiers envoyés par les utilisateurs. |
| `DJANGO_MEDIA_URL` | `/media/` | Préfixe d'URL public des fichiers médias. |

Exemple de configuration hors développement avec des valeurs fictives :

```dotenv
DJANGO_SECRET_KEY=remplacez-par-une-cle-longue-aleatoire-et-secrete
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.materiel.example.com
DJANGO_CORS_ALLOWED_ORIGINS=https://materiel.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://materiel.example.com
DATABASE_URL=postgresql://gestion_user:mot_de_passe_fictif@db.example.internal:5432/gestion_materiel?sslmode=require
DB_CONN_MAX_AGE=60
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_USE_X_FORWARDED_PROTO=False
DJANGO_SECURE_HSTS_SECONDS=300
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
DJANGO_SECURE_HSTS_PRELOAD=False
DJANGO_MEDIA_ROOT=/chemin/vers/un/volume/persistant/media
DJANGO_MEDIA_URL=/media/
```

L'URL PostgreSQL ci-dessus est uniquement un exemple : elle ne contient aucun
vrai identifiant. Le projet accepte les schémas `postgresql://` et
`postgres://`. SQLite convient au développement local et aux tests, mais un
service PostgreSQL est préférable pour un déploiement durable ou comportant
plusieurs instances.

Les options HTTPS ne doivent pas être activées avant la mise en place effective
du certificat et du proxy. Pour HSTS, commencez avec une durée courte, puis
augmentez-la après validation. N'activez l'inclusion des sous-domaines et le
préchargement que si tous les domaines concernés sont durablement accessibles
en HTTPS.

Une fois les vraies variables de production chargées, contrôlez le profil avec :

```powershell
.\.venv\Scripts\python.exe backend\manage.py check --deploy
```

Les avertissements de cette commande doivent être analysés avant la mise en
ligne, en particulier ceux concernant HTTPS, HSTS et la robustesse de la clé
secrète.

L'adresse de l'API utilisée par le frontend se configure dans `frontend/js/config.js`.

### Fichiers statiques et médias

Les fichiers statiques sont les ressources fournies avec l'application, comme
les feuilles de style de l'administration Django. Ils peuvent être reconstruits
à chaque déploiement. Depuis la racine du projet, collectez-les avec :

```powershell
.\.venv\Scripts\python.exe backend\manage.py collectstatic --noinput
```

Sous Linux ou macOS, utilisez :

```shell
.venv/bin/python backend/manage.py collectstatic --noinput
```

La commande place les fichiers dans `backend/staticfiles/`. Elle ne déploie pas
le frontend HTML/CSS/JavaScript, qui reste une application statique séparée.

Les médias sont au contraire des données créées pendant l'utilisation, par
exemple les photos des matériels. Ils ne sont jamais inclus par `collectstatic`
et ne doivent pas être confiés à WhiteNoise. Le stockage local dans
`backend/media/` convient au développement. Pour un déploiement, il faudra
choisir plus tard, selon la plateforme, un volume persistant ou un stockage
d'objets et prévoir sa sauvegarde.

## Tests

```powershell
.\.venv\Scripts\python.exe backend\manage.py test gestion
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py makemigrations --check --dry-run
```

Les tests utilisent une base temporaire et ne modifient pas `backend/db.sqlite3`.

## Structure du projet

```text
gestion-materiel_V2/
|-- backend/
|   |-- config/          # Configuration Django
|   |-- gestion/         # Modèles, API, services et tests
|   `-- manage.py
|-- frontend/
|   |-- css/
|   |-- js/
|   `-- *.html
|-- requirements.txt
`-- README.md
```

## Données locales

La base SQLite, les fichiers envoyés dans `backend/media/`, les caches Python et l'environnement virtuel sont volontairement exclus de Git. Après un nouveau clonage, exécutez les migrations et créez un compte administrateur local.
