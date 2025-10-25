# Snake Ultimate Edition

Le jeu Snake le plus complet jamais créé en Python ! Avec multijoueur, modes de jeu variés, effets visuels avancés et bien plus.

## 🎮 Fonctionnalités Principales

### Modes de Jeu
- **Mode Classique** : Le Snake traditionnel amélioré
- **Mode Portails** : Téléportation d'un côté à l'autre de l'écran
- **Mode Obstacles** : Obstacles fixes et mobiles à éviter
- **Multijoueur Local** : Deux joueurs sur le même écran

### Power-ups Avancés
- **🔴 Fruits Rouges** : +1 point (50% de chance)
- **🔵 Fruits Bleus** : +5 points (15% de chance)  
- **🟡 Fruits Dorés** : +2 points + ralentit le jeu (10% de chance)
- **🟣 Fruits Violets** : +3 points + réduit la taille (10% de chance)
- **🔵 Fruits Cyan** : +4 points + mode fantôme (10% de chance)
- **🟠 Fruits Orange** : +3 points + boost de vitesse (5% de chance)

### Effets Visuels Spectaculaires
- **Particules** : Explosions colorées quand on mange
- **Animations** : Fruits qui pulsent et scintillent
- **Dégradés** : Snake avec effet de fondu
- **Thèmes visuels** : 3 thèmes de couleurs différents
- **Grille dynamique** : Motifs de fond subtils
- **Effets fantôme** : Transparence en mode fantôme

### Système Audio Avancé
- **Sons générés** : Tons et accords créés dynamiquement
- **4 types de sons** : Manger, power-up, level-up, game over
- **Effets contextuels** : Sons différents selon les actions

### Interface Utilisateur Complète
- **Menu principal** avec navigation
- **Statistiques détaillées** : temps, niveau, parties jouées
- **Légende interactive** des power-ups
- **Indicateurs d'état** en temps réel
- **Écran de game over** avec statistiques complètes

## 🕹️ Contrôles

### Mode Solo
- **Flèches directionnelles** : Déplacer le snake
- **ESPACE** : Sprint (vitesse x2)
- **ECHAP** : Retour au menu
- **T** (dans le menu) : Changer de thème

### Mode Multijoueur
**Joueur 1 :**
- **Flèches** : Déplacement
- **ESPACE** : Sprint

**Joueur 2 :**
- **WASD** : Déplacement  
- **SHIFT DROIT** : Sprint

### Navigation Menu
- **Flèches HAUT/BAS** : Naviguer
- **ENTRÉE/ESPACE** : Sélectionner

## 🚀 Installation et Lancement

### Prérequis
```bash
pip install pygame
```

### Versions Disponibles

**Version Ultimate (Recommandée) :**
```bash
python snake_ultimate.py
```

**Version Enhanced :**
```bash
python snake_enhanced.py
```

**Version Classique :**
```bash
python snakeGame.py
```

## 🎯 Modes de Jeu Détaillés

### Mode Classique
- Snake traditionnel avec power-ups
- Collision avec les bords = game over
- Vitesse progressive selon le niveau

### Mode Portails
- Téléportation automatique d'un côté à l'autre
- Pas de collision avec les bords
- Stratégie différente requise

### Mode Obstacles
- 5 obstacles sur la carte
- 30% d'obstacles mobiles qui bougent
- Difficulté accrue

### Multijoueur Local
- 2 snakes simultanés
- 15 fruits au lieu de 10
- Collision entre joueurs possible
- Score séparé pour chaque joueur

## 🏆 Système de Progression

### Niveaux
- **Niveau 1** : Vitesse de base (8 FPS)
- **Niveau 2+** : +1.5 FPS par niveau
- **Maximum** : 25 FPS

### Effets Temporaires
- **Ralenti** : Divise la vitesse par 2 (5 secondes)
- **Boost** : Multiplie la vitesse par 1.5 (5 secondes)
- **Fantôme** : Traverse tout (3 secondes)
- **Sprint** : Double la vitesse (tant que maintenu)

## 📊 Statistiques Sauvegardées

- **Meilleur score** persistant
- **Nombre de parties** jouées
- **Temps total** de jeu
- **Données JSON** facilement modifiables

## 🎨 Fonctionnalités Techniques

### Architecture
- **Programmation orientée objet** propre
- **Classes séparées** : Snake, PowerUp, Particle, Obstacle, Game
- **Gestion d'erreurs** complète
- **Performance optimisée**

### Effets Avancés
- **Système de particules** avec physique
- **Animations fluides** avec math.sin
- **Collision detection** optimisée
- **Rendu multicouche**

### Audio Procédural
- **Génération de tons** mathématique
- **Accords harmoniques** pour les level-ups
- **Gestion d'erreurs** audio
- **Sons contextuels**

## 📁 Structure des Fichiers

```
jeuSnake/
├── snake_ultimate.py      # Version complète
├── snake_enhanced.py      # Version intermédiaire  
├── snakeGame.py          # Version basique
├── requirements.txt      # Dépendances
├── README.md            # Documentation
├── game_data.json       # Données sauvegardées (auto-créé)
└── best_score.json      # Ancien format (auto-créé)
```

## 🔧 Configuration

### Paramètres Modifiables
- **Résolution** : WIDTH, HEIGHT (défaut: 1200x800)
- **Taille cellules** : CELL_SIZE (défaut: 20)
- **Vitesse de base** : base_speed (défaut: 8)
- **Nombre de fruits** : 10 solo, 15 multijoueur

### Thèmes Visuels
1. **Classique** : Fond noir, grille grise
2. **Océan** : Fond bleu foncé, grille bleue
3. **Nuit** : Fond gris foncé, grille subtile

## 🎮 Conseils de Jeu

### Stratégies
- **Mode Portails** : Utilisez la téléportation tactiquement
- **Power-ups** : Priorisez les fruits bleus (+5 points)
- **Mode Fantôme** : Traversez votre propre corps
- **Sprint** : Utilisez avec parcimonie pour économiser le contrôle

### Multijoueur
- **Coopération** : Partagez les fruits équitablement
- **Compétition** : Bloquez l'adversaire stratégiquement
- **Vitesse** : Le plus rapide détermine la vitesse globale

## 🚀 Améliorations Futures Possibles

- **Mode en ligne** avec serveur
- **Plus de power-ups** (invisibilité, téléportation manuelle)
- **Éditeur de niveaux** personnalisés
- **Musique de fond** procédurale
- **Replay system** pour revoir les parties
- **Tournois** avec classements
- **Skins personnalisables** pour les snakes

## 🐛 Résolution de Problèmes

### Erreurs Communes
- **Pas de son** : Normal si pygame.mixer échoue
- **Performance** : Réduisez la résolution si nécessaire
- **Contrôles** : Vérifiez que les touches ne sont pas bloquées

### Support
Le jeu est entièrement autonome et ne nécessite que Pygame. Tous les assets sont générés par code pour éviter les dépendances externes.

---

**Développé avec ❤️ en Python + Pygame**

*Version Ultimate - La référence des jeux Snake !*