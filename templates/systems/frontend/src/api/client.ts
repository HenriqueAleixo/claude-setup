import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:{{BACKEND_PORT}}/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  timeout: 15000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // TODO: mapear erros HTTP para mensagens amigáveis
    return Promise.reject(error);
  },
);
