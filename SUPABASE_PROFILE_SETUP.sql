-- IARS editable profile settings (v4.4.13)
-- Run once in the Supabase SQL Editor.

create table if not exists public.iars_profiles (
  user_id text primary key,
  username_override text unique,
  profile_picture_data text,
  admin_password_salt text,
  admin_password_hash text,
  updated_at timestamptz not null default now()
);

create index if not exists iars_profiles_username_override_idx
  on public.iars_profiles (lower(username_override));

alter table public.iars_profiles enable row level security;

-- The Streamlit app uses the Supabase service-role key server-side.
-- No public client policy is required.
