-- IARS v4.4.79 - Policies & Memoranda Subject / Process Category
-- Run this once in the same Supabase project used by IARS.

alter table public.document_library
    add column if not exists subject_category text;

update public.document_library
set subject_category = 'Other'
where collection = 'Policies & Memoranda'
  and coalesce(trim(subject_category), '') = '';

create index if not exists document_library_subject_category_idx
    on public.document_library (subject_category);

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.document_library to service_role;

select column_name, data_type, is_nullable
from information_schema.columns
where table_schema = 'public'
  and table_name = 'document_library'
  and column_name = 'subject_category';
