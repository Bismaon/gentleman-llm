import './style.css'
import { getElement } from '@protolabo/zendom';
import { activateEditor } from './gentleman/index.js';
import MODEL from './model/concept_lv0.json';
import PROJECTION from './model/projection.json';

import { API } from './../example/import_functions.js'

const CodeForm = getElement('#codeForm') as HTMLFormElement;
const fileNames =  []
CodeForm.addEventListener('change', (event) => {
  const input = event.target as HTMLInputElement;
  if (input.files) {
    const files = Array.from(input.files);
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result;
        console.log(`File Name: ${file.name}`);
        console.log('Content:', content);
      };
      reader.readAsText(file);
    });
  }
});

const app = getElement('#app')!;

app.innerHTML = `
  <div>
    <h1>Gentleman Code</h1>
    <div data-gentleman="editor"></div>
    <div class="query-container"></div>
  </div>
`

// let editor = activateEditor(app)[0];

// editor.init({
//   config: {
//     header: false,
//   },
//   conceptModel: MODEL,
//   projectionModel: PROJECTION
// });

// let instance = editor.createInstance("file");
// API.fetchFunctions(editor, instance.concept)
// console.log(instance.concept);
