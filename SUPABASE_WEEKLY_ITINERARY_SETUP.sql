-- IARS Weekly Itinerary setup — V4.4.73
-- Run this once in the Supabase SQL Editor used by the IARS application.

create extension if not exists pgcrypto;

insert into storage.buckets (
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types
)
values (
    'iars-weekly-itineraries',
    'iars-weekly-itineraries',
    false,
    10485760,
    array['image/jpeg', 'image/png']
)
on conflict (id) do update set
    public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;

create table if not exists public.weekly_itineraries (
    id uuid primary key default gen_random_uuid(),
    owner_key text not null,
    auditor_name text not null,
    submitted_by_username text not null default '',
    week_start date not null,
    week_end date not null,
    original_filename text not null,
    storage_bucket text not null default 'iars-weekly-itineraries',
    storage_path text not null unique,
    mime_type text not null check (mime_type in ('image/jpeg', 'image/png')),
    file_size bigint not null default 0 check (file_size >= 0),
    sha256 text not null default '',
    status text not null default 'pending'
        check (status in ('pending', 'approved', 'returned')),
    revision_no integer not null default 1 check (revision_no >= 1),
    submitter_remarks text not null default '',
    admin_remarks text not null default '',
    submitted_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    approved_by text,
    approved_at timestamptz,
    constraint weekly_itineraries_owner_week_revision_unique
        unique (owner_key, week_start, revision_no),
    constraint weekly_itineraries_week_order_check check (week_end >= week_start)
);

create index if not exists weekly_itineraries_owner_idx
    on public.weekly_itineraries (owner_key, week_start desc, revision_no desc);

create index if not exists weekly_itineraries_status_idx
    on public.weekly_itineraries (status, week_start desc);

create index if not exists weekly_itineraries_auditor_idx
    on public.weekly_itineraries (lower(auditor_name), week_start desc);

alter table public.weekly_itineraries enable row level security;

-- IARS uses the Supabase service-role key from Streamlit Secrets.
-- No public/authenticated policies are created. The service role bypasses RLS,
-- while the application enforces auditor-only and administrator-only views.

comment on table public.weekly_itineraries is
    'Private JPG/PNG weekly itinerary submissions with administrator approval and revision history.';
