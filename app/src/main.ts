import './style.css'
import { getElement } from '@protolabo/zendom';
import { activateEditor } from './gentleman/index.js';
import MODEL from './model/concept_lv0.json';
import PROJECTION from './model/projection.json';

const app = getElement('#app')!;

app.innerHTML = `
  <div>
    <h1>Gentleman Code</h1>
    <div data-gentleman="editor"></div>
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

editor.createInstance("file");