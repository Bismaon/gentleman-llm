# Études préliminaires

## Analyse du problème

- Il faut pouvoir, à partir d'un fichier ou d'une liste de fichiers de code, définir les fonctions dans chaque fichier, déterminer leurs caractéristiques, et toute information qui peut être utile et être utilisée dans Gentleman. Ceci en faisant appel à une LLM pour définir certaines parties des fonctions qui ne sont pas explicitement écrites.

## Exigences

- La LLM doit pouvoir définir d'une fonction, les types des paramètres, le type du retour, sa catégorie, les appels qu'elle fait et qui l'appelle, sa description, et enfin des tags visant à définir la fonction en mots-clés pour un référencement.

## Recherche de solutions

- Une première solution a été d'utiliser tout le fichier et de demander au LLM de définir toutes les fonctions d'un coup, mais ceci s'est avéré trop compliqué pour l'intelligence du modèle utilisé, et instable entre chaque run, rendant son utilisation dure puisque les réponses du modèle ne sont pas passable.
- Une autre solution, qui a été celle adoptée par nous, est de définir les fonctions une à la fois, et de faire la même chose lors de l'extraction d'information par le modèle. Ceci permet de valider les réponses à chaque étape et donne un plus grand contrôle sur les réponses possibles du modèle.

## Méthodologie

- Utilisation d'une approche itérative, où on construit le code, et l'on modifie au fur et à mesure les différents aspects jusqu'à obtenir le résultat voulu. Cette approche a semblèrent marché même si, pour les prompts lors de la première solution, cette approche a été peu fructueuse dans les résultats. Cependant, une fois l'autre solution trouvée, le rendu fut presque complet, hormis le manque de profondeur/abstraction possible, qui n'ont pas été essayés par manque de temps.
