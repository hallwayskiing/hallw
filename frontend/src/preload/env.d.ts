/// <reference types="vite/client" />

interface ElectronAPI {
    process: {
        versions: {
            electron: string
            chrome: string
            node: string
            [key: string]: string
        }
    }
}

interface Window {
    electron: ElectronAPI
    api: unknown
}
