const USERS_KEY = "app_users";
const CURRENT_KEY = "app_current_user";

type User = { username: string; password: string };

const defaultUsers: User[] = [
  { username: "admin", password: "123456" },
  { username: "backup1", password: "111111" },
  { username: "backup2", password: "222222" },
  { username: "backup3", password: "333333" },
];

function initDefaultUsers() {
  const raw = localStorage.getItem(USERS_KEY);
  if (!raw) {
    localStorage.setItem(USERS_KEY, JSON.stringify(defaultUsers));
  }
}

export function getUsers(): User[] {
  initDefaultUsers();
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY) || "[]");
  } catch (e) {
    return [];
  }
}

export function saveUsers(users: User[]) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export function login(username: string, password: string) {
  const users = getUsers();
  const found = users.find(
    (u) => u.username === username && u.password === password,
  );
  if (found) {
    localStorage.setItem(CURRENT_KEY, JSON.stringify({ username }));
    return true;
  }
  return false;
}

export function register(username: string, password: string) {
  const users = getUsers();
  if (users.find((u) => u.username === username)) return false;
  users.push({ username, password });
  saveUsers(users);
  localStorage.setItem(CURRENT_KEY, JSON.stringify({ username }));
  return true;
}

export function logout() {
  localStorage.removeItem(CURRENT_KEY);
}

export function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem(CURRENT_KEY) || "null");
  } catch (e) {
    return null;
  }
}

export function isAuthenticated() {
  return !!getCurrentUser();
}

export default {
  getUsers,
  saveUsers,
  login,
  register,
  logout,
  getCurrentUser,
  isAuthenticated,
};
