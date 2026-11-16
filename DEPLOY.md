# Deploy do Dá Tempo? numa VPS

O sistema sobe em **um container só**: a API em Python (FastAPI) serve também as telas compiladas. O banco dos relatos e das contas fica no Supabase (esquema `datempo`) e a IA da Lia no Groq; o servidor só precisa das chaves.

No servidor, `MODO_PUBLICO=1` deixa a configuração de IA e o checklist **só para leitura**: os professores usam tudo, mas ninguém troca a chave nem edita o andamento pela tela.

## O que precisa ter

- Uma VPS Linux com Docker e o plugin Docker Compose (`docker compose version` responde).
- Um domínio ou subdomínio com registro **A** apontando para o IP da VPS (por exemplo, `datempo.seudominio.com.br`).
- Portas 80 e 443 abertas na VPS.
- As chaves em mãos: a do Groq e a URL e a chave secreta do Supabase. **Elas são digitadas só no servidor, nunca no chat nem no git.**

## Subir pela primeira vez

```bash
git clone https://github.com/jbelkior1/cidadao-em-dia.git datempo
cd datempo
cp .env.producao.exemplo .env.producao
nano .env.producao
docker compose up -d --build
```

No `nano`, preencha `IA_CHAVE`, `SUPABASE_URL` e `SUPABASE_SECRET_KEY` (o resto já vem preenchido). O primeiro build leva alguns minutos.

Confira se a API respondeu:

```bash
curl -s http://127.0.0.1:8010/api/saude
```

A resposta tem `"ok": true`. O container só escuta em `127.0.0.1:8010`; quem fala com a internet é o proxy com HTTPS, no passo seguinte.

## HTTPS

**Se a VPS ainda não tem proxy**, o Caddy resolve o certificado sozinho:

```bash
sudo apt install -y caddy
sudo cp deploy/Caddyfile.exemplo /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

No `nano`, troque `datempo.seudominio.com.br` pelo domínio de verdade.

**Se a VPS já tem Nginx**, use `deploy/nginx.exemplo.conf` como bloco do site (troque o domínio) e gere o certificado com o Certbot, como nos outros sites da máquina.

**Se a VPS já tem Traefik** (como a da equipe, em 16/11/2026): o contêiner não publica porta; o Traefik chega por uma rede interna própria e emite o certificado sozinho quando o DNS apontar para a VPS.

```bash
echo "DOMINIO=datempo.seudominio.com.br" > .env
docker compose -f docker-compose.yml -f deploy/docker-compose.traefik.yml up -d --build
docker network connect datempo_edge <contêiner do traefik>
```

## Conferir depois de subir

1. `https://SEU-DOMINIO` abre na página **Como funciona**.
2. A barra lateral não mostra **Configurações de IA** (é só no computador da equipe).
3. `https://SEU-DOMINIO/api/config/ia` mostra `"modo_publico": true` e `"ligada": true`.
4. Na aba **Sistema**, a Lia responde a "vou da Sé para a Paulista".
5. Em **Perfil**, criar uma conta de teste, salvar uma rota, sair e entrar de novo; depois apagar a conta.

## Atualizar

```bash
cd datempo
git pull
docker compose up -d --build
```

O volume `dados` guarda o contador de uso da IA e o histórico das linhas, e sobrevive à troca do container.

## Comandos do dia a dia

| Para quê | Comando |
|---|---|
| Ver os logs | `docker compose logs -f datempo` |
| Reiniciar | `docker compose restart datempo` |
| Parar | `docker compose down` |
| Ver o uso da IA hoje | `curl -s http://127.0.0.1:8010/api/config/ia` (campo `uso`) |

## Cuidados

- **Um processo só.** Os relatos de demonstração, o teste da DSA e o coletor da situação das linhas ficam na memória do processo: não suba com mais de um worker.
- **Limite de IA compartilhado.** `IA_LIMITE_DIARIO` vale para todo mundo que usa o servidor, inclusive o agente da PAI; cada mensagem gasta de 2 a 3 chamadas. Quando acaba, a Lia segue pelas regras e pela base e avisa. O plano gratuito do Groq também tem limite por minuto: com muita gente ao mesmo tempo, algumas respostas podem cair nas regras.
- **Limite por aparelho.** No modo público, cada aparelho (IP) faz no máximo 20 perguntas que usam IA a cada 5 minutos; depois disso recebe 429 com o aviso de esperar. Assim um visitante sozinho não esgota o limite do dia dos professores.
- **Histórico das linhas.** O arquivo `historico_linhas.local.jsonl` no volume cresce cerca de 1 MB por semana com o servidor ligado; para deixar no ar por meses, apague-o de vez em quando (`docker compose exec datempo rm /dados/historico_linhas.local.jsonl`).
- **Banco.** As migrações do esquema `datempo` (`banco/migracoes/`) já estão aplicadas no projeto Supabase da equipe. Num projeto novo, aplique os arquivos em ordem e exponha o esquema `datempo` na API do Supabase.
- **Chaves.** Se uma chave vazar, gere outra no painel do serviço, troque no `.env.producao` e rode `docker compose up -d`.
