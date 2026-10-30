create table if not exists public.mood_logs (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    timestamp timestamptz not null default now(),
    mood_score integer not null check (mood_score between 1 and 4),
    mood_label text not null default 'Unspecified',
    recommendation text not null
);

alter table public.mood_logs
    add column if not exists mood_label text not null default 'Unspecified';

create index if not exists mood_logs_user_timestamp_idx
    on public.mood_logs (user_id, timestamp);

create table if not exists public.memes (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    description text not null,
    image_path text not null,
    user_id text not null,
    created_at timestamptz not null default now(),
    is_hidden boolean not null default false
);

alter table public.memes
    add column if not exists is_hidden boolean not null default false;

create index if not exists memes_created_at_idx
    on public.memes (created_at desc);

create table if not exists public.jokes (
    id uuid primary key default gen_random_uuid(),
    category text not null,
    text text not null,
    user_id text not null,
    created_at timestamptz not null default now(),
    is_hidden boolean not null default false
);

alter table public.jokes
    add column if not exists is_hidden boolean not null default false;

create index if not exists jokes_created_at_idx
    on public.jokes (created_at desc);

create table if not exists public.content_reports (
    id uuid primary key default gen_random_uuid(),
    target_type text not null check (target_type in ('meme', 'joke')),
    target_id uuid not null,
    reporter_id text not null,
    reason text not null,
    resolved boolean not null default false,
    created_at timestamptz not null default now(),
    unique (target_type, target_id, reporter_id)
);

create index if not exists content_reports_open_created_idx
    on public.content_reports (resolved, created_at desc);

create table if not exists public.game_scores (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    game_name text not null,
    score integer not null check (score >= 0),
    created_at timestamptz not null default now()
);

create index if not exists game_scores_game_created_idx
    on public.game_scores (game_name, created_at desc);

create or replace function public.get_game_leaderboard(
    p_game_name text,
    p_since timestamptz default null
)
returns table (user_id text, metric bigint, rounds bigint)
language sql
stable
security definer
set search_path = public
as $$
    select
        scores.user_id,
        case
            when p_game_name = 'rock-paper-scissors' then sum(scores.score)::bigint
            else max(scores.score)::bigint
        end as metric,
        count(*)::bigint as rounds
    from public.game_scores as scores
    where scores.game_name = p_game_name
      and (p_since is null or scores.created_at >= p_since)
    group by scores.user_id
    order by metric desc, rounds desc, scores.user_id
    limit 10;
$$;

revoke all on function public.get_game_leaderboard(text, timestamptz) from public, anon, authenticated;
grant execute on function public.get_game_leaderboard(text, timestamptz) to service_role;

create table if not exists public.profiles (
    user_id text primary key,
    display_name text not null,
    avatar_color text not null default '#24473f',
    bio text not null default '',
    updated_at timestamptz not null default now()
);

create table if not exists public.activity_events (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    activity_type text not null,
    activity_date date not null default current_date,
    points integer not null default 0 check (points >= 0),
    created_at timestamptz not null default now(),
    unique (user_id, activity_type, activity_date)
);

create index if not exists activity_events_user_date_idx
    on public.activity_events (user_id, activity_date desc);

create table if not exists public.screen_time_submissions (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    activity_date date not null,
    screen_time_minutes integer not null check (screen_time_minutes between 1 and 1440),
    evidence_path text not null,
    created_at timestamptz not null default now(),
    unique (user_id, activity_date)
);

create index if not exists screen_time_submissions_date_minutes_idx
    on public.screen_time_submissions (activity_date, screen_time_minutes, user_id);

create table if not exists public.screen_time_rewards (
    week_start date not null,
    user_id text not null,
    rank integer not null check (rank between 1 and 100),
    points_awarded integer not null check (points_awarded between 1 and 100),
    created_at timestamptz not null default now(),
    primary key (week_start, user_id),
    unique (week_start, rank)
);

