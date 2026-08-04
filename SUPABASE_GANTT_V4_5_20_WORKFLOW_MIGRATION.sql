-- IARS V4.5.20 — Clickable Gantt + IRS/FRS workflow migration
-- Run once in the same Supabase project used by IARS V4.5.19.

begin;

alter table public.iars_gantt_schedule
    add column if not exists initial_report_submitted_at date,
    add column if not exists final_report_submitted_at date,
    add column if not exists initial_report_reference text not null default '',
    add column if not exists final_report_reference text not null default '';

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

create index if not exists iars_gantt_holiday_date_idx
    on public.iars_gantt_holiday (holiday_date);
create index if not exists iars_gantt_holiday_active_idx
    on public.iars_gantt_holiday (active);
create index if not exists iars_gantt_schedule_irs_idx
    on public.iars_gantt_schedule (initial_report_submitted_at);
create index if not exists iars_gantt_schedule_frs_idx
    on public.iars_gantt_schedule (final_report_submitted_at);

alter table public.iars_gantt_holiday enable row level security;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.iars_gantt_master to service_role;
grant select, insert, update, delete on table public.iars_gantt_schedule to service_role;
grant select, insert, update, delete on table public.iars_gantt_holiday to service_role;

commit;

-- Refresh the PostgREST schema cache after adding the new columns/table.
notify pgrst, 'reload schema';
