import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
    root: path.resolve(__dirname, 'frontend/react-app'),
    plugins: [react(), tailwindcss()],
    build: {
        outDir: path.resolve(__dirname, 'frontend/react-app/dist'),
        emptyOutDir: true,
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'frontend/react-app/src'),
        },
    },
})
