# Romeo Bot

Un bot Discord soundboard qui joue des sons aléatoires dans les canaux vocaux.

## Structure du projet

```
romeo-bot/
├── src/
│   ├── bot.py              # Initialisation du bot
│   ├── cogs/
│   │   ├── commands.py     # Commandes slash (/play)
│   │   ├── soundboard.py   # Logique de lecture des sons
│   │   └── status.py       # Gestion du statut du bot
│   └── utils/
│       ├── config.py       # Configuration et constantes
│       └── logger.py       # Système de logs colorés
├── config/
│   └── sound_titles.py     # Titres des sons
├── sounds/                 # Fichiers MP3/WAV
├── pics/                   # Images de profil
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances Python
├── docker-compose.yml      # Configuration Docker
├── Dockerfile             # Image Docker
└── .env                   # Variables d'environnement

```

## Installation

### Avec Docker (recommandé)

```bash
# Lancer le bot
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter le bot
docker-compose down

# Rebuild après modification
docker-compose up -d --build
```

### Sans Docker

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le bot
python main.py
```

## Configuration

Modifiez `src/utils/config.py` pour :
- Ajouter/retirer des canaux vocaux
- Changer les temps d'attente
- Modifier les statuts du bot

## Commandes

- `/play <son>` - Joue un son spécifique (avec autocomplete)

## Fonctionnalités

- Lecture aléatoire de sons dans les canaux vocaux
- Rotation automatique entre les canaux
- Détection de canaux vides
- Notifications dans le canal texte
- Changement de statut automatique
- Commande slash avec autocomplete pour tous les sons
- Logs colorés avec emojis
