import { ArrowRight } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Fluxograma from "../componentes/Fluxograma";
import { api, type Materias } from "../lib/api";

/*
 * Como funciona: a primeira página da plataforma. O problema, como o sistema resolve,
 * o fluxograma e onde cada matéria entra, dentro e fora do sistema.
 */

const SOLUCAO = [
  { titulo: "Uma conversa só", texto: "A pessoa diz que está saindo e para onde vai. A Lia confere linhas, chuva, alagamento, segurança e o que os passageiros relataram." },
  { titulo: "Uma decisão só", texto: "Em vez de quatro informações soltas, uma frase: pode ir, saia mais cedo ou mude o caminho, com a chegada prevista e o desvio." },
  { titulo: "Os passageiros contam o que veem", texto: "Relatos em dois toques (lotado, parado, alagado), sem texto livre nem foto, marcados como estimativa e não como dado oficial." },
  { titulo: "Sem dado pessoal", texto: "Não precisa de conta. CPF, telefone, e-mail e endereço são barrados antes de chegar à IA. A conta, se a pessoa quiser, é só usuário e senha." },
];

const ABAS = [
  { aba: "Home", texto: "Relatos dos passageiros por linha e atalho para perguntar à Lia." },
  { aba: "Mapa", texto: "Linhas pela situação atual, alagamentos, segurança perto das estações e relatos." },
  { aba: "IA", texto: "A Lia: confere a viagem, explica regras e direitos pelas fichas e monta a mensagem de atraso." },
  { aba: "Perfil", texto: "Minhas linhas, estação de casa e rotas salvas, com conferência em um toque." },
];

const EXEMPLO = [
  { pessoa: "Estou saindo de casa agora.", lia: "Para onde você vai?" },
  { pessoa: "Para a Paulista. Saio do Grajaú.", lia: "Linha 9 parada (simulação). Vá pela 9 só até Santo Amaro e troque para a 5. Chegada às 20:49." },
  { pessoa: "Avisa o pessoal do trabalho que vou atrasar.", lia: "Pronto: \"Oi, pessoal! Vou chegar uns 20 minutos atrasado...\". Copiar e enviar." },
];

