-- IARS V4.5.20 — Full Yearly Audit Gantt setup
-- Use for a fresh installation. Existing V4.5.19 users should run
-- SUPABASE_GANTT_V4_5_20_WORKFLOW_MIGRATION.sql instead.

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
    constraint iars_gantt_master_unique_record
        unique (company_department, custodian, audit_task, accountability)
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
    initial_report_submitted_at date,
    final_report_submitted_at date,
    initial_report_reference text not null default '',
    final_report_reference text not null default '',
    remarks text not null default '',
    created_by text not null default '',
    updated_by text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint iars_gantt_schedule_unique_month
        unique (master_id, schedule_year, schedule_month),
    constraint iars_gantt_done_requires_date check (
        status <> 'Done' or accomplished_date is not null
    ),
    constraint iars_gantt_frs_requires_irs check (
        final_report_submitted_at is null or initial_report_submitted_at is not null
    )
);

create table if not exists public.iars_gantt_holiday (
    id uuid primary key default gen_random_uuid(),
    holiday_date date not null,
    holiday_name text not null,
    coverage text not null
        check (coverage in ('National', 'Province of Rizal', 'San Mateo, Rizal')),
    holiday_type text not null
        check (holiday_type in ('Regular', 'Special Non-Working', 'Local Special Non-Working', 'Special Working')),
    source_reference text not null default '',
    active boolean not null default true,
    created_by text not null default '',
    updated_by text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint iars_gantt_holiday_unique_date_coverage unique (holiday_date, coverage)
);

create index if not exists iars_gantt_master_custodian_idx
    on public.iars_gantt_master (custodian);
create index if not exists iars_gantt_schedule_year_idx
    on public.iars_gantt_schedule (schedule_year);
create index if not exists iars_gantt_schedule_auditor_idx
    on public.iars_gantt_schedule (lower(auditor_full_name));
create index if not exists iars_gantt_schedule_status_idx
    on public.iars_gantt_schedule (status);
create index if not exists iars_gantt_schedule_irs_idx
    on public.iars_gantt_schedule (initial_report_submitted_at);
create index if not exists iars_gantt_schedule_frs_idx
    on public.iars_gantt_schedule (final_report_submitted_at);
create index if not exists iars_gantt_holiday_date_idx
    on public.iars_gantt_holiday (holiday_date);
create index if not exists iars_gantt_holiday_active_idx
    on public.iars_gantt_holiday (active);

alter table public.iars_gantt_master enable row level security;
alter table public.iars_gantt_schedule enable row level security;
alter table public.iars_gantt_holiday enable row level security;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.iars_gantt_master to service_role;
grant select, insert, update, delete on table public.iars_gantt_schedule to service_role;
grant select, insert, update, delete on table public.iars_gantt_holiday to service_role;

notify pgrst, 'reload schema';
