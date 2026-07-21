-- IARS v4.4.69 - Company Folder Migration for Policies & Memoranda
-- Run this ONCE in the existing Supabase project's SQL Editor before deploying
-- app.py and iars_document_library.py from the V4.4.69 patch.

create extension if not exists pgcrypto;

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

alter table public.document_library
    add column if not exists folder_id uuid;

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

create index if not exists document_library_folder_id_idx
    on public.document_library (folder_id);

alter table public.document_library_folders enable row level security;

grant usage on schema public to service_role;
grant select, insert, update, delete
    on table public.document_library_folders to service_role;
grant select, insert, update, delete
    on table public.document_library to service_role;
