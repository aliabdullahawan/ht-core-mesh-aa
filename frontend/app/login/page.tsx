"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { ApiError, apiFetch, getSession, homeFor, saveSession, SessionUser } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const u = getSession();
    if (u) router.replace(homeFor(u.role));
  }, [router]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await apiFetch<{ token: string; user: SessionUser }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      saveSession(res.token, res.user);
      router.replace(homeFor(res.user.role));
    } catch (err) {
      setError(err instanceof ApiError && err.status === 401 ? "Invalid email or password" : "Cannot reach the server, please try again.");
      setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      <form className="card login" onSubmit={submit}>
        <h1>NovaWorks PM</h1>
        <p className="muted small">AI Project Manager: meeting to execution</p>
        {error && <div className="alert error">{error}</div>}
        <label htmlFor="email">Email</label>
        <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        <div className="row">
          <button className="btn" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </div>
        <p className="muted small" style={{ marginTop: 14 }}>
          Demo: admin@novaworks.example / Demo123!
        </p>
      </form>
    </div>
  );
}
