# Suivi de projet

## Semaine 1

!!! info "Notes"
    - Lecture de la documentation sur les LLMs, leur usage sur du code ainsi que celle sur Gentleman.
    - Écriture de la description du projet

!!! abstract "Prochaines étapes"
    - Choisir une LLM pour le projet
    - Définition des fonctions dans le code
    - Essayer la LLM

## Semaine 3

!!! info "Notes"
    - Définition de différents types de fonctions pour la LLM
    - Choix et essai de la LLM

!!! warning "Problème possible"
    - Il faut pouvoir avoir assez de crédits pour faire des requêtes auprès du LLM.

!!! abstract "Avance"
    - Premier essai plutôt bon.

## Semaine 5

!!! info "Notes"
    - Besoin de définir de manière plus sévère les instructions
    - Besoin d'un template pour le `concept.json`

!!! warning "Problèmes"
    - Le LLM ne suit pas toujours les instructions, crée des `tags` qui n'existent pas ainsi que fait des actions explicitement interdites.

## Semaine 7

!!! info "Notes"
    - Ajout du template `concept.json` au projet
    - Ajout de règles, étapes de réflexion, définition de concepts Gentleman, d'un persona, ainsi que 3 niveaux de profondeur dans l'analyse.
    - Les trois niveaux sont :
        - Niveau 0 : contexte level C4 model (type de fonction, nature, paramètres, return types)
        - Niveau 1: container level C4 model (Niv 0 + relations avec d'autres fonctions)
        - Niveau 2 : abstraction semantic et relationnel (Niv 1 + contraintes dans la fonction).
    - Changement de moonshotai à meta-llama dû aux coûts des requêtes.
    - Division en deux entre les types de fonctions classiques et celles plus précises.
    - Le LLM renvoie des classifications plus similaires à chaque run

!!! warning "Problèmes"
    - La structure du JSON n'est pas garantie, et le LLM renvoie parfois du texte en plus.

## Semaine 9

!!! info "Notes"
    - Séparation du code, création du fichier `util.py` qui contiendra les fonctions utilitaires utilisées par le LLM et nous-mêmes.
    - Enrichissement des prompts pour essayer de faire mieux comprendre le LLM.
    - Ajout d'une note de hiérarchie des prompts pour la LLM.
    - Création d'une fonction principale pour extraire les fonctions d'un fichier.
    - Modification des types de fonctions pour simplifier la tâche au LLM, et clarification des points nécessaires, optionnels, ou qu'elle ne doit pas avoir.
    - Ajout d'un champ `reasoning` pour que l'on comprenne le choix du LLM.
    - Simplification des prompts dans l'idée de ne pas surcharger la LLM.
!!! warning "Problèmes"
    - Il y a quelques résultats, mais le LLM semble vraiment avoir du mal à output le JSON dans le bon format avec les bonnes valeurs.
    - Le LLM renvoie parfois des fichiers sans JSON, et dans un format qui n'est pas stable (change entre chaque run).

## Semaine 11

!!! info "Notes"
    - Changement de fichier retour, JSON -> YAML, dans l'espoir que le LLm soit plus stable dans ces réponses. Changement aussi du fichier contenant les types de fonctions de JSON vers du texte dans local.py.
    - Essaie de faire en sorte que la LLM renvoie seulement les types des paramètres de la fonction, et de réussir à valider sa réponse.
    - Changement de la structure de Gentleman LLM, désormais les fonctions auront leurs parties individuelles décrites par la LLM. La LLM va donc définir les types des paramètres, la description de chaque fonction, les tags, un à un, à la place de toutes les fonctions en un coup.

!!! warning "Problèmes"
    - Réponse du LLM n'est pas stable, pas un format unique et entrave grandement la possibilité d'utiliser ses réponses qui ne sont pas portables, manquant de structure.
    - Abandon de la première idée pour Gentleman LLM, les requêtes ne se feront pas sur tout le fichier d'un coup mais sur chaque fonction afin de nous permettre de  pouvoir parser les réponses du modèle.

## Semaine 13

!!! info "Notes"
    - Création de la base de la nouvelle structure du code, ajout de la possibilité de réessayer des kerries, si un output n'est pas valide.
    - Ajout de la définition du type de retour et de la catégorie de la fonction.
    - Création de logging et erreur handling pour chaque partie de la définition des fonctions.
    - Création d'une fonction dédiée à générer les types valides Python que l'on comparera aux réponses du LLM.
    - Ajout des imports du fichier dans lequel se situe la fonction afin de les utiliser comme type pour comparer aux réponses du LLM.
    - Création de la classe Gentleman LLM qui contiendra le code principal dans l'analyse de fichiers et leurs fonctions.
    - Création des gentleman requests, uploads et analyses qui forment l'API de Gentleman LLM.

!!! warning "Problèmes"
    - La définition des types de retour des fonctions n'est pas correcte à 100%, une erreur d'attribution de valeur ou de type peut avoir lieu lorsque la fonction contient plusieurs retours, ceci est dû à la façon dont AST parcours les fichiers Python.
