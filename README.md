# Gestionnaire de Tâches

Application desktop de gestion de tâches développée en Python avec Tkinter.

## Fonctionnalités

- **Gestion complète des tâches** : Créer, modifier, supprimer des tâches
- **Priorités** : 4 niveaux de priorité (Basse, Moyenne, Haute, Urgente)
- **Catégories** : Organiser vos tâches par catégories personnalisables
- **Dates d'échéance** : Définir des dates limites pour vos tâches
- **Statuts** : À faire, En cours, Terminée
- **Filtres multiples** :
  - Toutes les tâches
  - Tâches du jour
  - Tâches à venir
  - Tâches en retard
  - Tâches en cours
- **Codes couleur** :
  - Rouge clair : Tâches en retard
  - Rouge : Tâches urgentes
  - Orange : Tâches à haute priorité
  - Gris : Tâches terminées
- **Stockage local** : Toutes les données sont sauvegardées localement dans un fichier JSON

## Installation

### Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger ce dépôt**

2. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

Note : Si vous n'avez pas besoin du sélecteur de date graphique, vous pouvez sauter l'installation de `tkcalendar`. L'application fonctionnera avec un champ de saisie de date simple.

## Utilisation

### Lancer l'application

```bash
python main_app.py
```

### Créer une tâche

1. Cliquer sur le bouton **"Nouvelle tâche"**
2. Remplir les informations :
   - **Titre** (obligatoire)
   - **Description** (optionnel)
   - **Catégorie** (par défaut : Général)
   - **Priorité** (Basse, Moyenne, Haute, Urgente)
   - **Statut** (À faire, En cours, Terminée)
   - **Date d'échéance** (optionnel)
3. Cliquer sur **"Enregistrer"**

### Modifier une tâche

- Double-cliquer sur une tâche dans la liste, ou
- Sélectionner une tâche et cliquer sur **"Modifier"**

### Supprimer une tâche

1. Sélectionner une tâche
2. Cliquer sur **"Supprimer"**
3. Confirmer la suppression

### Marquer une tâche comme terminée

1. Sélectionner une tâche
2. Cliquer sur **"Marquer terminée"**

### Filtrer les tâches

Utilisez les boutons en haut de la fenêtre :
- **Toutes** : Afficher toutes les tâches
- **Aujourd'hui** : Afficher les tâches dont l'échéance est aujourd'hui
- **À venir** : Afficher les tâches avec une date future
- **En retard** : Afficher les tâches dépassant leur date d'échéance
- **En cours** : Afficher les tâches avec le statut "En cours"

### Ajouter une catégorie

1. Lors de la création/modification d'une tâche
2. Cliquer sur **"Nouvelle catégorie"**
3. Entrer le nom de la catégorie
4. Cliquer sur **"Ajouter"**

## Stockage des données

Les tâches sont automatiquement sauvegardées dans le fichier `tasks.json` à la racine de l'application. Ce fichier est créé automatiquement lors de l'ajout de la première tâche.

### Transférer vos tâches sur un autre ordinateur

1. Copier le fichier `tasks.json` depuis votre ordinateur actuel
2. Installer l'application sur le nouvel ordinateur (voir section Installation)
3. Placer le fichier `tasks.json` dans le même dossier que `main_app.py`
4. Lancer l'application

## Structure du projet

```
todomanage/
├── main_app.py          # Application principale
├── task_model.py        # Modèle de données pour les tâches
├── task_manager.py      # Gestion du stockage et des opérations
├── task_dialog.py       # Interface de dialogue pour ajouter/modifier
├── requirements.txt     # Dépendances Python
├── tasks.json          # Fichier de données (créé automatiquement)
└── README.md           # Ce fichier
```

## Compatibilité

- **Système d'exploitation** : Windows, macOS, Linux
- **Python** : 3.7+
- **Interface graphique** : Tkinter (inclus avec Python)

## Dépannage

### L'application ne se lance pas

- Vérifier que Python 3.7+ est installé : `python --version`
- Vérifier que Tkinter est installé (généralement inclus avec Python)
- Sur Ubuntu/Debian : `sudo apt-get install python3-tk`

### Le sélecteur de date ne s'affiche pas

- Si `tkcalendar` n'est pas installé, l'application utilisera un champ de texte simple
- Format de date à respecter : `AAAA-MM-JJ` (ex: 2025-11-09)

### Les données sont perdues

- Vérifier que le fichier `tasks.json` existe et n'est pas corrompu
- En cas de corruption, supprimer le fichier (les données seront perdues) et relancer l'application

## Licence

Ce projet est libre d'utilisation pour un usage personnel ou commercial.
