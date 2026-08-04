-- IARS V4.5.17 — Yearly Audit Gantt tables
-- Run this script once in the same Supabase project used by IARS.

create extension if not exists pgcrypto;

create table if not exists public.iars_gantt_master (
    id uuid primary key default gen_random_uuid(),
    company_department text not null,
    custodian text not null,
    audit_task text not null,
    accountability text not null default '',
    active boolean not null default true,
    created_by text not null default '',
    updated_by text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint iars_gantt_master_unique_record unique (company_department, custodian, audit_task)
);

create table if not exists public.iars_gantt_schedule (
    id uuid primary key default gen_random_uuid(),
    master_id uuid not null references public.iars_gantt_master(id) on delete cascade,
    schedule_year integer not null check (schedule_year between 2000 and 2200),
    schedule_month integer not null check (schedule_month between 1 and 12),
    auditor_full_name text not null,
    auditor_nickname text not null default '',
    status text not null default 'Planned'
        check (status in ('Planned', 'In Progress', 'Done', 'Overdue')),
    planned_date date,
    accomplished_date date,
    remarks text not null default '',
    created_by text not null default '',
    updated_by text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint iars_gantt_schedule_unique_month unique (master_id, schedule_year, schedule_month),
    constraint iars_gantt_done_requires_date check (
        status <> 'Done' or accomplished_date is not null
    )
);

create index if not exists iars_gantt_master_custodian_idx
    on public.iars_gantt_master (custodian);
create index if not exists iars_gantt_schedule_year_idx
    on public.iars_gantt_schedule (schedule_year);
create index if not exists iars_gantt_schedule_auditor_idx
    on public.iars_gantt_schedule (lower(auditor_full_name));
create index if not exists iars_gantt_schedule_status_idx
    on public.iars_gantt_schedule (status);

-- Existing V4.5.16 databases may still contain the old frequency column in
-- iars_gantt_master. It can remain safely. V4.5.17 ignores it and calculates
-- frequency from the number of Done audit schedules for each custodian/year.

alter table public.iars_gantt_master enable row level security;
alter table public.iars_gantt_schedule enable row level security;

-- IARS connects through the service-role key configured in Streamlit Secrets.
grant usage on schema public to service_role;
grant select, insert, update, delete on table public.iars_gantt_master to service_role;
grant select, insert, update, delete on table public.iars_gantt_schedule to service_role;
