-- Dá Tempo?: relatos dos passageiros no Supabase (projeto PontoW, esquema próprio "datempo").
--
-- O esquema fica separado do "public" da GoodWe. Só o servidor (FastAPI, com a chave secreta)
-- lê e grava: anon e authenticated não têm nenhum acesso, e o RLS fica ligado sem política,
-- como segunda trava. Nada de dado pessoal: o autor é só um hash de 12 caracteres do id aleatório
-- do aparelho, e o relato tem só campos prontos (linha, tipo, estação).
--
-- Idempotente: pode rodar de novo sem quebrar.

create schema if not exists datempo;

revoke all on schema datempo from public, anon, authenticated;
grant usage on schema datempo to service_role;

-- ------------------------------------------------------------------ relatos
create table if not exists datempo.relatos (
  id            text primary key check (id ~ '^[0-9a-f]{12}$'),
  linha         text not null check (linha ~ '^[0-9]{1,2}$'),
  estacao_id    text check (estacao_id is null or length(estacao_id) between 1 and 64),
  tipo          text not null check (tipo in ('lotado', 'parado', 'quebrou', 'chuva', 'alagado', 'seguranca', 'normal')),
  criado_em     timestamptz not null default now(),
  expira_em     timestamptz not null,
  autor_hash    text not null check (autor_hash ~ '^[0-9a-f]{12}$'),
  confirmacoes  integer not null default 0 check (confirmacoes >= 0),
  contestacoes  integer not null default 0 check (contestacoes >= 0),
  sinalizacoes  integer not null default 0 check (sinalizacoes >= 0),
  demo          boolean not null default false,
  check (expira_em > criado_em)
);

-- relatos ativos (expira_em > now()) e limpeza dos vencidos
create index if not exists relatos_expira_em_idx on datempo.relatos (expira_em);
-- "um relato por autor e linha a cada 10 min": a conferência fica no servidor (um processo só, com trava);
-- com mais de um processo, trocar por uma função com pg_advisory_xact_lock
-- (a consulta precisa ter demo = false para usar este índice parcial)
create index if not exists relatos_autor_linha_idx on datempo.relatos (autor_hash, linha, criado_em desc) where not demo;

-- ------------------------------------------------------------------ votos ("continua" / "já acabou")
create table if not exists datempo.votos (
  relato_id   text not null references datempo.relatos (id) on delete cascade,
  autor_hash  text not null check (autor_hash ~ '^[0-9a-f]{12}$'),
  valor       text not null check (valor in ('ainda', 'acabou')),
  criado_em   timestamptz not null default now(),
  primary key (relato_id, autor_hash)
);

-- ------------------------------------------------------------------ sinalizações (3 tiram o relato do feed)
create table if not exists datempo.sinalizacoes (
  relato_id   text not null references datempo.relatos (id) on delete cascade,
  autor_hash  text not null check (autor_hash ~ '^[0-9a-f]{12}$'),
  criado_em   timestamptz not null default now(),
  primary key (relato_id, autor_hash)
);

alter table datempo.relatos enable row level security;
alter table datempo.votos enable row level security;
alter table datempo.sinalizacoes enable row level security;

revoke all on all tables in schema datempo from public, anon, authenticated;
grant select, insert, update, delete on all tables in schema datempo to service_role;

-- ------------------------------------------------------------------ operações atômicas
-- Um voto por pessoa por relato: grava o voto e soma no contador na mesma transação.
-- Devolve false se a pessoa já votou ou se o relato não existe mais.
create or replace function datempo.registrar_voto(p_relato text, p_autor text, p_valor text)
returns boolean
language plpgsql
security invoker
set search_path = ''
as $$
begin
  begin
    insert into datempo.votos (relato_id, autor_hash, valor)
    select r.id, p_autor, p_valor from datempo.relatos r
     where r.id = p_relato and r.expira_em > now() and r.sinalizacoes < 3
    on conflict do nothing;
  exception when foreign_key_violation then
    return false;   -- o relato venceu e foi apagado no meio do caminho
  end;
  if not found then
    return false;
  end if;
  update datempo.relatos
     set confirmacoes = confirmacoes + (p_valor = 'ainda')::int,
         contestacoes = contestacoes + (p_valor = 'acabou')::int
   where id = p_relato;
  return true;
end;
$$;

create or replace function datempo.registrar_sinalizacao(p_relato text, p_autor text)
returns boolean
language plpgsql
security invoker
set search_path = ''
as $$
begin
  begin
    insert into datempo.sinalizacoes (relato_id, autor_hash)
    select r.id, p_autor from datempo.relatos r
     where r.id = p_relato and r.expira_em > now() and r.sinalizacoes < 3
    on conflict do nothing;
  exception when foreign_key_violation then
    return false;
  end;
  if not found then
    return false;
  end if;
  update datempo.relatos set sinalizacoes = sinalizacoes + 1 where id = p_relato;
  return true;
end;
$$;

revoke all on function datempo.registrar_voto(text, text, text) from public, anon, authenticated;
revoke all on function datempo.registrar_sinalizacao(text, text) from public, anon, authenticated;
grant execute on function datempo.registrar_voto(text, text, text) to service_role;
grant execute on function datempo.registrar_sinalizacao(text, text) to service_role;

-- tabelas e funções criadas depois neste esquema: só o service_role. A trava real para anon e authenticated é
-- não terem USAGE no esquema; em função nova, revogar EXECUTE de public explicitamente (o padrão do Postgres dá).
alter default privileges in schema datempo revoke all on tables from public, anon, authenticated;
alter default privileges in schema datempo revoke all on functions from public, anon, authenticated;
alter default privileges in schema datempo grant select, insert, update, delete on tables to service_role;
alter default privileges in schema datempo grant execute on functions to service_role;
