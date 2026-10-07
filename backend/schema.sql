-- Run once in the Supabase SQL editor, or: python seed.py --schema
create table if not exists users (
  id text primary key,                       -- ADMIN, PM01, DEV01 ...
  name text not null,
  email text not null unique,
  password_hash text not null,
  role text not null check (role in ('ADMIN','MANAGER','AGENT')),
  specialization text,
  skills text[] default '{}'
);

create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  client_name text not null,
  description text default '',
  manager_id text not null references users(id),
  deadline date not null,
  created_at timestamptz default now()
);

create table if not exists tasks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  title text not null,
  description text default '',
  assignee_id text not null references users(id),
  deadline date not null,
  estimated_hours numeric not null check (estimated_hours > 0)
);

create index if not exists tasks_project_idx on tasks(project_id);
create index if not exists tasks_assignee_idx on tasks(assignee_id);
create index if not exists projects_manager_idx on projects(manager_id);
