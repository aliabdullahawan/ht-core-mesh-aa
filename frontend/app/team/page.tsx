"use client";

import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { apiFetch, User } from "@/lib/api";

export default function TeamPage() {
  return (
    <Shell>
      <Team />
    </Shell>
  );
}

function Team() {
  const [users, setUsers] = useState<User[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<User[]>("/users").then(setUsers).catch(() => setError("Could not load the team."));
  }, []);

  return (
    <>
      <div className="page-head">
        <h1>Team directory</h1>
      </div>
      {error && <div className="alert error">{error}</div>}
      {!users && !error && <p className="muted">Loading…</p>}
      {users && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Role</th>
                <th>Specialization</th>
                <th>Skills</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="muted">{u.id}</td>
                  <td><strong>{u.name}</strong></td>
                  <td><span className="badge">{u.role.toLowerCase()}</span></td>
                  <td>{u.specialization}</td>
                  <td className="muted">{u.skills?.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
