# Romeo Bot

Un bot Discord musical qui joue des chansons aléatoires dans les canaux vocaux.

## Structure du projet

```
romeo-bot/
├── src/
│   ├── bot.py              # Initialisation du bot
│   ├── cogs/
│   │   ├── commands.py     # Commandes (!next)
│   │   ├── music.py        # Logique de lecture musicale
│   │   └── status.py       # Gestion du statut du bot
│   └── utils/
│       └── config.py       # Configuration et constantes
├── config/
│   └── song_titles.py      # Titres des chansons
├── songs/                  # Fichiers MP3/WAV
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

- `!next` - Passe à la chanson suivante

## Fonctionnalités

- Lecture aléatoire de musique dans les canaux vocaux
- Rotation automatique entre les canaux
- Détection de canaux vides
- Notifications dans le canal texte
- Changement de statut automatique
