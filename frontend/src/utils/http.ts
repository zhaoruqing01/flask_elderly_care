import axios from "axios";
import auth from "@/utils/auth";

const baseURL = (import.meta.env.VITE_API_BASE as string) || "";

const api = axios.create({
  baseURL,
  timeout: 100000,
});

// 请求拦截器：添加角色头
api.interceptors.request.use(
  (config) => {
    const user = auth.getCurrentUser();
    if (user && user.role) {
      config.headers["X-User-Role"] = user.role;
      // 同时也作为参数传递，增加兼容性
      if (config.method === 'get') {
        config.params = { ...config.params, role: user.role };
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => ({
    data: response.data,
    status: response.status,
    headers: response.headers,
  }),
  (error) => Promise.reject(error?.response?.data || error.message || error),
);

export default api;
