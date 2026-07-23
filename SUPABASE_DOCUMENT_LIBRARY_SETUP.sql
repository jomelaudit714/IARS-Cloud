-- IARS v4.4.79 - Document Library with Company Folders and Subject Categories
-- Use this script for a NEW Supabase document-library setup.
-- Existing installations should run SUPABASE_POLICY_SUBJECT_CATEGORY_MIGRATION.sql after the earlier folder migration.

create extension if not exists pgcrypto;

insert into storage.buckets (id, name, public)
values ('iars-document-library', 'iars-document-library', false)
on conflict (id) do nothing;

create table if not exists public.document_library_folders (
    id uuid primary key default gen_random_uuid(),
    collection text not null default 'Policies & Memoranda'
        check (collection in ('Report Templates', 'Policies & Memoranda')),
    folder_name text not null,
    description text not null default '',
    created_by text not null default '',
    status text not null default 'Active'
        check (status in ('Active', 'Archived')),
    created_at timestamptz not null default now()
);

create unique index if not exists document_library_folders_unique_active_name_idx
    on public.document_library_folders (collection, lower(folder_name))
    where status = 'Active';
create index if not exists document_library_folders_collection_idx
    on public.document_library_folders (collection);
create index if not exists document_library_folders_created_at_idx
    on public.document_library_folders (created_at desc);

create table if not exists public.document_library (
    id uuid primary key default gen_random_uuid(),
    collection text not null check (collection in ('Report Templates', 'Policies & Memoranda')),
    folder_id uuid references public.document_library_folders(id) on delete set null,
    title text not null,
    category text not null default 'General',
    subject_category text,
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

alter table public.document_library
    add column if not exists folder_id uuid;

alter table public.document_library
    add column if not exists subject_category text;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'document_library_folder_id_fkey'
          and conrelid = 'public.document_library'::regclass
    ) then
        alter table public.document_library
            add constraint document_library_folder_id_fkey
            foreign key (folder_id)
            references public.document_library_folders(id)
            on delete set null;
    end if;
end $$;

create index if not exists document_library_collection_idx
    on public.document_library (collection);
create index if not exists document_library_folder_id_idx
    on public.document_library (folder_id);
create index if not exists document_library_category_idx
    on public.document_library (category);
create index if not exists document_library_subject_category_idx
    on public.document_library (subject_category);
create index if not exists document_library_uploaded_at_idx
    on public.document_library (uploaded_at desc);
create index if not exists document_library_sha256_idx
    on public.document_library (sha256);

alter table public.document_library enable row level security;
alter table public.document_library_folders enable row level security;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.document_library to service_role;
grant select, insert, update, delete on table public.document_library_folders to service_role;
