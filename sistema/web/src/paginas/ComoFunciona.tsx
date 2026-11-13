import { ArrowRight } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Fluxograma from "../componentes/Fluxograma";
import { api, type Materias } from "../lib/api";

/* Case norteador: o que o caso pede, como a Lia responde e o que cada matéria faz dentro e fora do sistema. */

const PEDIDOS = [
  { pedido: "Orientar o cidadão no dia a dia", resposta: "A Lia acompanha a ida e a volta de trem e metrô e diz o que fazer quando algo dá errado." },
  { pedido: "Toda orientação com fonte", resposta: "Cada cartão traz de onde veio a informação e a hora da leitura: operadoras, INMET, CGE, SSP-SP, sites oficiais." },
  { pedido: "Avisar as limitações", resposta: "A Lia diz quando não sabe, avisa que não é canal oficial e que o aviso da estação vale mais." },
  { pedido: "Sem dados pessoais", resposta: "Sem conta, sem nome, sem localização. CPF, telefone ou endereço são barrados antes de chegar ao modelo de IA." },
];

const ROTEIRO = [
  { pessoa: "Estou saindo de casa agora.", auxilia: "Para onde você vai?" },
  { pessoa: "Para a Paulista. Saio do Grajaú.", auxilia: "Linha 9 parada (simulação). Vá pela 9 só até Santo Amaro e troque para a 5. Chegada às 20:49." },
  { pessoa: "Avisa o pessoal do trabalho que vou atrasar.", auxilia: "Pronto: \"Oi, pessoal! Vou chegar uns 20 minutos atrasado...\". Copiar e enviar." },
];

