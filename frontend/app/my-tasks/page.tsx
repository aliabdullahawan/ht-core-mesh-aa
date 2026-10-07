"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { apiFetch, formatDate, MyTask } from "@/lib/api";

export default function MyTasksPage() {
  return (
    <Shell roles={["AGENT"]}>
      <MyTasks />
    </Shell>
  );
}

function MyTasks() {
  const [tasks, setTasks] = useState<MyTask[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<MyTask[]>("/tasks/mine").then(setTasks).catch(() => setError("Could not load your tasks."));
  }, []);

  return (
    <>
      <div className="page-head">
        <h1>My Tasks</h1>
      </div>
      {error && <div className="alert error">{error}</div>}
      {!tasks && !error && <p className="muted">Loading…</p>}
      {tasks?.length === 0 && <div className="card empty">No tasks assigned to you yet.</div>}
      {tasks && tasks.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Task</th>
                <th>Description</th>
                <th>Project</th>
                <th>Manager</th>
                <th>Deadline</th>
                <th className="num">Est. hours</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((t) => (
                <tr key={t.id}>
                  <td><strong>{t.title}</strong></td>
                  <td>{t.description}</td>
                  <td className="nowrap">
                    <Link href={`/projects/${t.project.id}`} style={{ textDecoration: "underline" }}>
                      {t.project.name}
                    </Link>
                  </td>
                  <td className="nowrap">{t.project.managerName}</td>
                  <td className="nowrap">{formatDate(t.deadline)}</td>
                  <td className="num">{t.estimatedHours}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
