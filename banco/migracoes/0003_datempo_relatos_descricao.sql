-- Dá Tempo?: descrição curta e opcional no relato (até 140 caracteres).
--
-- O texto passa antes pela barreira de dado pessoal do servidor (sem CPF, telefone, e-mail, endereço,
-- nome ou link) e só aparece no feed. A Lia não lê esta coluna.
--
-- Aditiva e idempotente: relatos antigos ficam com descrição vazia. Só mexe no esquema "datempo".

alter table datempo.relatos
  add column if not exists descricao text not null default '' check (char_length(descricao) <= 140);

-- o PostgREST precisa recarregar o esquema para enxergar a coluna
notify pgrst, 'reload schema';
