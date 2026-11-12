# Fontes da pesquisa de mobilidade (conferência de 12/11/2026)

Observação: o WebFetch devolve um resumo da página, não o HTML bruto. Os trechos entre aspas vieram desses resumos; a equipe deve reconferir os trechos críticos na página.

## Abriram e foram usadas
- https://www.metro.sp.gov.br/pt_BR/fale-conosco/faq/ (declaração de ocorrência, SMS Segurança)
- https://www.metro.sp.gov.br/pt_BR/fale-conosco/ (Central 0800 770 7722, SMS, ouvidoria)
- https://www.metro.sp.gov.br/sua-viagem/direto-metro/ (situação das linhas)
- https://www.metro.sp.gov.br/sua-viagem/declaracao-ocorrencias/politica-comunicacao-anormalidade/
- https://www.metro.sp.gov.br/pt_BR/sua-viagem/bilhetes-cartoes/ (integração, tarifas, isenções)
- https://www.metro.sp.gov.br/wp-content/uploads/2023/10/Carta-de-Servic%CC%A7os-Metro%CC%82.pdf (lida com pdftotext; documento de out/2023)
- https://www.metro.sp.gov.br/2026/09/21/metro-e-corpo-de-bombeiros-realizam-simulados-de-evacuacao-e-resgate-na-linha-17-ouro/
- https://www.cptm.sp.gov.br/cptm/contato/fale-conosco
- https://www.cptm.sp.gov.br/cptm/sua-viagem/acessibilidade
- https://www.cptm.sp.gov.br/cptm/esg-consciente/praticas-de-governanca/canal-de-denuncias
- https://www.cptm.sp.gov.br/cptm/contato/perguntas_frequentes
- https://trilhos.motiva.com.br/ (ViaQuatro e ViaMobilidade; os domínios viaquatro.com.br e viamobilidade.com.br redirecionam para cá)
- https://trilhos.motiva.com.br/linha-4-amarela/declaracao-de-ocorrencias, /contatos, /perdidos-e-achados, /guia-de-uso
- https://trilhos.motiva.com.br/viamobilidade8e9, /declaracao-de-ocorrencias, /contatos, /guia-de-uso
- https://trilhos.motiva.com.br/linha-5-lilas/ (só a página inicial)
- https://www.sptrans.com.br/ , /atende/ , /tarifas/ , /historico-de-tarifas/ , /fale-conosco/ouvidoria-sptrans/
- https://www.sptrans.com.br/perguntas-e-respostas/?sobre=gratuidade-60-64 , ?sobre=bilhete-pcd , ?sobre=bilhete-pessoa-idosa
- https://prefeitura.sp.gov.br/web/mobilidade/w/institucional/sptrans/acesso_a_informacao/366625 (convênio PAESE)
- https://prefeitura.sp.gov.br/w/noticia/sptrans-disponibiliza-onibus-para-atendimento-entre-as-estacoes-pinheiros-e-ceasa (2018)
- https://prefeitura.sp.gov.br/w/noticia/plano-de-atendimento-entre-empresas-de-transporte-em-situacao-de-emergencia-e-acionado-entre-estacoes-santo-amaro-e-berrini-da-cptm (2019)
- https://www.spsemprealerta.sp.gov.br/ , /orientacoes/inundacoes/ , /orientacoes/tempestades-raios-e-granizo/ , /defesa-civil-alerta/temporais/
- https://www.defesacivil.sp.gov.br (página inicial)
- https://www.gov.br/pt-br/servicos/solicitar-cadastro-para-recebimento-de-avisos-e-alertas-de-desastres
- https://www.gov.br/celularseguro
- https://servicos.sp.gov.br/fcarta/58530894-E128-4E25-ADEC-AB177394802A (Carta de Serviços da Delegacia Eletrônica)
- https://servicos.sp.gov.br/fcarta/13E3EA16-EA64-40AA-B526-F8EEF0C7E0BF (Canal de Denúncia CPTM)
- https://www.artesp.sp.gov.br/ e /artesp/canais-de-comunicacao/ouvidoria
- https://www.planalto.gov.br/ccivil_03/leis/2003/l10.741.htm (Estatuto da Pessoa Idosa, art. 39)
- https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13460.htm (Lei 13.460/2017)

## Não abriram ou vieram vazias
- https://www.metro.sp.gov.br/wp-content/uploads/2026/07/guia_do_passageiro_online.html : erro 404 (também por curl). Era a fonte esperada de "nunca descer à via"; orientação NÃO confirmada.
- https://www.metro.sp.gov.br/pt_BR/fale-conosco/achados-e-perdidos/ : 404.
- https://metro.sp.gov.br/fale-conosco/faq.aspx e https://metro.sp.gov.br/mobile/declaracao-ocorrencias/comunicacao-anormalidade.aspx : erro de certificado.
- http://cge.prefeitura.sp.gov.br/v3/dicas.jsp : erro de certificado (orientação do CGE não lida).
- https://delegaciadigital.policia-civil.sp.gov.br/ (para onde a Delegacia Eletrônica redireciona) e /duvidas-frequentes/ : só "Carregando aplicação".
- https://www.ssp.sp.gov.br/servicos/delegacia-eletronica : só o título "Portal SSP".
- https://www.metro.sp.gov.br/sua-viagem/declaracao-ocorrencias/ : só os títulos dos links.
- https://www.cptm.sp.gov.br/cptm , /sua-viagem , /transparencia/carta-de-servicos , /Pages/atendimento.aspx : abriram, mas sem o conteúdo pedido (a Situação das Linhas aparecia como "Carregando...").
- https://www.defesacivil.sp.gov.br : abriu, sem os números 199 e 40199 (vieram do spsemprealerta.sp.gov.br).

## Dúvidas abertas
- Declaração de atraso da CPTM: sem passo a passo oficial lido.
- Orientação "não descer na via" quando o trem para: sem página oficial lida.
- PAESE: sem página explicativa atual ao passageiro; gratuidade não confirmada.
- Delegacia de Polícia do Metropolitano (Delpom): nenhuma página oficial aberta; não entrou no catálogo.
- Artesp: lista de concessões que ela fiscaliza não foi lida.
- Páginas com instrução dirigida ao agente: nenhuma encontrada.
