import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Fluxograma from "../componentes/Fluxograma";
import { api, type Materias } from "../lib/api";

const PASSOS = [
  { titulo: "A pessoa salva o trajeto uma vez", texto: "Escolhe a estação de saída e a de chegada. Fica guardado só no aparelho dela: sem conta, sem nome e sem localização." },
  { titulo: "Antes de sair, o app confere tudo", texto: "A situação das linhas do caminho, o aviso de chuva do INMET, os pontos de alagamento perto das estações e se é horário de pico." },
  { titulo: "Responde numa frase", texto: "\"Pode ir\", \"Saia mais cedo\" ou \"Use o Plano B\", com os motivos logo abaixo e o caminho estação por estação." },
  { titulo: "Se a linha para, mostra a saída", texto: "Compara esperar com desviar, indica até onde ainda dá para ir e explica os direitos: declaração de atraso, ônibus de apoio e ouvidorias." },
];

export default function ComoFunciona() {
  const [materias, setMaterias] = useState<Materias | null>(null);
  useEffect(() => {
    api.materias().then(setMaterias).catch(() => setMaterias(null));
  }, []);

  return (
    <div className="mx-auto w-full max-w-3xl space-y-10 px-4 py-8 lg:px-8">
      <header className="space-y-3">
        <h2 className="text-3xl leading-tight font-bold">Saiba antes de sair se o seu trem vai te deixar na mão</h2>
        <p className="text-lg text-apagado">
          O Plano B confere o trajeto de trem e metrô em São Paulo antes de você sair de casa e, quando uma linha para, mostra o que fazer.
        </p>
        <Link to="/" className="inline-flex rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">
          Conferir meu trajeto
        </Link>
      </header>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">O problema</h3>
        <p className="text-[17px] leading-relaxed">
          Milhões de pessoas dependem do trem e do metrô para trabalhar e estudar. Quando uma linha para ou um temporal alaga o caminho,
          a informação está espalhada: o status fica no site de cada operadora, o aviso de chuva fica no INMET, os alagamentos ficam no mapa da
          prefeitura e os direitos do passageiro quase ninguém conhece. A pessoa descobre o problema já na plataforma, quando não dá mais para
          sair mais cedo nem escolher outro caminho.
        </p>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-bold">Como a pessoa usa</h3>
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
          Cada parte da tela é feita pelo trabalho de uma matéria. Com o modo banca ligado, o app mostra o selo de quem fez cada parte.
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
        <Link to="/materias" className="inline-flex text-[15px] font-semibold text-marca-forte underline">
          Ver o andamento no Painel da equipe
        </Link>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">De onde vêm os dados</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-[17px] leading-relaxed">
          <li>Rede de trem e metrô: GTFS da SPTrans (estações, linhas e tempo entre estações).</li>
          <li>Situação das linhas: um agregador público que lê os avisos das seis operadoras. A linha 7 não aparece nele.</li>
          <li>Chuva: avisos ativos do INMET para a cidade de São Paulo.</li>
          <li>Alagamentos: pontos de risco do GeoSampa, da Prefeitura.</li>
          <li>Segurança: ocorrências registradas na SSP-SP, contadas por estação, sem endereço e sem dado de pessoa.</li>
          <li>Energia e CO₂: MCTI, Relatório Integrado do Metrô, INMETRO e ANP.</li>
        </ul>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">O Laboratório</h3>
        <p className="text-[17px] leading-relaxed">
          Antes de levar o app às ruas, a Simulação da sociedade testa a ideia com passageiros simulados: a auxiliar de limpeza que pega a Linha 9,
          o aposentado sem internet, a enfermeira do plantão noturno, a usuária de cadeira de rodas e outros. Cada um diz se usaria e por quê, e dá
          para ver quem fica de fora em cada canal (app, painel na estação, WhatsApp). As personas e os pesos são fictícios: servem para discutir o
          produto, não substituem o teste com pessoas de verdade.
        </p>
        <Link to="/laboratorio" className="inline-flex rounded-full px-5 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
          Abrir a simulação
        </Link>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-bold">Combinados</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-[17px] leading-relaxed">
          <li>Não é canal oficial das operadoras e avisa isso: o aviso da estação e do site da operadora vale mais.</li>
          <li>Não pede conta, nome, telefone nem localização. O trajeto fica só no aparelho da pessoa.</li>
          <li>Mostra sempre de onde veio cada informação e a hora em que foi lida.</li>
          <li>Funciona sem inteligência artificial. Com ela ligada, dado pessoal é barrado antes de qualquer chamada ao modelo.</li>
        </ul>
      </section>
    </div>
  );
}
