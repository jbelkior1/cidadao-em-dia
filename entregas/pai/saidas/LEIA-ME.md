# Resultados das rodadas do golden

`python avaliar.py --nome antes` e `python avaliar.py --nome depois` gravam aqui `rodada_antes.json` e
`rodada_depois.json`: para cada mensagem, a resposta do agente (com dado pessoal mascarado, canais
oficiais das fichas preservados), o motivo, as fichas usadas e o veredito do juiz por critério.
`python avaliar.py --comparar antes depois` imprime a tabela antes × depois.

As duas rodadas precisam usar a mesma régua do juiz e a mesma máscara, senão a comparação não vale.
