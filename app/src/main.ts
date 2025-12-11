import './style.css'
import { getElement } from '@protolabo/zendom';
import { activateEditor } from './gentleman/index.js';
import MODEL from './model/concept_lv0.json';
import PROJECTION from './model/projection.json';

import { LLM_API } from './llm/import_functions.js'
import { uploadFile, analyze } from './api.js'
import FUNCTIONS_DATA from '../../documents/results/repertoire_parser_func_concepts_2.json'; // MODIFY THIS

// const CodeForm = getElement('#codeForm') as HTMLFormElement;
// const fileNames =  []
// CodeForm.addEventListener('change', (event) => {
//   const input = event.target as HTMLInputElement;
//   if (input.files) {
//     const files = Array.from(input.files);
//     files.forEach(file => {
//       const reader = new FileReader();
//       reader.onload = (e) => {
//         const content = e.target?.result;
//         console.log(`File Name: ${file.name}`);
//         console.log('Content:', content);
//       };
//       reader.readAsText(file);
//     });
//   }
// });

const app = getElement('#app')!;
const btnUpload = getElement('#btnUpload')!;
const btnAnalyze = getElement('#btnAnalyze')!;


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

let folderName: string;

btnUpload.addEventListener("click", (event) => {
  const filepath = "/code/fichier_test.py"

  uploadFile({
    filepath: filepath,
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
    `
  }).then(name =>{
    folderName = name
  })
    .catch(console.error)
})

btnAnalyze.addEventListener("click", (event) => {
  const filePath = "/"+folderName+"/fichier_test.py"
  const token = "" // get from .env
  analyze({
    filepath: filePath,
    token
  }).then(json => {
    let instance = editor.createInstance("file");
    LLM_API.fetchFunctions(json, editor, instance.concept)
  }).catch(console.error)
})


function test() {
  let instance = editor.createInstance("file");
  console.log(FUNCTIONS_DATA);
  LLM_API.fetchFunctions(FUNCTIONS_DATA, editor, instance.concept);
}

test();