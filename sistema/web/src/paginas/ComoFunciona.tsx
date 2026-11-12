import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Fluxograma from "../componentes/Fluxograma";
import { api, type Materias } from "../lib/api";

const PASSOS = [
  { titulo: "A pessoa conta o que precisa", texto: "Escreve do jeito dela, sem CPF e sem nome. Se o texto tiver dado pessoal, o sistema recusa e não registra." },
  { titulo: "O sistema mostra o que entendeu", texto: "Diz qual assunto identificou e quais palavras levaram a isso. A pessoa confirma ou corrige." },
  { titulo: "Resolve na mesma conversa", texto: "Tira a dúvida, faz poucas perguntas de sim ou não, calcula a conta de luz ou confere uma mensagem suspeita." },
  { titulo: "Toda resposta vem com a fonte", texto: "Com o link oficial, a data da consulta e o aviso de que este não é um canal oficial. Quando não sabe, o sistema diz." },
];

export default function ComoFunciona() {
  const [materias, setMaterias] = useState<Materias | null>(null);
  useEffect(() => {
    api.materias().then(setMaterias).catch(() => setMaterias(null));
  }, []);

  return (
    <div className="mx-auto w-full max-w-3xl space-y-10 px-4 py-8 lg:px-8">
      <header className="space-y-3">
        <h2 className="text-3xl leading-tight font-bold">Direitos e documentos em dia, sem complicação</h2>
        <p className="text-lg text-apagado">
          O Cidadão em Dia orienta famílias de baixa renda sobre cadastro, benefícios, conta de luz e documentos, e ajuda a reconhecer golpes.
        </p>
        <Link to="/" className="inline-flex rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">
          Abrir o atendimento
        </Link>
      </header>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">O problema</h3>
        <p className="text-[17px] leading-relaxed">
          Quem mais precisa de um serviço público costuma ser quem menos consegue acompanhar as regras. Um cadastro sem atualizar pode custar
          um benefício, um desconto na conta de luz pode nunca aparecer, e uma mensagem falsa pode levar o pouco dinheiro que a família tem.
          Os canais oficiais respondem quando a pessoa pergunta. Falta alguém que explique em linguagem simples e mostre onde está escrito.
        </p>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-bold">Como o cidadão usa</h3>
        <ol className="grid gap-3 sm:grid-cols-2">
          {PASSOS.map((p, i) => (
            <li key={p.titulo} className="rounded-xl border border-linha bg-superficie p-4">
              <p className="text-sm font-semibold text-marca-forte">Passo {i + 1}</p>
              <p className="mt-1 text-[17px] font-semibold">{p.titulo}</p>
              <p className="mt-1 text-[15px] text-apagado">{p.texto}</p>
            </li>
          ))}
        </ol>
        <Fluxograma />
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-bold">As matérias por trás</h3>
        <p className="text-[17px] leading-relaxed">
          Cada parte da resposta é feita pelo trabalho de uma matéria. Com o modo banca ligado, o chat mostra o selo de quem fez cada parte.
        </p>
        <ul className="space-y-2">
          {materias?.no_sistema.map((m) => (
            <li key={m.cod}>
              <Link to={`/materias/${m.cod.toLowerCase()}`} className="flex gap-3 rounded-xl border border-linha bg-superficie p-4 hover:border-marca">
              <span className="mt-1.5 size-3 shrink-0 rounded-full" style={{ background: m.cor }} />
              <div className="min-w-0">
                <p className="font-semibold">
                  {m.cod} · {m.nome}
                </p>
                <p className="text-[15px] text-apagado">{m.papel}</p>
                <p className="mt-1 text-[14px]">
                  <span className="font-semibold">Onde aparece:</span> {m.no_chat}
                </p>
                <p className="mt-1 text-[14px] font-semibold text-marca-forte">Entender a matéria, testar e ver o checklist</p>
              </div>
              </Link>
            </li>
          ))}
        </ul>
        {materias && (
          <p className="text-[15px] text-apagado">
            Entregues à parte, fora do sistema: {materias.a_parte.map((m) => `${m.nome} (${m.cod})`).join(", ")}.
          </p>
        )}
        <Link to="/materias" className="inline-flex text-[15px] font-semibold text-marca-forte underline">
          Ver o andamento no Painel da equipe
        </Link>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">O Laboratório</h3>
        <p className="text-[17px] leading-relaxed">
          Antes de levar o produto às ruas, a Simulação da sociedade testa a ideia com pessoas simuladas: uma idosa da zona rural, uma mãe da
          periferia, um entregador, uma agente do CRAS e outras. Cada uma tem a sua internet, a sua familiaridade com o celular e a sua
          confiança no governo, e diz se usaria o produto e por quê. Dá para testar cada parte e cada canal (app, totem no CRAS, WhatsApp) e ver
          quem fica de fora. As personas e os pesos são fictícios até a MLAM trazer os dados reais.
        </p>
        <Link to="/laboratorio" className="inline-flex rounded-full px-5 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
          Abrir a simulação
        </Link>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">Combinados</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-[17px] leading-relaxed">
          <li>Não é canal oficial do governo e avisa isso em toda resposta.</li>
          <li>Não pede e não guarda CPF, nome, telefone, endereço ou senha.</li>
          <li>Só responde com o que está na base, com fonte oficial e data.</li>
          <li>Funciona sem inteligência artificial. Com ela ligada, só o texto da base vai para o modelo, nunca o que a pessoa escreveu.</li>
        </ul>
      </section>
    </div>
  );
}
