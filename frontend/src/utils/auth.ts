const CURRENT_KEY = "app_current_user";
const USERS_KEY = "app_users_list";

export type User = { username: string; role: string };

// 初始化一些默认用户以便测试
function initDefaultUsers() {
  const existingUsers = localStorage.getItem(USERS_KEY);
  let users: any[] = [];

  if (existingUsers) {
    try {
      users = JSON.parse(existingUsers);
    } catch (e) {
      users = [];
    }
  }

  // 定义默认用户
  const defaultUsers = [
    { username: "admin", password: "123456", role: "institution" },
    { username: "caregiver1", password: "123456", role: "caregiver" },
    { username: "gov", password: "123456", role: "regulatory" },
  ];

  // 检查每个默认用户是否存在，不存在则添加
  let hasChanges = false;
  defaultUsers.forEach((defaultUser) => {
    const exists = users.some((u) => u.username === defaultUser.username);
    if (!exists) {
      users.push(defaultUser);
      hasChanges = true;
    }
  });

  // 如果有新增用户，保存到 localStorage
  if (hasChanges || !existingUsers) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
  }
}
initDefaultUsers();

export async function login(
  username: string,
  password: string,
): Promise<boolean> {
  try {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || "[]");
    const user = users.find(
      (u: any) => u.username === username && u.password === password,
    );

    if (user) {
      const { password: _, ...userInfo } = user;
      localStorage.setItem(CURRENT_KEY, JSON.stringify(userInfo));
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
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || "[]");

    // 检查用户名是否已存在
    if (users.some((u: any) => u.username === username)) {
      return false;
    }

    const newUser = { username, password, role };
    users.push(newUser);
    localStorage.setItem(USERS_KEY, JSON.stringify(users));

    // 注册后自动登录
    const { password: _, ...userInfo } = newUser;
    localStorage.setItem(CURRENT_KEY, JSON.stringify(userInfo));

    return true;
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
