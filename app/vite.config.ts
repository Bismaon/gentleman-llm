import { defineConfig } from 'vite';
import path from "path";

export default {
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
            "@gentleman": path.resolve(__dirname, "./src/gentleman"),
            "@generator": path.resolve(__dirname, "./src/gentleman/generator"),
            "@editor": path.resolve(__dirname, "./src/gentleman/editor"),
            "@model": path.resolve(__dirname, "./src/gentleman/model"),
            '@concept': path.resolve(__dirname, 'src/gentleman/model/concept'),
            '@structure': path.resolve(__dirname, 'src/gentleman/model/structure'),
            "@projection": path.resolve(__dirname, "./src/gentleman/projection"),
            '@field': path.resolve(__dirname, 'src/gentleman/projection/field'),
            '@layout': path.resolve(__dirname, 'src/gentleman/projection/layout'),
            '@static': path.resolve(__dirname, 'src/gentleman/projection/static'),
            '@exception': path.resolve(__dirname, 'src/gentleman/exception'),
            "@css": path.resolve(__dirname, "./src/css"),
            "@utils": path.resolve(__dirname, "./src/utils"),
            "@data": path.resolve(__dirname, "./data"),
        },
    },
};
