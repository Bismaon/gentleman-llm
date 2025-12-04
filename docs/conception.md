# Conception

## Architecture

- On a une classe Gentleman LLM qui contient la partie qui va analyser les fichiers et définir les fonctions.
- Un fichier gentleman request qui est l'API gentleman LLM qui recevra les fichiers de l'utilisateur, ainsi que les requêtes pour analyser ces fichiers.

## Choix technologiques

- On utilise Python et le module AST pour parcourir le contenu des fichiers et pour le parser. Ceci a été fait pour la simplicité d'usage qui vient avec Python pour faire des requêtes vers des LLMs. De plus, l'idée ici était plutôt de montrer la possibilité d'utiliser des LLMs pour Gentleman, on cherchait simplement à faire un fichier dans le format d'un concept Gentleman.

## Prototype

- Voici un exemple d'appel de l'API et un résultat envisageable:

Upload du fichier vers Gentleman

=== "Python"
    ```python
    resp = requests.post(
        "http://127.0.0.1:8000/upload",
        json={
            "filename": "list_files.py",
            "content": '''def list_files(directory: str) -> list[str]:\n    \"\"\"Lists all files in a given directory.\n\n    Args:\n        directory (str): The name of the directory\n\n    Returns:\n        list[str]: Lists of all file names in a directory.\n    \"\"\"\n\n    try:\n        return [\n            f\n            for f in os.listdir(directory)\n            if os.path.isfile(os.path.join(directory, f))\n        ]\n    except FileNotFoundError:\n        print(f\"Directory not found: {directory}\")\n        return []\n    except Exception as e:\n        print(f\"Error listing files in {directory}: {e}\")\n        return []''',
        },
    )
    ```

Analyse du fichier par GentlemanLLM

=== "Python"
    ```python
    resp = requests.post(
        "http://127.0.0.1:8000/analyze",
        json={
            "filepath": "list_files.py",
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "hf_token": hf_token,
        },
    )
    ```

Resultat possible

=== "JSON"
    ```json
    [
        {
            "file": "temp.py"
        },
        {
            "name": "list_files",
            "parameters": [
                [
                    "directory",
                    "str"
                ]
            ],
            "source": "def list_files(directory: str) -> list[str]:\n    \"\"\"Lists all files in a given directory.\n\n    Args:\n        directory (str): The name of the directory\n\n    Returns:\n        list[str]: Lists of all file names in a directory.\n    \"\"\"\n\n    try:\n        return [\n            f\n            for f in os.listdir(directory)\n            if os.path.isfile(os.path.join(directory, f))\n        ]\n    except FileNotFoundError:\n        print(f\"Directory not found: {directory}\")\n        return []\n    except Exception as e:\n        print(f\"Error listing files in {directory}: {e}\")\n        return []",
            "start_line": 3,
            "end_line": 24,
            "called_by": [],
            "calls": [],
            "description": "\"Lists all files in a given directory, handling exceptions.\"",
            "tags": [
                "file_management",
                "directory_scanning",
                "os_interaction",
                "file_listing",
                "filesystem"
            ],
            "category": "ExternalInteraction",
            "return": [
                "[f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]",
                "list"
            ]
        }
    ]
    ```