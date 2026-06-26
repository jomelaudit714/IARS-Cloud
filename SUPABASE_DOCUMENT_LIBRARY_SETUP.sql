-- IARS v4.0.0 - Report Templates and Policies & Memoranda document library
-- Run once in the same Supabase project used by IARS.

create extension if not exists pgcrypto;

insert into storage.buckets (id, name, public)
values ('iars-document-library', 'iars-document-library', false)
on conflict (id) do nothing;

create table if not exists public.document_library (
    id uuid primary key default gen_random_uuid(),
    collection text not null check (collection in ('Report Templates', 'Policies & Memoranda')),
    title text not null,
    category text not null default 'General',
    description text not null default '',
    version_label text not null default '',
    effective_date date,
    original_filename text not null,
    storage_bucket text not null default 'iars-document-library',
    storage_path text not null unique,
    mime_type text not null default 'application/octet-stream',
    file_extension text not null,
    uploaded_by text not null default '',
    file_size bigint not null default 0,
    sha256 text not null,
    status text not null default 'Active' check (status in ('Active', 'Archived')),
    uploaded_at timestamptz not null default now()
);

create index if not exists document_library_collection_idx
    on public.document_library (collection);
create index if not exists document_library_category_idx
    on public.document_library (category);
create index if not exists document_library_uploaded_at_idx
    on public.document_library (uploaded_at desc);
create index if not exists document_library_sha256_idx
    on public.document_library (sha256);

alter table public.document_library enable row level security;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.document_library to service_role;
