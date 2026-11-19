-- Dá Tempo?: avaliação de quem usou o sistema (página "Avaliação usuários").
-- Uma linha por pessoa que fez o teste guiado: as 3 tarefas da PAI (tempo e acerto), as 4 situações de
-- energia da SERS, a nota de energia, as 5 perguntas de facilidade (1 a 5), um comentário e uma sugestão.
--
-- Sem dado pessoal: nada de nome, e-mail ou telefone. O servidor recusa texto com dado pessoal antes de
-- gravar (mesma barreira da Lia) e guarda só o hash do id aleatório do aparelho, para limitar envios.
-- Mesmas travas da 0001 e da 0002: só o servidor (FastAPI, chave secreta) lê e grava; anon e authenticated
-- sem acesso nenhum; RLS ligado sem política como segunda trava.
--
-- Idempotente: pode rodar de novo sem quebrar.

create table if not exists datempo.avaliacoes (
  id             uuid primary key default gen_random_uuid(),
  criada_em      timestamptz not null default now(),
  autor_hash     text not null check (autor_hash ~ '^[0-9a-f]{12}$'),
  perfil         text check (perfil in ('familia', 'faculdade', 'trabalho', 'conhecido', 'outro')),
  -- tarefas da PAI: segundos até achar (nulo = não achou em 5 minutos) e se a resposta escolhida estava certa
  t1_segundos    integer check (t1_segundos between 0 and 300),
  t2_segundos    integer check (t2_segundos between 0 and 300),
  t3_segundos    integer check (t3_segundos between 0 and 300),
  t1_acertou     boolean,
  t2_acertou     boolean,
  t3_acertou     boolean,
  -- situações de energia da SERS: a pessoa entendeu?
  e1             text check (e1 in ('sim', 'em parte', 'nao')),
  e2             text check (e2 in ('sim', 'em parte', 'nao')),
  e3             text check (e3 in ('sim', 'em parte', 'nao')),
  e4             text check (e4 in ('sim', 'em parte', 'nao')),
  nota_energia   smallint check (nota_energia between 1 and 5),
  -- facilidade (1 = discordo totalmente, 5 = concordo totalmente)
  f1             smallint not null check (f1 between 1 and 5),
  f2             smallint not null check (f2 between 1 and 5),
  f3             smallint not null check (f3 between 1 and 5),
  f4             smallint not null check (f4 between 1 and 5),
  f5             smallint not null check (f5 between 1 and 5),
  comentario     text check (comentario is null or length(comentario) between 1 and 500),
  sugestao       text check (sugestao is null or length(sugestao) between 1 and 300)
);
create index if not exists avaliacoes_criada_idx on datempo.avaliacoes (criada_em desc);
create index if not exists avaliacoes_autor_idx on datempo.avaliacoes (autor_hash, criada_em desc);

alter table datempo.avaliacoes enable row level security;
revoke all on datempo.avaliacoes from public, anon, authenticated;
grant select, insert, delete on datempo.avaliacoes to service_role;
