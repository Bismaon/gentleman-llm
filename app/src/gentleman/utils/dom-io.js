import { h } from '@protolabo/zendom';

/**
     * Creates a bold text
     * @param {string} text 
     * @returns {string}
     */
export const _b = (text) => {
    /** @type {HTMLElement} */
    let element = h("strong", {
        class: ["text-bf"],
    }, text);

    return element.outerHTML;
};

/**
 * Creates an italic text
 * @param {string} text 
 * @returns {string}
 */
export const _i = (text) => {
    /** @type {HTMLElement} */
    let element = h("em", {
        class: ["text-it"],
    }, text);

    return element.outerHTML;
};
