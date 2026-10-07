"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { ApiError, apiFetch, formatDate, getSession, ProjectDetail } from "@/lib/api";

export default function ProjectDetailPage() {
  return (
    <Shell>
      <Detail />
    </Shell>
  );
}

function Detail() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [error, setError] = useState("");
  const isAgent = getSession()?.role === "AGENT";

  useEffect(() => {
    apiFetch<ProjectDetail>(`/projects/${id}`)
      .then(setProject)
      .catch((e) =>
        setError(e instanceof ApiError && e.status === 404 ? "Project not found or you don't have access." : "Could not load project.")
      );
  }, [id]);

  if (error)
    return (
      <>
        <div className="alert error">{error}</div>
        <Link href="/projects" className="linkbtn">← Back to projects</Link>
      </>
    );
  if (!project) return <p className="muted">Loading…</p>;

  const totalHours = project.tasks.reduce((s, t) => s + t.estimatedHours, 0);

  return (
    <>
      <Link href="/projects" className="muted small">← Projects</Link>
      <div className="page-head" style={{ marginTop: 8 }}>
        <div>
          <h1>{project.name}</h1>
          <p className="muted">{project.clientName}</p>
        </div>
      </div>
      <div className="card" style={{ marginBottom: 20 }}>
        <dl className="meta" style={{ marginTop: 0 }}>
          <dt>Client</dt>
          <dd>{project.clientName}</dd>
          <dt>Manager</dt>
          <dd>{project.manager.name}</dd>
          <dt>Deadline</dt>
          <dd>{formatDate(project.deadline)}</dd>
          <dt>Description</dt>
          <dd>{project.description || <span className="muted">—</span>}</dd>
        </dl>
      </div>
      <h2 style={{ fontSize: 18, marginBottom: 10 }}>
        {isAgent ? "My tasks in this project" : "Tasks"}{" "}
        <span className="muted small">
          ({project.tasks.length} tasks · {totalHours} h)
        </span>
      </h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Task</th>
              <th>Description</th>
              <th>Assigned to</th>
              <th>Deadline</th>
              <th className="num">Est. hours</th>
            </tr>
          </thead>
          <tbody>
            {project.tasks.map((t) => (
              <tr key={t.id}>
                <td><strong>{t.title}</strong></td>
                <td>{t.description}</td>
                <td className="nowrap">{t.assignee.name}</td>
                <td className="nowrap">{formatDate(t.deadline)}</td>
                <td className="num">{t.estimatedHours}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
