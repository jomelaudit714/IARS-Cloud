-- IARS V4.5.51 Notification per-user delete state
-- Safe additive migration. Run after V4.5.48 notification setup.
-- Does not alter or delete any existing notification, Gantt, itinerary, archive,
-- authentication, document-library, or audit-extraction records.

alter table if exists public.iars_notification_reads
    add column if not exists deleted_at timestamptz;

create index if not exists iars_notification_reads_deleted_idx
    on public.iars_notification_reads (user_key, deleted_at desc);

grant usage on schema public to service_role;
grant select, insert, update, delete
    on table public.iars_notification_reads
    to service_role;

notify pgrst, 'reload schema';
