-- IARS V4.5.48 Notification Center
-- Safe additive migration. Does not alter existing IARS tables.

create extension if not exists pgcrypto;

create table if not exists public.iars_notifications (
    id uuid primary key default gen_random_uuid(),
    event_key text unique,
    category text not null default 'Information',
    title text not null,
    message text not null default '',
    target_type text not null default 'all' check (target_type in ('all', 'user')),
    recipient_key text not null default '',
    action_page text not null default '',
    source_type text not null default '',
    source_id text not null default '',
    created_by text not null default '',
    created_at timestamptz not null default now()
);

create index if not exists iars_notifications_created_at_idx
    on public.iars_notifications (created_at desc);
create index if not exists iars_notifications_target_idx
    on public.iars_notifications (target_type, recipient_key);

create table if not exists public.iars_notification_reads (
    notification_id uuid not null references public.iars_notifications(id) on delete cascade,
    user_key text not null,
    read_at timestamptz not null default now(),
    primary key (notification_id, user_key)
);

create index if not exists iars_notification_reads_user_idx
    on public.iars_notification_reads (user_key, read_at desc);

alter table public.iars_notifications enable row level security;
alter table public.iars_notification_reads enable row level security;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.iars_notifications to service_role;
grant select, insert, update, delete on table public.iars_notification_reads to service_role;

notify pgrst, 'reload schema';
