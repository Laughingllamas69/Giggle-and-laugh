create table if not exists public.mood_logs (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    timestamp timestamptz not null default now(),
    mood_score integer not null check (mood_score between 1 and 4),
    recommendation text not null
);

create index if not exists mood_logs_user_timestamp_idx
    on public.mood_logs (user_id, timestamp);

create table if not exists public.memes (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    description text not null,
    image_path text not null,
    user_id text not null,
    created_at timestamptz not null default now()
);

create index if not exists memes_created_at_idx
    on public.memes (created_at desc);

create table if not exists public.jokes (
    id uuid primary key default gen_random_uuid(),
    category text not null,
    text text not null,
    user_id text not null,
    created_at timestamptz not null default now()
);

create index if not exists jokes_created_at_idx
    on public.jokes (created_at desc);

alter table public.mood_logs enable row level security;
alter table public.memes enable row level security;
alter table public.jokes enable row level security;

grant all privileges on table public.mood_logs to service_role;
grant all privileges on table public.memes to service_role;
grant all privileges on table public.jokes to service_role;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
    'community-memes',
    'community-memes',
    true,
    5242880,
    array['image/png', 'image/jpeg', 'image/webp']
)
on conflict (id) do update set
    public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;