export default function ComoFunciona() {
  const [materias, setMaterias] = useState<Materias | null>(null);
  useEffect(() => {
    api.materias().then(setMaterias).catch(() => setMaterias(null));
  }, []);

  return (
    <div className="mx-auto w-full max-w-4xl space-y-10 px-4 py-8 lg:px-8">
      <header className="space-y-3">
        <p className="text-[13px] font-semibold tracking-wide text-marca-forte uppercase">Global Solution 2026.2 · CitizenTech · Citizen Assist AI</p>
        <h2 className="text-3xl leading-tight font-bold">Dá Tempo? A Lia acompanha você no trem e no metrô</h2>
        <p className="text-lg text-apagado">
          O case pede um assistente que oriente o cidadão com fonte, avise as limitações e não use dados pessoais. A nossa resposta é uma
          conversa só: a pessoa diz que está saindo, a Lia confere linhas, chuva, alagamento e caminho e diz o que fazer.
        </p>
        <Link to="/" className="inline-flex items-center gap-2 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">
          Abrir o sistema<ArrowRight className="size-4" aria-hidden />
        </Link>
      </header>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">O problema</h3>
        <p className="text-[17px] leading-relaxed">
          Milhões de pessoas dependem do trem e do metrô em São Paulo. Quando uma linha para ou um temporal alaga o caminho, a informação está
          espalhada: o status fica no site de cada operadora, o aviso de chuva no INMET, os alagamentos no CGE da Prefeitura e os direitos do
          passageiro quase ninguém conhece. A pessoa descobre o problema já na plataforma, quando não dá mais para sair mais cedo nem avisar quem
          está esperando.
        </p>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-bold">O que o case pede e onde está</h3>
        <ul className="grid gap-3 sm:grid-cols-2">
          {PEDIDOS.map((p) => (
            <li key={p.pedido} className="rounded-xl border border-linha bg-superficie p-4">
              <p className="text-[15px] font-bold">{p.pedido}</p>
              <p className="mt-1 text-[15px] text-apagado">{p.resposta}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-bold">O roteiro do pitch</h3>
        <ol className="space-y-3 rounded-2xl border border-linha bg-superficie p-4">
          {ROTEIRO.map((r, i) => (
            <li key={i} className="space-y-1.5">
              <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-marca px-3.5 py-2 text-[15px] text-white">{r.pessoa}</p>
              <p className="w-fit max-w-[85%] rounded-2xl rounded-bl-md bg-fundo px-3.5 py-2 text-[15px] ring-1 ring-linha">{r.auxilia}</p>
            </li>
          ))}
        </ol>
        <Fluxograma />
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-bold">O que cada matéria faz, dentro e fora do sistema</h3>
        <p className="text-[17px] leading-relaxed">
          Dentro do sistema, cada matéria é uma ferramenta que a Lia chama. Fora dele, cada professor recebe a entrega no formato do
          enunciado. Na página de cada matéria ficam a explicação, o teste individual e o checklist da entrega.
        </p>
        <ul className="space-y-3">
          {materias?.no_sistema.map((m) => (
            <li key={m.cod} className="rounded-xl border border-linha bg-superficie p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="size-3 rounded-full" style={{ background: m.cor }} />
                <p className="font-bold">{m.cod} · {m.nome}</p>
              </div>
              <div className="mt-3 grid gap-3 text-[15px] sm:grid-cols-2">
                <div>
                  <p className="text-[12px] font-semibold tracking-wide text-apagado uppercase">No sistema</p>
                  <p>{m.no_chat}</p>
                </div>
                <div>
                  <p className="text-[12px] font-semibold tracking-wide text-apagado uppercase">Entrega ao professor</p>
                  <p>{m.entrega}</p>
                </div>
              </div>
              <Link to={`/materias/${m.cod.toLowerCase()}`} className="mt-3 inline-flex items-center gap-1 text-[14px] font-semibold text-marca-forte">
                Entenda, teste e checklist<ArrowRight className="size-4" aria-hidden />
              </Link>
            </li>
          ))}
        </ul>
        {!!materias?.a_parte.length && (
          <div className="space-y-3 rounded-2xl border border-dashed border-linha p-4">
            <p className="text-[15px] font-bold">Entregues à parte, fora do sistema</p>
            <p className="text-[15px] text-apagado">
              Estas atividades não fazem sentido dentro da conversa, então seguem só o que o enunciado pede, no formato dele.
            </p>
            <ul className="grid gap-3 sm:grid-cols-2">
              {materias.a_parte.map((m) => (
                <li key={m.cod} className="rounded-xl bg-superficie p-4 ring-1 ring-linha">
                  <p className="font-bold">{m.cod} · {m.nome}</p>
                  <p className="mt-1 text-[14px]"><span className="font-semibold">Entrega: </span>{m.entrega}</p>
                  <Link to={`/materias/${m.cod.toLowerCase()}`} className="mt-2 inline-flex items-center gap-1 text-[14px] font-semibold text-marca-forte">
                    Entenda, teste e checklist<ArrowRight className="size-4" aria-hidden />
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">De onde vêm os dados</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-[17px] leading-relaxed">
          <li>Rede de trem e metrô: GTFS da SPTrans (estações, linhas e tempo entre estações).</li>
          <li>Situação das linhas: agregador público que lê os avisos das seis operadoras. A linha 7 não aparece nele.</li>
          <li>Chuva: avisos ativos do INMET para a cidade de São Paulo.</li>
          <li>Alagamentos ao vivo: CGE da Prefeitura (estado de atenção ou alerta e pontos do dia). Áreas de risco: GeoSampa.</li>
          <li>Segurança: ocorrências registradas na SSP-SP, contadas por estação, sem endereço e sem dado de pessoa.</li>
          <li>Energia e CO₂: MCTI, Relatório Integrado do Metrô, INMETRO e ANP.</li>
          <li>Ficaram de fora por não serem abertos: alertas do Waze (só para parceiros) e posição dos ônibus da SPTrans (exige cadastro aprovado).</li>
        </ul>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">Combinados</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-[17px] leading-relaxed">
          <li>Não é canal oficial das operadoras nem da Defesa Civil, e avisa isso.</li>
          <li>A Lia só afirma o que as ferramentas trouxeram; o que não sabe, diz que não sabe.</li>
          <li>A única lembrança é a estação de casa, guardada no aparelho da pessoa.</li>
          <li>A mensagem de atraso é montada pelo sistema, mas quem envia é a pessoa, pelo canal que preferir.</li>
        </ul>
        <Link to="/sociedade" className="inline-flex rounded-full px-5 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
          Ver a sociedade usando o sistema
        </Link>
      </section>
    </div>
  );
}
