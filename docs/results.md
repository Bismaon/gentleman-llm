# Résultats

## Fonctionnalités

Gentleman-LLM est un système d’analyse automatisée du code Python basé sur :

1. **Analyse statique du code avec `ast`**  
    - Extraction de toutes les fonctions d’un fichier.  
    - Récupération des paramètres, lignes de début/fin, corps exact du code.
    - Détection des imports.
    - Analyse des appels internes entre fonctions.  
    - Inférence partielle du type de retour.

2. **Enrichissement sémantique via une LLM**  
    - Déduction automatique des types de paramètres.  
    - Génération d’une description concise du rôle de chaque fonction.  
    - Création de tags représentatifs.  
    - Détermination de la catégorie de la fonction.  
    - Correction/validation du type de retour si nécessaire.

3. **Validation stricte des réponses du modèle**  
    - Vérification du format des types.  
    - Validation des catégories.  
    - Gestion des erreurs et tentative automatique jusqu’à stabilité.  
    - Nettoyage et normalisation des sorties du modèle.

4. **Structure finale des données**  
    Pour chaque fichier Python analysé, Gentleman-LLM génère un objet JSON contenant :
    - le nom du fichier  
    - la liste complète des fonctions  
    - pour chaque fonction :  
        - nom  
        - paramètres et leurs types  
        - description générée  
        - tags  
        - catégorie  
        - type de retour  
        - relations (calls / called_by)  
        - code source exact  

5. **Export automatique**  
    - Renvoie le résultat sous forme de JSON dans `documents/results/...`  
    - Versionnement automatique (filename_1.json, filename_2.json, etc.)
