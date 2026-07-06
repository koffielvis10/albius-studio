import axios from "axios"

// URL du backend. En dev : http://127.0.0.1:8000 (valeur par défaut).
// En production : définie via la variable d'env VITE_API_URL (build Vercel).
export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

const api = axios.create({ baseURL: API_URL })

export default api
