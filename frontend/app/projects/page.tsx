"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { apiFetch, formatDate, getSession, Project } from "@/lib/api";

export default function ProjectsPage() {
  return (
    <Shell>
      <ProjectList />
    </Shell>
  );
}

function ProjectList() {
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [error, setError] = useState("");
  const user = getSession();

  useEffect(() => {
    apiFetch<Project[]>("/projects").then(setProjects).catch(() => setError("Could not load projects."));
  }, []);

  const title = user?.role === "ADMIN" ? "All projects" : user?.role === "MANAGER" ? "My projects" : "My related projects";

  return (
    <>
      <div className="page-head">
        <h1>{title}</h1>
        {user?.role === "ADMIN" && (
          <Link href="/transcript" className="btn">
            Create from Transcript
          </Link>
        )}
      </div>
      {error && <div className="alert error">{error}</div>}
      {!projects && !error && <p className="muted">Loading…</p>}
      {projects?.length === 0 && (
        <div className="card empty">
          No projects yet.
          {user?.role === "ADMIN" && " Paste a meeting transcript to create them."}
        </div>
      )}
      <div className="grid">
        {projects?.map((p) => (
          <Link key={p.id} href={`/projects/${p.id}`} className="card">
            <h3>{p.name}</h3>
            <p className="muted small">{p.clientName}</p>
            <dl className="meta">
              <dt>Manager</dt>
              <dd>{p.manager.name}</dd>
              <dt>Deadline</dt>
              <dd>{formatDate(p.deadline)}</dd>
              <dt>{user?.role === "AGENT" ? "My tasks" : "Tasks"}</dt>
              <dd>{p.taskCount}</dd>
            </dl>
          </Link>
        ))}
      </div>
    </>
  );
}
