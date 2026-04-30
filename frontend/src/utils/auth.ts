import api from "./http";

const CURRENT_KEY = "app_current_user";

export type User = { username: string; role: string };

export async function login(
  username: string,
  password: string,
): Promise<boolean> {
  try {
    const response = await api.post(`/api/auth/login`, {
      username,
      password,
    });
    if (response.data.user) {
      localStorage.setItem(CURRENT_KEY, JSON.stringify(response.data.user));
      return true;
    }
    return false;
  } catch (error) {
    console.error("Login failed:", error);
    return false;
  }
}

export async function register(
  username: string,
  password: string,
  role: string = "caregiver",
): Promise<boolean> {
  try {
    const response = await api.post(`/api/auth/register`, {
      username,
      password,
      role,
    });
    if (response.data.user) {
      localStorage.setItem(CURRENT_KEY, JSON.stringify(response.data.user));
      return true;
    }
    return false;
  } catch (error) {
    console.error("Registration failed:", error);
    return false;
  }
}

export function logout() {
  localStorage.removeItem(CURRENT_KEY);
}

export function getCurrentUser(): User | null {
  try {
    return JSON.parse(localStorage.getItem(CURRENT_KEY) || "null");
  } catch (e) {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return !!getCurrentUser();
}

export function hasRole(role: string): boolean {
  const user = getCurrentUser();
  return user?.role === role;
}

export default {
  login,
  register,
  logout,
  getCurrentUser,
  isAuthenticated,
  hasRole,
};
