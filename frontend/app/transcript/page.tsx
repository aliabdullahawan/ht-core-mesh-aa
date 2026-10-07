"use client";

import Link from "next/link";
import { useState } from "react";
import Shell from "@/components/Shell";
import { ApiError, apiFetch } from "@/lib/api";

type Created = { projects: { id: string; name: string; taskCount: number }[] };

export default function TranscriptPage() {
  return (
    <Shell roles={["ADMIN"]}>
      <TranscriptForm />
    </Shell>
  );
}

function TranscriptForm() {
  const [transcript, setTranscript] = useState("");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [result, setResult] = useState<Created | null>(null);

  async function submit() {
    if (!transcript.trim() || loading) return;
    setLoading(true);
    setErrors([]);
    setResult(null);
    try {
      setResult(await apiFetch<Created>("/transcript", { method: "POST", body: JSON.stringify({ transcript }) }));
    } catch (e) {
      if (e instanceof ApiError && e.status === 422 && Array.isArray(e.body?.errors)) setErrors(e.body.errors);
      else if (e instanceof ApiError && e.status === 403) setErrors(["Only the admin can create projects from a transcript."]);
      else if (e instanceof ApiError && typeof e.body?.detail === "string")
        setErrors([`AI service failed, please try again. (${e.body.detail})`]);
      else setErrors(["AI service failed, please try again."]);
    } finally {
      setLoading(false);
    }
  }

  async function loadSample() {
    const res = await fetch("/sample-transcript.txt");
    setTranscript(await res.text());
  }

  const taskTotal = result?.projects.reduce((s, p) => s + p.taskCount, 0) ?? 0;

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Create from Transcript</h1>
          <p className="muted small">
            Paste a meeting transcript. AI creates the projects and tasks using the team directory, then saves them.
          </p>
        </div>
      </div>

      {result && (
        <div className="alert ok">
          <strong>
            Created {result.projects.length} project{result.projects.length === 1 ? "" : "s"} and {taskTotal} task
            {taskTotal === 1 ? "" : "s"}
          </strong>
          <ul>
            {result.projects.map((p) => (
              <li key={p.id}>
                <Link href={`/projects/${p.id}`} style={{ textDecoration: "underline" }}>
                  {p.name}
                </Link>{" "}
                ({p.taskCount} tasks)
              </li>
            ))}
          </ul>
        </div>
      )}

      {errors.length > 0 && (
        <div className="alert error">
          <strong>Nothing was saved. Please correct the transcript and try again:</strong>
          <ul>
            {errors.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      <textarea
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
        placeholder="Paste the meeting transcript here…"
        disabled={loading}
      />
      <div className="row">
        <button className="btn" onClick={submit} disabled={loading || !transcript.trim()}>
          {loading ? "AI is reading the meeting…" : "Create from Transcript"}
        </button>
        {!loading && (
          <button className="linkbtn small" onClick={loadSample}>
            Load sample transcript
          </button>
        )}
        {loading && <span className="muted small">This can take up to a minute.</span>}
      </div>
    </>
  );
}
