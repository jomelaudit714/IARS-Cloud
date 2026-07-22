-- IARS Weekly Itinerary permission hotfix — V4.4.73A
-- Run this in the SAME Supabase project's SQL Editor used by IARS.
-- Safe to run more than once.

begin;

-- The Streamlit application connects through the Supabase service-role key.
-- RLS bypass alone is not enough: PostgREST also requires SQL table privileges.
grant usage on schema public to service_role;
grant select, insert, update, delete
    on table public.weekly_itineraries
    to service_role;

-- Explicit Storage permissions for private itinerary images.
grant usage on schema storage to service_role;
grant select on table storage.buckets to service_role;
grant select, insert, update, delete
    on table storage.objects
    to service_role;

commit;

-- Verification: this should show SELECT/INSERT/UPDATE/DELETE for service_role.
select
    grantee,
    privilege_type
from information_schema.role_table_grants
where table_schema = 'public'
  and table_name = 'weekly_itineraries'
  and grantee = 'service_role'
order by privilege_type;
