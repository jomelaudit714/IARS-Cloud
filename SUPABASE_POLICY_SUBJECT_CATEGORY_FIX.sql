-- IARS V4.4.95
-- Fix for PGRST204: document_library.subject_category is missing from schema cache.
-- Run this once in the Supabase SQL Editor for the same project used by IARS.

begin;

alter table public.document_library
    add column if not exists subject_category text;

update public.document_library
set subject_category = 'Other'
where collection = 'Policies & Memoranda'
  and coalesce(trim(subject_category), '') = '';

create index if not exists document_library_subject_category_idx
    on public.document_library (subject_category);

grant usage on schema public to service_role;
grant select, insert, update, delete
    on table public.document_library
    to service_role;

commit;

-- Ask PostgREST/Supabase API to refresh its table/column cache immediately.
notify pgrst, 'reload schema';

-- Verification result: this must return one row for subject_category.
select
    column_name,
    data_type,
    is_nullable
from information_schema.columns
where table_schema = 'public'
  and table_name = 'document_library'
  and column_name = 'subject_category';
