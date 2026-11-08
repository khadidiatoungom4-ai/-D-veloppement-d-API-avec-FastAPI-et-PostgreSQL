# API de gestion d'un atelier de couture

## 1. Présentation du projet

Cette application est une API REST développée avec FastAPI et PostgreSQL pour assurer la gestion d'un atelier de couture.

Elle permet de gérer les utilisateurs, les clients, les mesures, le catalogue des prestations, les commandes, les paiements, les livraisons et les statistiques de l'atelier.

## 2. Technologies utilisées

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT pour l'authentification
- Argon2 pour le hachage des mots de passe
- Pytest pour les tests
- Docker et Docker Compose

## 3. Structure du projet

```text
atelier_couture_api/
├── app/
│   ├── core/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── database.py
│   ├── main.py
│   └── seed.py
├── migrations/
├── tests/
├── .env.example
├── .gitignore
├── .dockerignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 4. Installation et configuration

### Prérequis

- Python
- PostgreSQL
- Git
- Docker Desktop (pour le lancement avec Docker)

### Cloner le projet

```bash
git clone https://github.com/khadidiatoungom4-ai/atelier_couture_api.git
cd atelier_couture_api
```

### Créer un environnement virtuel

```bash
python -m venv .venv
```

Activer l'environnement sous Windows :

```bash
.venv\Scripts\activate
```

### Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

### Configurer les variables d'environnement

Créer le fichier `.env` à partir du modèle :

```bash
copy .env.example .env
```

Renseigner les paramètres de connexion à la base de données, la clé secrète JWT et les informations du premier administrateur.

Ne jamais publier le fichier `.env` sur GitHub.

## 5. Lancement en local

### Appliquer les migrations

```bash
alembic upgrade head
```

### Initialiser les données

```bash
python -m app.seed
```

Cette commande permet de créer le premier administrateur et d'insérer les prestations du catalogue. Elle peut être exécutée plusieurs fois sans créer de doublons.

### Démarrer l'application

```bash
uvicorn app.main:app --reload
```

L'API est accessible à l'adresse :

http://127.0.0.1:8000

Documentation interactive :

http://127.0.0.1:8000/docs

Documentation alternative :

http://127.0.0.1:8000/redoc

## 6. Lancement avec Docker

Vérifier que Docker Desktop est démarré, puis exécuter :

```bash
docker compose up --build -d
```

Initialiser les données :

```bash
docker compose exec api python -m app.seed
```

Consulter les journaux de l'API :

```bash
docker compose logs --tail 30 api
```

Arrêter les conteneurs :

```bash
docker compose down
```

L'API est accessible sur le port 8000 et PostgreSQL sur le port 5433 de la machine hôte.

## 7. Authentification et rôles

L'API utilise une authentification par jeton JWT.

Les rôles prévus dans l'application sont :

- **admin** : administration de l'application et gestion des utilisateurs.
- **accueil** : gestion des clients, commandes, paiements et livraisons.
- **tailleur** : gestion des mesures et suivi de la production.

Pour accéder aux routes protégées, il faut d'abord se connecter avec les identifiants d'un utilisateur actif, puis utiliser le jeton obtenu dans le bouton **Authorize** de Swagger.

## 8. Routes de l'API

Toutes les routes métier utilisent le préfixe `/api/v1`.

### Authentification

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Connexion |
| GET | `/api/v1/auth/me` | Informations sur l'utilisateur connecté |

### Utilisateurs

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/v1/utilisateurs/` | Créer un utilisateur |
| GET | `/api/v1/utilisateurs/` | Lister les utilisateurs |
| GET | `/api/v1/utilisateurs/{utilisateur_id}` | Consulter un utilisateur |
| PATCH | `/api/v1/utilisateurs/{utilisateur_id}` | Modifier un utilisateur |

### Clients

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/v1/clients/` | Créer un client |
| GET | `/api/v1/clients/` | Lister les clients |
| GET | `/api/v1/clients/{client_id}` | Consulter un client |
| PATCH | `/api/v1/clients/{client_id}` | Modifier un client |
| DELETE | `/api/v1/clients/{client_id}` | Supprimer un client |

### Catalogue

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/v1/catalogue/` | Ajouter une prestation |
| GET | `/api/v1/catalogue/` | Consulter le catalogue |
| GET | `/api/v1/catalogue/{type_vetement_id}` | Consulter une prestation |
| PATCH | `/api/v1/catalogue/{type_vetement_id}` | Modifier une prestation |

### Mesures

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/v1/clients/{client_id}/mesures` | Enregistrer des mesures |
| GET | `/api/v1/clients/{client_id}/mesures` | Consulter l'historique des mesures |
| GET | `/api/v1/clients/{client_id}/mesures/derniere` | Consulter les dernières mesures |
| GET | `/api/v1/mesures/{mesure_id}` | Consulter une mesure |
| PATCH | `/api/v1/mesures/{mesure_id}` | Modifier une mesure |

### Commandes

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/v1/commandes` | Créer une commande |
| GET | `/api/v1/commandes` | Lister les commandes |
| GET | `/api/v1/commandes/{commande_id}` | Consulter une commande |
| PATCH | `/api/v1/commandes/{commande_id}` | Modifier une commande |
| POST | `/api/v1/commandes/{commande_id}/lignes` | Ajouter une ligne |
| DELETE | `/api/v1/commandes/{commande_id}/lignes/{ligne_id}` | Supprimer une ligne |
| POST | `/api/v1/commandes/{commande_id}/statut` | Modifier le statut |
| GET | `/api/v1/commandes/{commande_id}/historique` | Consulter l'historique |

### Paiements

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/v1/commandes/{commande_id}/paiements` | Enregistrer un paiement |
| GET | `/api/v1/commandes/{commande_id}/paiements` | Consulter les paiements |
| DELETE | `/api/v1/paiements/{paiement_id}` | Annuler un paiement |

### Livraisons

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/v1/commandes/{commande_id}/livraison` | Consulter la livraison d'une commande |
| PUT | `/api/v1/commandes/{commande_id}/livraison` | Planifier ou modifier une livraison |
| POST | `/api/v1/commandes/{commande_id}/livraison/confirmer` | Confirmer une livraison |
| GET | `/api/v1/livraisons` | Lister les livraisons |

### Statistiques

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/v1/statistiques/tableau-de-bord` | Tableau de bord |
| GET | `/api/v1/statistiques/chiffre-affaires` | Chiffre d'affaires |
| GET | `/api/v1/statistiques/types-vetement` | Statistiques par type de vêtement |
| GET | `/api/v1/statistiques/top-clients` | Meilleurs clients |
| GET | `/api/v1/statistiques/impayes` | Suivi des impayés |

### Routes générales

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Message d'accueil |
| GET | `/health` | Vérification de l'état de l'API et de la base de données |

## 9. Tests

Les tests automatisés sont exécutés avec Pytest :

```bash
python -m pytest -v
```

Les tests actuellement présents vérifient notamment :

- Le fonctionnement de la route de santé.
- Le refus de suppression d'un client ayant des commandes.
- La suppression autorisée d'un client sans commande.

## 10. Initialisation du catalogue

Le catalogue est initialisé automatiquement par le script `app.seed`.

Les prestations prévues sont le boubou, le costume deux pièces, la robe, l'ensemble wax, la chemise, le pantalon et les retouches.

## 11. Auteur

Projet réalisé dans le cadre du développement d'une API de gestion d'un atelier de couture.