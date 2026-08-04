-- IARS V4.5.18 — Gantt duplicate-rule migration
-- Safe for existing V4.5.16/V4.5.17 installations.
-- This does not delete Gantt master or schedule records.

begin;

-- The old rule blocked the same Company/Custodian/Audit Task even when
-- Accountability was different. Replace it with the exact four-field rule.
alter table public.iars_gantt_master
    drop constraint if exists iars_gantt_master_unique_record;

alter table public.iars_gantt_master
    add constraint iars_gantt_master_unique_record
    unique (company_department, custodian, audit_task, accountability);

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.iars_gantt_master to service_role;
grant select, insert, update, delete on table public.iars_gantt_schedule to service_role;

commit;
