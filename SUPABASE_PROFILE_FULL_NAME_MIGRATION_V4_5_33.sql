-- IARS V4.5.33: allow the Administrator profile to save an editable full name.
-- Safe to run more than once in Supabase SQL Editor.

begin;

alter table public.iars_profiles
  add column if not exists full_name_override text;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.iars_profiles to service_role;

commit;

notify pgrst, 'reload schema';

select column_name, data_type
from information_schema.columns
where table_schema = 'public'
  and table_name = 'iars_profiles'
  and column_name = 'full_name_override';
