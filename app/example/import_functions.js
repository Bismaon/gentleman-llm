const FUNCTIONS_DATA = require('../../documents/results/annuaire_parser_func_concepts_2.json');

export const API = {
    fetchFunctions(editor, fileConcept) {
        const functionsSet = fileConcept.getAttribute("functions").getTarget();
        functionsSet.removeAllElement();

        FUNCTIONS_DATA.forEach(entry => {
            if (entry.file) {
                fileConcept.getAttribute("name").setValue(entry.file);
                return;
            }

            // FUNCTION
            let fn = editor.createConcept("function");
            fn.getAttribute("name").setValue(entry.name);
            fn.getAttribute("description").setValue(entry.description || "");
            fn.getAttribute("category").setValue(entry.category || "");

            // RETURN
            let returnConcept = editor.createConcept("return_c");
            returnConcept.getAttribute("name").setValue(entry.return?.[0] || "");
            returnConcept.getAttribute("type").setValue(entry.return?.[1] || "");
            fn.getAttribute("return").setTarget(returnConcept);

            // PARAMETERS
            const paramsSet = fn.getAttribute("parameters").getTarget();
            (entry.parameters || []).forEach(([pName, pType]) => {
                let param = editor.createConcept("param_c");
                param.getAttribute("name").setValue(pName);
                param.getAttribute("type").setValue(pType);
                paramsSet.addElement(param);
            });

            // SOURCE
            let src = editor.createConcept("source_c");
            src.getAttribute("code").setValue(entry.source);
            src.getAttribute("start_line").setValue(entry.start_line);
            src.getAttribute("end_line").setValue(entry.end_line);
            fn.getAttribute("source").setTarget(src);

            // TAGS
            let tags = fn.getAttribute("tags").getTarget();
            (entry.tags || []).forEach(tag => tags.addElement(tag));

            // CALLS
            let calls = fn.getAttribute("calls").getTarget();
            (entry.calls || []).forEach(c => calls.addElement(c));

            // CALLED BY
            let calledBy = fn.getAttribute("called_by").getTarget();
            (entry.called_by || []).forEach(cb => calledBy.addElement(cb));

            // ADD TO FILE
            functionsSet.addElement(fn);
        });
    }
};