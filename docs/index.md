# Projections avec les LLMs

> **Thèmes**: Science de données, Génie logiciel, LLM
> **Superviseur**: Louis Edouard Lafontant  
> **Collaborateurs:** ...

## Équipe

Esteban Maries 20235999

## Description du projet

### Contexte

Le domaine d'application de ce projet comprend l'Ingénierie Logicielle ainsi que du Traitement Automatique du Langage Naturel (NLP), avec une emphase sur l'Analyse du Code Source et la Compréhension de Programme. Alors que les systèmes logiciels gagnent en complexité, l'intégration des Grands Modèles de Langage (LLMs) dans les flux de travail d'analyse de code devient essentielle, presque obligatoire pour améliorer l'efficacité, la précision et l'automatisation du code.

Cependant, les développeurs passent beaucoup de temps à chercher et digérer les informations du code source qui permettent d’y contribuer ou de le comprendre, surtout lorsqu'ils travaillent avec du code peu familier ou des environnements complexes.

Une approche proposée pour atténuer ce problème est le concept de projections de code. Ces projections permettent de visualiser le même code source de multiples façons dynamiques. Au lieu d'une structure rigide, le programmeur peut choisir une structure qu'il juge la plus pertinente pour sa tâche actuelle.

Ce projet s'inscrit comme une extension possible du projet Gentleman visant à rendre la modélisation plus accessible aux experts du domaine et aux praticiens.

### Problématique ou motivations

#### Problématique

La problématique principale que ce projet cherche à résoudre est de combler le fossé qui existe entre la compréhension profonde du code, fournie par les LLMs, et la présentation structurée et dynamique du code source, donné par Gentleman.
Comment utiliser un LLM pour fournir les fragments de code pertinents et les présenter aux développeurs sous forme de projections compréhensible ?

#### Motivations

1. Les développeurs passent un temps considérable à comprendre le comportement et la logique du code pour faciliter son édition et maintenance. En fournissant des projections ciblées, l'outil pourrait réduire considérablement la quantité de code à parcourir par le développeur.

2. Bien que les LLMs excellent à expliquer le code en langage naturel, les requêtes ouvertes peuvent encore nécessiter un prompt engineering difficile, en particulier pour les novices. L'intégration d'un mécanisme de projection permet de matérialiser l'analyse du LLM dans des vues concrètes et interactives, offrant une assistance visuelle du code au développeur.

### Proposition et objectifs

#### Proposition solution

1. Lecture et Contexte : Le système lira le code source.

2. Analyse par LLM : Un LLM analysera le code pour comprendre sa structure et sa fonctionnalité, et pour identifier les fragments de code qui correspondent à des préoccupations sémantiques implicites. Son importance, rôle dans le code

3. Sortie des Projections : Les sorties du LLM seront donnes en deux fichiers un qui est les projections et l’autre les concepts qui définiront le code source pour Gentleman.

#### Objectifs Concrets

1. Définir et implémenter une méthodologie pour contextualiser le code source et formuler les requêtes auprès du LLM afin que ce dernier puisse identifier les différents fragments de code pertinents, ainsi que leurs liens dans le code source.

2. Manier le LLM afin qu’il renvoie dans le format attendu par Gentleman, c’est à dire un fichier projection et un fichier concept. Qui permettront à Gentleman de modeler le code source donné par le développeur.

## Échéancier

!!! info
    Le suivi complet est disponible dans la page [Suivi de projet](suivi.md).

| Jalon (*Milestone*)            | Date prévue   | Livrable                            | Statut      |
|--------------------------------|---------------|-------------------------------------|-------------|
| Ouverture de projet            | 16 septembre  | Choix de projet                     | ✅ Terminé  |
| Definir le projet              | 28 septembre  | Description du projet remis         | ✅ Terminé  |
| Definition de fonctions        | 5 octobre     | Document sur les fonctions          | ✅ Terminé  |
| Choix LLM                      | 5 octobre     | LLM                                 | ✅ Terminé  |
| Essai de la LLM                | 8 septembre  | Resultats                           | ✅ Terminé  |
| Ajout d'un template json du resultat attendu     | 30 septembre  | Fichier JSON          | ✅ Terminé  |
| Ajout de profondeur d'exploration/définition du LLM  | 6 octobre     | Code | ✅ Terminé  |
| Correction des défauts dans l'architecture           | 12 octobre     | Code    | ✅ Terminé  |
| Peaufinage des prompts et du resultats de sortie              | 20 octobre    | Code et résultats                      | ✅ Terminé  |
| Reconstruction de la structure de requete      | 11 novembre   | Code              | ✅ Terminé  |
| Ajout d'informations extraites par fonctions              | 20 novembre  | Code et résultats               | ✅ Terminé  |
| Creation de l'API et last minute code check                          | 30 novembre| Plan + Résultats intermédiaires     | ✅ Terminé  |
| Ecriture du suivi et du rapport              | 1 décembre    | Analyse des résultats + Discussion  | 🔄 En cours  |
| Présentation         | 11 décembre   | Présentation               | ⏳ À venir  |
| Rapport         | 19 décembre   | Rapport              | ⏳ À venir  |
