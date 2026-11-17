-- Dá Tempo?: foto como evidência no relato.
--
-- O arquivo não fica no banco: vai para um bucket privado do Storage ("datempo-relatos"), que o
-- servidor cria sozinho no primeiro envio. Aqui fica só a marca de que o relato tem foto.
-- Quando o relato vence ou recebe 3 sinalizações, o servidor apaga o arquivo e volta a marca para false.
--
-- Aditiva e idempotente: relatos antigos ficam sem foto. Só mexe no esquema "datempo".

alter table datempo.relatos
  add column if not exists tem_foto boolean not null default false;

-- a limpeza de fotos procura relatos com foto ainda marcada, por vencimento
create index if not exists relatos_foto_idx on datempo.relatos (expira_em) where tem_foto;

-- o PostgREST precisa recarregar o esquema para enxergar a coluna
notify pgrst, 'reload schema';
