# Versão de antes da melhoria

Os três arquivos como estavam na rodada "antes" do golden:

- `fichas.py`: palavra-chave casava só por texto exato (sem `#` como dígito);
- `guardrails.py`: "meu celular", "meu telefone" etc. contavam como dado pessoal em qualquer frase;
- `FT-04_gratuidades.md`: palavras-chave com "60 anos" e "65 anos", sem "## anos" nem "pago metrô".

Os comentários desses arquivos podem citar a melhoria; o que vale é o código. O script
`../../rodar_antes_e_depois.py` troca estes arquivos por um momento para rodar a rodada "antes" e devolve
a versão atual em seguida.
