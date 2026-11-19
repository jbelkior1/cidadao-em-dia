-- Dá Tempo?: a avaliação pode ser só um comentário (formulário simples "O que você achou do sistema?").
-- As 5 notas de facilidade deixam de ser obrigatórias; a regra passa a ser: ou as 5 notas, ou um comentário.
-- O teste completo (tarefas, energia e notas) continua gravando tudo, como antes.
--
-- Só afrouxa a regra: nenhuma linha muda e nenhuma permissão muda. Idempotente.

alter table datempo.avaliacoes alter column f1 drop not null;
alter table datempo.avaliacoes alter column f2 drop not null;
alter table datempo.avaliacoes alter column f3 drop not null;
alter table datempo.avaliacoes alter column f4 drop not null;
alter table datempo.avaliacoes alter column f5 drop not null;

alter table datempo.avaliacoes drop constraint if exists avaliacoes_notas_ou_comentario;
alter table datempo.avaliacoes add constraint avaliacoes_notas_ou_comentario check (
  (f1 is not null and f2 is not null and f3 is not null and f4 is not null and f5 is not null) or comentario is not null
);
