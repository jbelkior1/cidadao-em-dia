-- Dá Tempo?: conta básica (usuário e senha) e o que ela guarda: minhas linhas, estação de casa e
-- rotas salvas. Esquema próprio "datempo" (nada no "public" do projeto, nada no
-- login do Supabase).
--
-- Mesmas travas da 0001: só o servidor (FastAPI, chave secreta) lê e grava; anon e authenticated
-- sem acesso nenhum; RLS ligado sem política como segunda trava.
-- Dado pessoal mínimo: um nome de usuário escolhido pela pessoa (sem e-mail, sem nome real) e a
-- senha só como hash scrypt com sal. O token de sessão também só é guardado como hash SHA-256.
--
-- Idempotente: pode rodar de novo sem quebrar.

-- ------------------------------------------------------------------ contas
create table if not exists datempo.contas (
  id                 uuid primary key default gen_random_uuid(),
  usuario            text not null unique check (usuario ~ '^[a-z0-9_.]{3,30}$'),
  senha_hash         text not null check (senha_hash like 'scrypt$%' and length(senha_hash) between 40 and 200),
  criado_em          timestamptz not null default now(),
  tentativas_falhas  integer not null default 0 check (tentativas_falhas >= 0),
  bloqueado_ate      timestamptz
);

-- ------------------------------------------------------------------ sessões (login)
create table if not exists datempo.sessoes (
  token_hash  text primary key check (token_hash ~ '^[0-9a-f]{64}$'),
  conta_id    uuid not null references datempo.contas (id) on delete cascade,
  criada_em   timestamptz not null default now(),
  expira_em   timestamptz not null,
  check (expira_em > criada_em)
);
create index if not exists sessoes_conta_idx on datempo.sessoes (conta_id);
create index if not exists sessoes_expira_idx on datempo.sessoes (expira_em);

-- ------------------------------------------------------------------ preferências (uma linha por conta)
create table if not exists datempo.preferencias (
  conta_id       uuid primary key references datempo.contas (id) on delete cascade,
  linhas         text[] not null default '{}' check (cardinality(linhas) <= 20),
  casa           text check (casa is null or length(casa) between 1 and 64),
  atualizado_em  timestamptz not null default now()
);

-- ------------------------------------------------------------------ rotas salvas (viagem de sempre)
create table if not exists datempo.rotinas (
  id          uuid primary key default gen_random_uuid(),
  conta_id    uuid not null references datempo.contas (id) on delete cascade,
  nome        text not null check (length(nome) between 1 and 40),
  origem      text not null check (length(origem) between 1 and 64),
  destino     text not null check (length(destino) between 1 and 64),
  horario     time not null,
  dias        text not null default '12345' check (dias ~ '^[1-7]{1,7}$'),
  criada_em   timestamptz not null default now(),
  check (origem <> destino)
);
create index if not exists rotinas_conta_idx on datempo.rotinas (conta_id);

alter table datempo.contas enable row level security;
alter table datempo.sessoes enable row level security;
alter table datempo.preferencias enable row level security;
alter table datempo.rotinas enable row level security;

revoke all on datempo.contas, datempo.sessoes, datempo.preferencias, datempo.rotinas from public, anon, authenticated;
grant select, insert, update, delete on datempo.contas, datempo.sessoes, datempo.preferencias, datempo.rotinas to service_role;
