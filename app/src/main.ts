import './style.css'
import { getElement } from '@protolabo/zendom';
import { activateEditor } from './gentleman/index.js';
import { analyze, uploadFile } from './api.js';
import MODEL from './model/concept_lv0.json';
import PROJECTION from './model/projection.json';

import { API } from './../example/import_functions.js'

uploadFile({
  filename: "fichier_test.py",
  content: `
  import os

def list_files(directory: str) -> list[str]:
    """Lists all files in a given directory.

    Args:
        directory (str): The name of the directory

    Returns:
        list[str]: Lists of all file names in a directory.
    """

    try:
        return [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return []
    except Exception as e:
        print(f"Error listing files in {directory}: {e}")
        return []
  `,
})
  .then(console.log)
  .catch(console.error);

const app = getElement('#app')!;
const btnAnalyze = getElement('#btnAnalyze')!;

btnAnalyze.addEventListener("click", (event) => {
  analyze({
    filename: "code/fichier_test.py",
    token: "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"
  })
    .then(json => {
      let instance = editor.createInstance("file");
      API.fetchFunctions(json, editor, instance.concept)
    })
    .catch(console.error)
})

app.innerHTML = `
  <div>
    <h1>Gentleman Code</h1>
    <div data-gentleman="editor"></div>
    <div class="query-container"></div>
  </div>
`

let editor = activateEditor(app)[0];

editor.init({
  config: {
    header: false,
  },
  conceptModel: MODEL,
  projectionModel: PROJECTION
});

