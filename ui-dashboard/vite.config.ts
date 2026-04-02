import { defineConfig } from "vite";
import { viteExternalsPlugin } from 'vite-plugin-externals';
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        react(),
        viteExternalsPlugin({
            GFN: 'GFN'
        }),
    ],
    // The optimizedDeps and build blocks are for development with the
    // local streaming library build only.
    optimizeDeps: {
        include: ['@nvidia/omniverse-webrtc-streaming-library'],
    },
    build: {
        commonjsOptions: {
            include: [/web-streaming-library/],
        },
    },
});