create table if not exists public.hobby_goals (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    hobby_name text not null check (char_length(hobby_name) between 1 and 60),
    goal text not null check (char_length(goal) between 1 and 240),
    skill_level text not null check (
        skill_level in ('Brand new', 'Some experience', 'Getting back into it')
    ),
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists hobby_goals_user_active_updated_idx
    on public.hobby_goals (user_id, is_active, updated_at desc);

create table if not exists public.hobby_messages (
    id uuid primary key default gen_random_uuid(),
    goal_id uuid not null references public.hobby_goals (id) on delete cascade,
    user_id text not null,
    role text not null check (role in ('user', 'assistant')),
    content text not null check (char_length(content) between 1 and 2000),
    created_at timestamptz not null default now()
);

create index if not exists hobby_messages_goal_user_created_idx
    on public.hobby_messages (goal_id, user_id, created_at);

create or replace function public.get_screen_time_leaderboard(
    p_week_start date
)
returns table (
    user_id text,
    average_minutes numeric,
    submission_count bigint,
    rank bigint,
    points_awarded integer
)
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
    v_current_week_start date :=
        date_trunc('week', timezone('utc', now()))::date;
begin
    if p_week_start is null
       or p_week_start > v_current_week_start
       or extract(isodow from p_week_start) <> 1 then
        raise exception 'Week start must be a Monday not later than the current week.';
    end if;

    if p_week_start = v_current_week_start then
        with weeks_to_award as (
            select distinct date_trunc('week', submissions.activity_date)::date as week_start
            from public.screen_time_submissions as submissions
            where submissions.activity_date < v_current_week_start
              and not exists (
                  select 1
                  from public.screen_time_rewards as existing_rewards
                  where existing_rewards.week_start =
                      date_trunc('week', submissions.activity_date)::date
              )
        ),
        ranked_weeks as (
            select
                weeks.week_start,
                submissions.user_id,
                row_number() over (
                    partition by weeks.week_start
                    order by avg(submissions.screen_time_minutes),
                        count(*) desc,
                        submissions.user_id
                ) as place
            from weeks_to_award as weeks
            join public.screen_time_submissions as submissions
              on submissions.activity_date >= weeks.week_start
             and submissions.activity_date < weeks.week_start + 7
            group by weeks.week_start, submissions.user_id
        ),
        newly_awarded as (
            insert into public.screen_time_rewards (
                week_start, user_id, rank, points_awarded
            )
            select
                ranked.week_start,
                ranked.user_id,
                ranked.place::integer,
                (101 - ranked.place)::integer
            from ranked_weeks as ranked
            where ranked.place <= 100
            on conflict (week_start, user_id) do nothing
            returning week_start, user_id, points_awarded
        )
        insert into public.activity_events (
            user_id, activity_type, activity_date, points
        )
        select
            newly_awarded.user_id,
            'weekly_screen_time_reward',
            newly_awarded.week_start,
            newly_awarded.points_awarded
        from newly_awarded
        on conflict (user_id, activity_type, activity_date) do nothing;
    end if;

    return query
    with ranked_week as (
        select
            submissions.user_id,
            round(avg(submissions.screen_time_minutes), 2) as avg_minutes,
            count(*)::bigint as entries,
            row_number() over (
                order by avg(submissions.screen_time_minutes),
                    count(*) desc,
                    submissions.user_id
            ) as place
        from public.screen_time_submissions as submissions
        where submissions.activity_date >= p_week_start
          and submissions.activity_date < p_week_start + 7
        group by submissions.user_id
    )
    select
        ranked.user_id,
        ranked.avg_minutes,
        ranked.entries,
        ranked.place,
        coalesce(rewards.points_awarded, 0)
    from ranked_week as ranked
    left join public.screen_time_rewards as rewards
      on rewards.week_start = p_week_start
     and rewards.user_id = ranked.user_id
    where ranked.place <= 100
    order by ranked.place;
end;
$$;

revoke all on function public.get_screen_time_leaderboard(date) from public, anon, authenticated;
grant execute on function public.get_screen_time_leaderboard(date) to service_role;

create table if not exists public.comments (
    id uuid primary key default gen_random_uuid(),
    target_type text not null check (target_type in ('meme', 'joke')),
    target_id uuid not null,
    user_id text not null,
    body text not null check (char_length(body) between 1 and 300),
    created_at timestamptz not null default now()
);

create index if not exists comments_target_created_idx
    on public.comments (target_type, target_id, created_at);

create table if not exists public.chat_messages (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    display_name text not null check (char_length(display_name) between 1 and 30),
    body text not null,
    created_at timestamptz not null default now(),
    is_hidden boolean not null default false,
    attachment_path text,
    attachment_name text,
    attachment_type text,
    attachment_size integer check (attachment_size is null or attachment_size between 1 and 1048576)
);

alter table public.chat_messages
    add column if not exists attachment_path text,
    add column if not exists attachment_name text,
    add column if not exists attachment_type text,
    add column if not exists attachment_size integer
        check (attachment_size is null or attachment_size between 1 and 1048576);

alter table public.chat_messages
    drop constraint if exists chat_messages_body_check;

alter table public.chat_messages
    add constraint chat_messages_body_check
        check (
            char_length(body) between 1 and 500
            or (char_length(body) = 0 and attachment_path is not null)
        );

create index if not exists chat_messages_created_idx
    on public.chat_messages (created_at desc)
    where is_hidden = false;

create table if not exists public.reactions (
    id uuid primary key default gen_random_uuid(),
    target_type text not null check (target_type in ('meme', 'joke')),
    target_id uuid not null,
    user_id text not null,
    reaction text not null check (reaction in ('like', 'laugh', 'love')),
    created_at timestamptz not null default now(),
    unique (target_type, target_id, user_id)
);

create index if not exists reactions_target_idx
    on public.reactions (target_type, target_id);

alter table public.mood_logs enable row level security;
alter table public.memes enable row level security;
alter table public.jokes enable row level security;
alter table public.content_reports enable row level security;
alter table public.game_scores enable row level security;
alter table public.profiles enable row level security;
alter table public.activity_events enable row level security;
alter table public.screen_time_submissions enable row level security;
alter table public.screen_time_rewards enable row level security;
alter table public.hobby_goals enable row level security;
alter table public.hobby_messages enable row level security;
alter table public.comments enable row level security;
alter table public.reactions enable row level security;
alter table public.chat_messages enable row level security;

grant all privileges on table public.mood_logs to service_role;
grant all privileges on table public.memes to service_role;
grant all privileges on table public.jokes to service_role;
grant all privileges on table public.content_reports to service_role;
grant all privileges on table public.game_scores to service_role;
grant all privileges on table public.profiles to service_role;
grant all privileges on table public.activity_events to service_role;
grant all privileges on table public.screen_time_submissions to service_role;
grant all privileges on table public.screen_time_rewards to service_role;
grant all privileges on table public.hobby_goals to service_role;
grant all privileges on table public.hobby_messages to service_role;
grant all privileges on table public.comments to service_role;
grant all privileges on table public.reactions to service_role;
grant all privileges on table public.chat_messages to service_role;

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

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
    'screen-time-evidence',
    'screen-time-evidence',
    false,
    5242880,
    array['image/png', 'image/jpeg', 'image/webp']
)
on conflict (id) do update set
    public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
    'community-chat',
    'community-chat',
    false,
    1048576,
    array['image/png', 'image/jpeg', 'image/webp', 'application/pdf', 'text/plain']
)
on conflict (id) do update set
    public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;