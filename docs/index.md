# Nom du projet

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

Ce projet s'inscrit comme une extension possible du projet gentleman visant à rendre la modélisation plus accessible aux experts du domaine et aux praticiens.

### Problématique ou motivations

#### Problématique
La problématique principale que ce projet cherche à résoudre est de combler le fossé qui existe entre la compréhension profonde du code, fournie par les LLMs, et la présentation structurée et dynamique du code source, donné par Gentleman.
Comment peut-on, à l’aide d’une LLM, fournir les fragments de code pertinents et les présenter aux développeurs sous forme de projections compréhensible ?

#### Motivations

1.	Les développeurs passent un temps considérable à comprendre le comportement et la logique du code pour faciliter son édition et maintenance. En fournissant des projections ciblées, l'outil pourrait réduire considérablement la quantité de code à parcourir par le développeur. 

2.	Bien que les LLMs excellent à expliquer le code en langage naturel, les requêtes ouvertes peuvent encore nécessiter un prompt engineering difficile, en particulier pour les novices. L'intégration d'un mécanisme de projection structurelle permet de matérialiser l'analyse du LLM dans des vues concrètes et interactives, offrant une assistance visuelle du code au développeur.

### Proposition et objectifs

#### Proposition solution

1.	Lecture et Contexte : Le système lira le code source.

2.	Analyse par LLM : Un LLM analysera le code pour comprendre ses schémas, sa structure et sa fonctionnalité, et pour identifier les fragments de code qui correspondent à des préoccupations sémantiques implicites.

3.	Sortie des Projections : Les sorties du LLM seront donnes en deux fichiers un qui est les projections et l’autre les concepts qui définiront le code source pour gentleman. 

#### Objectifs Concrets

1.	Définir et implémenter une méthodologie pour contextualiser la code source et formuler les requêtes auprès du LLM afin que ce dernier puisse identifier les fragments de code pertinents, et les différents liens de ces fragments de code dans le code source.

2.	Manier le LLM afin qu’il renvoie dans le format attendu par Gentleman, c’est à dire un fichier projection et un fichier concept. Qui permettront à Gentleman de modeler le code source donne par le développeur.

## Échéancier

!!! info
    Le suivi complet est disponible dans la page [Suivi de projet](suivi.md).

| Jalon (*Milestone*)            | Date prévue   | Livrable                            | Statut      |
|--------------------------------|---------------|-------------------------------------|-------------|
| Ouverture de projet            | 1 septembre   | Proposition de projet               | ✅ Terminé  |
| Analyse des exigences          | 16 septembre  | Document d'analyse                  | 🔄 En cours |
| Prototype 1                    | 23 septembre  | Maquette + Flux d'activités         | ⏳ À venir  |
| Prototype 2                    | 30 septembre  | Prototype finale + Flux             | ⏳ À venir  |
| Architecture                   | 30 septembre  | Diagramme UML ou modèle C4          | ⏳ À venir  |
| Modèle de donneés              | 6 octobre     | Diagramme UML ou entité-association | ⏳ À venir  |
| Revue de conception            | 6 octobre     | Feedback encadrant + ajustements    | ⏳ À venir  |
| Implémentation v1              | 20 octobre    | Application v1                      | ⏳ À venir  |
| Implémentation v2 + tests      | 11 novembre   | Application v2 + Tests              | ⏳ À venir  |
| Implémentation v3              | 1er décembre  | Version finale                      | ⏳ À venir  |
| Tests                          | 11-31 novembre| Plan + Résultats intermédiaires     | ⏳ À venir  |
| Évaluation finale              | 8 décembre    | Analyse des résultats + Discussion  | ⏳ À venir  |
| Présentation + Rapport         | 15 décembre   | Présentation + Rapport              | ⏳ À venir  |
