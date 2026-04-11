import axios from "axios";

const baseURL = (import.meta.env.VITE_API_BASE as string) || "";

const api = axios.create({
  baseURL,
  timeout: 100000,
});

api.interceptors.response.use(
  (response) => ({
    data: response.data,
    status: response.status,
    headers: response.headers,
  }),
  (error) => Promise.reject(error?.response?.data || error.message || error),
);

export default api;
