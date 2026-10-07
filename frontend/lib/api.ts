export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Role = "ADMIN" | "MANAGER" | "AGENT";
export type SessionUser = { id: string; name: string; role: Role };

export type Project = {
  id: string;
  name: string;
  clientName: string;
  description: string;
  deadline: string;
  manager: { id: string; name: string };
  taskCount: number;
};
export type Task = {
  id: string;
  title: string;
  description: string;
  deadline: string;
  estimatedHours: number;
  assignee: { id: string; name: string };
};
export type ProjectDetail = Project & { tasks: Task[] };
export type MyTask = Omit<Task, "assignee"> & { project: { id: string; name: string; managerName: string } };
export type User = { id: string; name: string; role: Role; specialization: string; skills: string[] };

export class ApiError extends Error {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  constructor(public status: number, public body: any) {
    super(typeof body?.detail === "string" ? body.detail : `Request failed (${status})`);
  }
}

export function getSession(): SessionUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("user");
    return raw && localStorage.getItem("token") ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveSession(token: string, user: SessionUser) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

export function homeFor(role: Role) {
  return role === "AGENT" ? "/my-tasks" : "/projects";
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const body = await res.json().catch(() => null);
  if (res.status === 401 && path !== "/auth/login") {
    clearSession();
    window.location.href = "/login";
  }
  if (!res.ok) throw new ApiError(res.status, body);
  return body as T;
}

export function formatDate(iso: string) {
  return new Date(iso + "T00:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}
