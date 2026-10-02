create extension if not exists vector with schema extensions;

create table if not exists public.business_chunks (
  id text primary key,
  business_id text not null,
  url text not null,
  title text not null,
  section text not null,
  content_type text not null default 'website',
  content text not null,
  metadata jsonb not null default '{}'::jsonb,
  embedding extensions.vector(1536) not null,
  last_indexed timestamptz not null default now(),
  indexed_at timestamptz not null default now()
);
alter table public.business_chunks add column if not exists indexed_at timestamptz not null default now();
create index if not exists business_chunks_business_idx on public.business_chunks (business_id);
create index if not exists business_chunks_embedding_idx on public.business_chunks using hnsw (embedding extensions.vector_cosine_ops);
alter table public.business_chunks enable row level security;

create or replace function public.match_business_chunks(
  query_embedding extensions.vector(1536),
  match_business_id text,
  match_count int default 6
)
returns table (id text, content text, metadata jsonb, similarity float)
language sql stable security definer set search_path = public, extensions
as $$
  select c.id, c.content, c.metadata, 1 - (c.embedding <=> query_embedding) as similarity
  from public.business_chunks c
  where c.business_id = match_business_id
  order by c.embedding <=> query_embedding
  limit least(greatest(match_count, 1), 12);
$$;
revoke all on function public.match_business_chunks(extensions.vector, text, int) from public, anon, authenticated;
grant execute on function public.match_business_chunks(extensions.vector, text, int) to service_role;
grant all on public.business_chunks to service_role;

create table if not exists public.chat_rate_limits (
  key_hash text primary key,
  window_started_at timestamptz not null,
  request_count integer not null default 0
);
alter table public.chat_rate_limits enable row level security;
grant all on public.chat_rate_limits to service_role;

create or replace function public.consume_chat_rate_limit(request_key text, max_requests integer, window_seconds integer)
returns boolean
language plpgsql security definer set search_path = public
as $$
declare allowed boolean;
begin
  insert into public.chat_rate_limits as limits (key_hash, window_started_at, request_count)
  values (request_key, now(), 1)
  on conflict (key_hash) do update set
    window_started_at = case when limits.window_started_at < now() - make_interval(secs => window_seconds) then now() else limits.window_started_at end,
    request_count = case when limits.window_started_at < now() - make_interval(secs => window_seconds) then 1 else limits.request_count + 1 end;
  select request_count <= max_requests into allowed from public.chat_rate_limits where chat_rate_limits.key_hash = request_key;
  return allowed;
end;
$$;
revoke all on function public.consume_chat_rate_limit(text, integer, integer) from public, anon, authenticated;
grant execute on function public.consume_chat_rate_limit(text, integer, integer) to service_role;
