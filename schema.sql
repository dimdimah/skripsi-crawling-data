create table if not exists public.jobs (
    id            uuid default gen_random_uuid() primary key,
    title         text        not null,
    company       text        not null,
    location      text        not null,
    type          text        not null default 'Full-time'
                    check (type in ('Full-time', 'Part-time', 'Contract', 'Internship')),
    salary        text,
    description   text        not null,
    skills        jsonb       default '[]'::jsonb,
    contact_info  text,
    url           text        not null unique,
    source        text        not null,
    is_active     boolean     not null default true,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

create index if not exists idx_jobs_source    on public.jobs (source);
create index if not exists idx_jobs_is_active on public.jobs (is_active);

create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create trigger trg_jobs_updated_at
before update on public.jobs
for each row execute procedure set_updated_at();
