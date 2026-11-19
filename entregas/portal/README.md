# Entrega no portal, matéria por matéria

Cada professor pede a entrega num formato próprio, e o formato também vale nota. Esta pasta tem o arquivo pronto de cada matéria, no formato do enunciado dela. Os pacotes finais saem com:

```bash
python scripts/montar_entregas.py --url https://SEU-DOMINIO
```

O script grava tudo em `entregas/portal/saida/` (fora do git) e lista o que ainda está entre colchetes, por preencher. Sem `--url`, a linha com o endereço da plataforma sai do texto.

| Matéria | O que vai ao portal | Arquivo pronto | O que ainda falta |
|---|---|---|---|
| **PCP** | Só um .txt com 5 campos (nome do assistente, público, integrantes e RM, link do repositório, link do vídeo) | [`pcp/PCP_entrega.txt`](pcp/PCP_entrega.txt); repositório público em https://github.com/jbelkior1/citizen-assist-ai | Testar com 3 pessoas (10 atendimentos) antes do vídeo, gravar o vídeo técnico de 5 a 8 min, colar os links |
| **DSA** | Código, documentação, Big-O e evidências (formato livre) | [`dsa/LEIA-ME.txt`](dsa/LEIA-ME.txt); o script gera `DSA_entrega.zip` | Conferir na tela do portal o formato aceito |
| **SERS** | Só um .txt com nome completo e RM, link do repositório e link do vídeo | [`sers/SERS_entrega.txt`](sers/SERS_entrega.txt) | Testes com usuários em `entregas/sers/TESTES_USUARIOS.md`, conferir os números lidos de PDF, vídeo de até 3 min, colar o link |
| **MLAM** | Base .csv, códigos .py e relatório .pdf, postados soltos, **sem links** | O script gera `MLAM_para_enviar/`; instruções em [`mlam/COMO_ENVIAR.txt`](mlam/COMO_ENVIAR.txt) (não vai ao portal) | Conferir quantos arquivos o portal aceita, conferir o cadastro do grupo e postar |
| **PAI** | Protótipo testável, fichas, juiz com antes e depois, relatório dos testes e justificativas (formato livre) | [`pai/LEIA-ME.txt`](pai/LEIA-ME.txt); o script gera `PAI_entrega.zip` | Testes com 5 pessoas (tempo e facilidade) em `entregas/pai/TESTES_USUARIOS.md`, confirmar o formato de envio |
| **Vídeo pitch** | Entrega própria do portal (GS2026.2 - ENTREGA VÍDEO PITCH) | Modelo em [`pitch/PITCH_entrega.txt`](pitch/PITCH_entrega.txt) | Gravar o pitch de até 3 min, sem narração por IA |

## Antes de enviar qualquer uma

1. **Integrantes no portal:** em cada entrega, inserir os três integrantes com RM. Em 13/11 o campo mostrava só um; sem isso a nota pode não chegar aos outros dois.
2. **Prazo:** 19/11/2026, adotar 23h55 (o menor horário entre os enunciados). Depois do prazo o portal não aceita envio nem troca.
3. **Links:** abrir cada link (repositório, vídeos, plataforma) numa janela anônima antes de enviar. Vídeo do YouTube como "não listado", nunca "privado".
4. **Plataforma:** publicar na VPS (`DEPLOY.md`) e rodar o script de novo com `--url`.
