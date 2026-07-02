-- IARS editable profile and profile-picture storage (v4.4.14)
-- Safe to run more than once in the Supabase SQL Editor.

create table if not exists public.iars_profiles (
  user_id text primary key,
  username_override text unique,
  profile_picture_path text,
  profile_picture_data text,
  admin_password_salt text,
  admin_password_hash text,
  updated_at timestamptz not null default now()
);

alter table public.iars_profiles
  add column if not exists username_override text,
  add column if not exists profile_picture_path text,
  add column if not exists profile_picture_data text,
  add column if not exists admin_password_salt text,
  add column if not exists admin_password_hash text,
  add column if not exists updated_at timestamptz not null default now();

create unique index if not exists iars_profiles_username_override_unique_idx
  on public.iars_profiles (lower(username_override))
  where username_override is not null;

alter table public.iars_profiles enable row level security;

-- The Streamlit app uses the server-side service-role key, so public policies
-- are intentionally not added.
insert into storage.buckets (
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types
)
values (
  'iars-profile-pictures',
  'iars-profile-pictures',
  false,
  5242880,
  array['image/jpeg','image/png']
)
on conflict (id) do update set
  name = excluded.name,
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

-- Refresh PostgREST's schema cache after adding/updating columns.
notify pgrst, 'reload schema';
