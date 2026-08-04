-- IARS V4.5.18 — Gantt permission repair
-- Safe for existing Gantt tables. This does not delete or recreate any data.

begin;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.iars_gantt_master to service_role;
grant select, insert, update, delete on table public.iars_gantt_schedule to service_role;

commit;