export default function ComoFunciona() {
  const [materias, setMaterias] = useState<Materias | null>(null);
  useEffect(() => {
    api.materias().then(setMaterias).catch(() => setMaterias(null));
  }, []);

  return (
    <div className="mx-auto w-full max-w-4xl space-y-12 px-4 py-8 lg:px-8">
      <header className="space-y-4">
        <p className="text-[14px] font-semibold text-marca-forte">Global Solution 2026.2 da FIAP: CitizenTech, case Citizen Assist AI</p>
        <h2 className="text-3xl leading-tight font-bold sm:text-4xl">Dá Tempo? Saiba antes de sair se o trem vai te deixar na mão</h2>
        <p className="text-lg text-apagado">
          Um app de trem e metrô de São Paulo com uma agente, a Lia, que confere a viagem antes de a pessoa sair e diz o que fazer, com a
          fonte de cada informação e sem pedir dado pessoal.
        </p>
        <div className="flex flex-wrap gap-2">
          <Link to="/sistema" className="inline-flex items-center gap-2 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">
            Abrir o sistema<ArrowRight className="size-4" aria-hidden />
          </Link>
          <Link to="/sociedade" className="inline-flex items-center rounded-full px-5 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
            Ver o teste da sociedade
          </Link>
        </div>
      </header>

      <section className="space-y-3" aria-labelledby="titulo-problema">
        <h3 id="titulo-problema" className="text-xl font-bold">O problema</h3>
        <p className="text-[17px] leading-relaxed">
          Milhões de pessoas dependem do trem e do metrô em São Paulo. Quando uma linha para ou um temporal alaga o caminho, a informação está
          espalhada: a situação de cada linha fica no site da sua operadora (são seis), o aviso de chuva no INMET, os alagamentos no CGE da
          Prefeitura e os direitos do passageiro quase ninguém conhece. A pessoa descobre o problema já na plataforma, quando não dá mais para
          sair mais cedo nem avisar quem está esperando.
        </p>
        <p className="text-[17px] leading-relaxed">
          Apps de rota e os canais das operadoras mostram partes dessa informação, cada um no seu canto. Nos que comparamos, nenhum junta a
          situação das seis operadoras, o aviso de chuva, os alagamentos e a segurança perto da estação numa decisão só, nem compara esperar
          com desviar quando a linha para. É essa lacuna que o Dá Tempo? ocupa.
        </p>
      </section>

      <section className="space-y-4" aria-labelledby="titulo-solucao">
        <h3 id="titulo-solucao" className="text-xl font-bold">Como o sistema resolve</h3>
        <ul className="grid gap-3 sm:grid-cols-2">
          {SOLUCAO.map((s) => (
            <li key={s.titulo} className="rounded-xl border border-linha bg-superficie p-4">
              <p className="text-[16px] font-bold">{s.titulo}</p>
              <p className="mt-1 text-[15px] text-apagado">{s.texto}</p>
            </li>
          ))}
        </ul>
        <div className="rounded-xl border border-linha bg-superficie p-4">
          <p className="text-[15px] font-bold">O app tem quatro abas, com SOS e sinal de alerta em todas</p>
          <dl className="mt-2 grid gap-x-6 gap-y-2 text-[15px] sm:grid-cols-2">
            {ABAS.map((a) => (
              <div key={a.aba}>
                <dt className="font-semibold">{a.aba}</dt>
                <dd className="text-apagado">{a.texto}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section className="space-y-4" aria-labelledby="titulo-exemplo">
        <h3 id="titulo-exemplo" className="text-xl font-bold">Um exemplo de uso</h3>
        <ol className="space-y-3 rounded-2xl border border-linha bg-superficie p-4">
          {EXEMPLO.map((r, i) => (
            <li key={i} className="space-y-1.5">
              <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-marca px-3.5 py-2 text-[15px] text-white">{r.pessoa}</p>
              <p className="w-fit max-w-[85%] rounded-2xl rounded-bl-md bg-fundo px-3.5 py-2 text-[15px] ring-1 ring-linha">{r.lia}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="space-y-3" aria-labelledby="titulo-fluxo">
        <h3 id="titulo-fluxo" className="text-xl font-bold">O fluxograma</h3>
        <p className="text-[16px] text-apagado">O caminho de uma pergunta: da mensagem da pessoa até a resposta, com a matéria responsável por cada etapa.</p>
        <Fluxograma />
      </section>

      <section className="space-y-4" aria-labelledby="titulo-materias">
        <h3 id="titulo-materias" className="text-xl font-bold">Onde cada matéria entra</h3>
        <p className="text-[17px] leading-relaxed">
          Cada professor avalia a entrega do seu enunciado, no formato pedido. Dentro do sistema, cinco matérias viraram ferramentas que a Lia
          usa; as outras três são entregues à parte. Na página de cada matéria ficam a explicação, os arquivos no GitHub, o teste e o checklist.
        </p>
        <ul className="space-y-3">
          {materias?.no_sistema.map((m) => (
            <li key={m.cod} className="rounded-xl border border-linha bg-superficie p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="size-3 rounded-full" style={{ background: m.cor }} aria-hidden />
                <p className="font-bold">{m.cod} · {m.nome}</p>
              </div>
              <div className="mt-3 grid gap-3 text-[15px] sm:grid-cols-2">
                <div>
                  <p className="text-[13px] font-semibold text-apagado">No sistema</p>
                  <p>{m.no_chat}</p>
                </div>
                <div>
                  <p className="text-[13px] font-semibold text-apagado">Entrega ao professor</p>
                  <p>{m.entrega}</p>
                </div>
              </div>
              <Link to={`/materias/${m.cod.toLowerCase()}`} className="mt-3 inline-flex items-center gap-1 text-[14px] font-semibold text-marca-forte">
                Abrir a página da matéria<ArrowRight className="size-4" aria-hidden />
              </Link>
            </li>
          ))}
        </ul>
        {!!materias?.a_parte.length && (
          <div className="space-y-3 rounded-2xl border border-dashed border-linha p-4">
            <p className="text-[15px] font-bold">Entregues à parte, fora do sistema</p>
            <p className="text-[15px] text-apagado">Estas atividades não fazem sentido dentro da conversa, então seguem só o que o enunciado pede, no formato dele.</p>
            <ul className="grid gap-3 sm:grid-cols-3">
              {materias.a_parte.map((m) => (
                <li key={m.cod} className="rounded-xl bg-superficie p-4 ring-1 ring-linha">
                  <p className="font-bold">{m.cod} · {m.nome}</p>
                  <p className="mt-1 text-[14px]">{m.entrega}</p>
                  <Link to={`/materias/${m.cod.toLowerCase()}`} className="mt-2 inline-flex items-center gap-1 text-[14px] font-semibold text-marca-forte">
                    Abrir a página<ArrowRight className="size-4" aria-hidden />
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="space-y-3" aria-labelledby="titulo-dados">
        <h3 id="titulo-dados" className="text-xl font-bold">De onde vêm os dados</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-[17px] leading-relaxed">
          <li>Rede de trem e metrô: GTFS da SPTrans (estações, linhas e tempo entre estações).</li>
          <li>Situação das linhas: agregador público que lê os avisos das seis operadoras. A linha 7 não aparece nele.</li>
          <li>Chuva: avisos ativos do INMET para a cidade de São Paulo.</li>
          <li>Alagamentos: CGE da Prefeitura (estado de atenção ou alerta e pontos do dia) e áreas de risco do GeoSampa.</li>
          <li>Segurança: ocorrências registradas na SSP-SP, contadas por estação, sem endereço e sem dado de pessoa.</li>
          <li>Energia e CO₂: MCTI, Relatório Integrado do Metrô, INMETRO e ANP.</li>
        </ul>
      </section>

      <section className="space-y-3" aria-labelledby="titulo-combinados">
        <h3 id="titulo-combinados" className="text-xl font-bold">Combinados</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-[17px] leading-relaxed">
          <li>Não é canal oficial das operadoras nem da Defesa Civil, nem canal de emergência, e avisa isso.</li>
          <li>A Lia só afirma o que as ferramentas trouxeram; o que não sabe, diz que não sabe.</li>
          <li>O que a pessoa escreve para a Lia não fica guardado. Sem conta, só a estação de casa e as linhas marcadas ficam no aparelho.</li>
          <li>A mensagem de atraso é montada pelo sistema, mas quem envia é a pessoa, pelo canal que preferir.</li>
        </ul>
        <Link to="/documentacao" className="inline-flex items-center gap-1 text-[15px] font-semibold text-marca-forte">
          Ler a documentação funcional completa<ArrowRight className="size-4" aria-hidden />
        </Link>
      </section>
    </div>
  );
}
