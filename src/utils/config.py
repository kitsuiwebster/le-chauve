"""Configuration constants for the bot"""

# Liste des canaux vocaux où le bot peut jouer
VOICE_CHANNEL_IDS = [
    534010128773414926,
    811683007290146858,
    880881683749015622,
    530012749066010657,
    885570764047278120,
    534010172587114508,
    1017001428524486686,
    1150149299028635731,
    1298685917682204702
]

# Canal texte pour les notifications
TEXT_CHANNEL_ID = 1199479426497380423

# Canal d'attente
WAIT_CHANNEL_ID = 1200530884831477841

# Utilisateur à ignorer lors du comptage des membres
IGNORED_USER_ID = 1161683957440589976

# Temps d'attente (en secondes)
WAIT_AFTER_SOUND = 1200  # 20 minutes
WAIT_IN_WAIT_CHANNEL = 1800  # 30 minutes
EMPTY_CHANNEL_THRESHOLD = 20  # Nombre de canaux vides avant pause
PAUSE_AFTER_EMPTY_CHANNELS = 1800  # 30 minutes de pause

# Statuts du bot
BOT_STATUSES = [
    "TG!",
    "SUCE!",
    "MA BEUTEU???",
    "NON!"
]

# Intervalle de changement de statut (en secondes)
STATUS_CHANGE_INTERVAL = 10
