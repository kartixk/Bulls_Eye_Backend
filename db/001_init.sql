-- Personal AI Trading Assistant — initial schema
-- Phase 1: single owner. Phase 2: multi-user (RLS already user-scoped).
-- Run this in the Supabase SQL editor against your own Supabase project.

create extension if not exists "pgcrypto";

create table if not exists public.users (
    id              uuid primary key references auth.users(id) on delete cascade,
    email           text unique not null,
    display_name    text,
    telegram_chat_id text,
    role            text not null default 'owner',
    created_at      timestamptz not null default now()
);

do $$ begin
    create type signal_action as enum ('BUY', 'SELL');
exception when duplicate_object then null; end $$;

do $$ begin
    create type signal_kind as enum ('EQUITY', 'FNO');
exception when duplicate_object then null; end $$;

do $$ begin
    create type signal_outcome as enum ('WIN', 'LOSS', 'PARTIAL', 'MISSED');
exception when duplicate_object then null; end $$;

do $$ begin
    create type instrument_type as enum ('equity', 'index', 'fno');
exception when duplicate_object then null; end $$;

create table if not exists public.signals (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid not null references public.users(id) on delete cascade,
    instrument      text not null,
    kind            signal_kind not null,
    action          signal_action not null,
    entry_price     numeric(12,2) not null,
    target_price    numeric(12,2),
    stop_loss       numeric(12,2),
    confidence      numeric(5,2) not null check (confidence between 0 and 100),
    rsi             numeric(6,2),
    macd            numeric(10,4),
    ema21           numeric(12,2),
    volume_ratio    numeric(6,2),
    strike_price    numeric(12,2),
    expiry_date     date,
    premium         numeric(10,2),
    rationale       text,
    outcome         signal_outcome,
    created_at      timestamptz not null default now()
);

create index if not exists idx_signals_user_created on public.signals (user_id, created_at desc);
create index if not exists idx_signals_instrument on public.signals (instrument);

create table if not exists public.watchlist (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid not null references public.users(id) on delete cascade,
    instrument      text not null,
    instrument_type instrument_type not null,
    added_at        timestamptz not null default now(),
    unique (user_id, instrument)
);

create index if not exists idx_watchlist_user on public.watchlist (user_id);

create table if not exists public.system_health (
    id              uuid primary key default gen_random_uuid(),
    component       text not null,
    status          text not null,
    message         text,
    recorded_at     timestamptz not null default now()
);

create index if not exists idx_health_recorded on public.system_health (recorded_at desc);

alter table public.users         enable row level security;
alter table public.signals       enable row level security;
alter table public.watchlist     enable row level security;
alter table public.system_health enable row level security;

grant select, insert, update, delete on public.users     to authenticated;
grant select, insert, update, delete on public.signals   to authenticated;
grant select, insert, update, delete on public.watchlist to authenticated;
grant select on public.system_health to authenticated;
grant all on public.users, public.signals, public.watchlist, public.system_health to service_role;

drop policy if exists "users self" on public.users;
create policy "users self" on public.users
    for all to authenticated using (id = auth.uid()) with check (id = auth.uid());

drop policy if exists "signals own" on public.signals;
create policy "signals own" on public.signals
    for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists "watchlist own" on public.watchlist;
create policy "watchlist own" on public.watchlist
    for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists "health read" on public.system_health;
create policy "health read" on public.system_health
    for select to authenticated using (true);

alter publication supabase_realtime add table public.signals;
alter publication supabase_realtime add table public.watchlist;
