import { ArrowRight, Bell, House, Map as MapaIcone, MessageCircle, Siren, UserRound, type LucideIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Fluxograma from "../componentes/Fluxograma";
import { api, type Materias } from "../lib/api";

/*
 * Como funciona: a primeira página da plataforma. O problema em poucas linhas, como usar o app aba
 * por aba, um exemplo, o fluxograma e onde cada matéria entra.
 */

type Aba = { nome: string; Icone: LucideIcon; serve: string; passos: string[] };

const ABAS: Aba[] = [
  {
    nome: "Home", Icone: House,
    serve: "Ver o que os outros passageiros estão relatando agora.",
    passos: [
      "\"Agora nas linhas\" mostra a situação estimada de cada linha, pelos relatos recentes.",
      "Toque em Relatar, escolha a linha e toque no que está vendo: lotado, parado, quebrou, chuva, alagamento, segurança ou tudo certo. Não tem texto livre nem foto.",
      "Nos relatos dos outros, confirme que ainda continua ou que já acabou. Em \"Minhas linhas\" você vê só as suas.",
    ],
  },
  {
    nome: "Mapa", Icone: MapaIcone,
    serve: "Ver onde está o problema no mapa de trem e metrô.",
    passos: [
      "As linhas aparecem coloridas pela situação de agora.",
      "Os botões do topo ligam e desligam as camadas: linhas, alagamentos (Prefeitura), segurança perto das estações (SSP-SP) e relatos.",
      "Toque numa estação para ver o resumo dela.",
    ],
  },
  {
    nome: "IA", Icone: MessageCircle,
    serve: "Conversar com a Lia antes de sair.",
    passos: [
      "Diga que está saindo e para onde vai, por exemplo: \"Vou do Grajaú para a Paulista\".",
      "A Lia confere linhas, chuva, alagamento e segurança e responde com uma decisão: pode ir, saia mais cedo ou mude o caminho, com a chegada prevista.",
      "Pergunte uma regra (\"tenho 67 anos, pago metrô?\") ou peça a mensagem de atraso para o trabalho: ela monta o texto, você copia e envia.",
    ],
  },
  {
    nome: "Perfil", Icone: UserRound,
    serve: "Deixar o app do seu jeito, sem precisar de conta.",
    passos: [
      "Marque as linhas que você usa e a estação perto de casa. Isso fica só no seu aparelho.",
      "Se quiser, crie uma conta só com usuário e senha para guardar essas escolhas e as rotas do dia a dia.",
      "Com uma rota salva, a Lia confere o trajeto num toque. Dá para apagar tudo do aparelho quando quiser.",
    ],
  },
];

const EXEMPLO = [
  { pessoa: "Estou saindo de casa agora.", lia: "Para onde você vai?" },
  { pessoa: "Para a Paulista. Saio do Grajaú.", lia: "Linha 9 parada. Vá pela 9 só até Santo Amaro e troque para a 5. Chegada às 20:49." },
  { pessoa: "Avisa o pessoal do trabalho que vou atrasar.", lia: "Pronto: \"Oi, pessoal! Vou chegar uns 20 minutos atrasado...\". Copiar e enviar." },
];

export default function ComoFunciona() {
  const [materias, setMaterias] = useState<Materias | null>(null);
  useEffect(() => {
    api.materias().then(setMaterias).catch(() => setMaterias(null));
  }, []);
  const todas = [...(materias?.no_sistema ?? []), ...(materias?.a_parte ?? [])];

  return (
    <div className="mx-auto w-full max-w-4xl space-y-12 px-4 py-8 lg:px-8">
      <header className="space-y-4">
        <p className="text-[14px] font-semibold text-marca-forte">Global Solution 2026.2 da FIAP · CitizenTech, case Citizen Assist AI</p>
        <h2 className="text-3xl leading-tight font-bold sm:text-4xl">Dá Tempo? Saiba antes de sair se o trem vai te deixar na mão</h2>
        <p className="text-lg text-apagado">
          Um app de trem e metrô de São Paulo com uma agente, a Lia, que confere a viagem antes de a pessoa sair e diz o que fazer, com a
          fonte de cada informação e sem pedir dado pessoal.
        </p>
        <div className="flex flex-wrap gap-2">
          <Link to="/sistema" className="inline-flex items-center gap-2 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">
            Abrir o sistema<ArrowRight className="size-4" aria-hidden />
          </Link>
          <Link to="/app" className="inline-flex items-center rounded-full px-5 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
            Abrir só o app (celular)
          </Link>
          <Link to="/sociedade" className="inline-flex items-center rounded-full px-5 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
            Ver o teste da sociedade
          </Link>
        </div>
      </header>

      <section className="space-y-3" aria-labelledby="titulo-problema">
        <h3 id="titulo-problema" className="text-xl font-bold">O problema</h3>
        <p className="text-[17px] leading-relaxed">
          Quando uma linha para ou um temporal alaga o caminho, a informação está espalhada: a situação de cada linha no site da sua operadora
          (são seis), o aviso de chuva no INMET, os alagamentos no CGE da Prefeitura. A pessoa descobre o problema já na plataforma, quando não
          dá mais para sair mais cedo nem avisar quem está esperando. Nos apps que comparamos, nenhum junta tudo isso numa decisão só, nem
          compara esperar com desviar. É essa lacuna que o Dá Tempo? ocupa.
        </p>
      </section>

      <section className="space-y-4" aria-labelledby="titulo-uso">
        <div className="space-y-1">
          <h3 id="titulo-uso" className="text-xl font-bold">Como usar, aba por aba</h3>
          <p className="text-[15px] text-apagado">
            O app tem quatro abas embaixo. Em qualquer uma, no topo, ficam o <span className="font-semibold text-tinta">SOS</span> e o sino de alertas.
          </p>
        </div>
        <ul className="grid gap-3 md:grid-cols-2">
          {ABAS.map(({ nome, Icone, serve, passos }) => (
            <li key={nome} className="space-y-3 rounded-xl border border-linha bg-superficie p-4">
              <div className="flex items-center gap-2.5">
                <span className="flex size-9 items-center justify-center rounded-full bg-marca-suave text-marca-forte"><Icone className="size-[18px]" aria-hidden /></span>
                <div className="min-w-0">
                  <p className="text-[16px] leading-tight font-bold">{nome}</p>
                  <p className="text-[14px] text-apagado">{serve}</p>
                </div>
              </div>
              <ol className="list-decimal space-y-1.5 pl-5 text-[15px]">
                {passos.map((p) => <li key={p}>{p}</li>)}
              </ol>
            </li>
          ))}
        </ul>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="flex gap-3 rounded-xl border border-linha bg-superficie p-4">
            <Siren className="mt-0.5 size-5 shrink-0 text-erro" aria-hidden />
            <p className="text-[15px]"><span className="font-bold">SOS: </span>abre o canal certo da linha já preenchido (SMS Segurança do Metrô, central da CPTM, da ViaQuatro ou da ViaMobilidade) e atalhos para 190, 192 e 193. O app não envia nada: quem toca em enviar é a pessoa. Não é canal de emergência.</p>
          </div>
          <div className="flex gap-3 rounded-xl border border-linha bg-superficie p-4">
            <Bell className="mt-0.5 size-5 shrink-0 text-marca-forte" aria-hidden />
            <p className="text-[15px]"><span className="font-bold">Sino de alertas: </span>mostra as linhas com problema, o aviso de chuva do INMET e o alagamento do CGE, e leva a pergunta para a Lia.</p>
          </div>
        </div>
        <p className="rounded-xl bg-marca-suave px-4 py-3 text-[15px]">
          <span className="font-bold text-marca-forte">Pelo celular: </span>abra{" "}
          <Link to="/app" className="font-mono font-semibold underline">{window.location.origin}/app</Link>.
          Só o app, em tela cheia, sem esta barra.
        </p>
      </section>

      <section className="space-y-3" aria-labelledby="titulo-exemplo">
        <h3 id="titulo-exemplo" className="text-xl font-bold">Um exemplo de conversa</h3>
        <ol className="space-y-3 rounded-2xl border border-linha bg-superficie p-4">
          {EXEMPLO.map((r) => (
            <li key={r.pessoa} className="space-y-1.5">
              <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-marca px-3.5 py-2 text-[15px] text-white">{r.pessoa}</p>
              <p className="w-fit max-w-[85%] rounded-2xl rounded-bl-md bg-fundo px-3.5 py-2 text-[15px] ring-1 ring-linha">{r.lia}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="space-y-3" aria-labelledby="titulo-fluxo">
        <h3 id="titulo-fluxo" className="text-xl font-bold">O fluxograma</h3>
        <p className="text-[16px] text-apagado">O caminho de uma pergunta, da mensagem da pessoa até a resposta, com a matéria responsável por cada etapa.</p>
        <Fluxograma />
      </section>

      <section className="space-y-3" aria-labelledby="titulo-materias">
        <h3 id="titulo-materias" className="text-xl font-bold">Onde cada matéria entra</h3>
        <p className="text-[16px] text-apagado">
          Cinco matérias viraram ferramentas da Lia; CS, MMC e COA são entregas próprias, fora do app. Cada página tem a explicação, os
          arquivos no GitHub, o teste e o checklist.
        </p>
        <ul className="grid gap-2 sm:grid-cols-2">
          {todas.map((m) => (
            <li key={m.cod}>
              <Link to={`/materias/${m.cod.toLowerCase()}`} className="flex h-full items-start gap-3 rounded-xl border border-linha bg-superficie p-3.5 hover:border-marca/50">
                <span className="mt-1.5 size-3 shrink-0 rounded-full" style={{ background: m.cor }} aria-hidden />
                <span className="min-w-0">
                  <span className="block text-[15px] font-bold">{m.cod} · {m.curto}</span>
                  <span className="block text-[14px] text-apagado">{m.no_chat}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-2" aria-labelledby="titulo-dados">
        <h3 id="titulo-dados" className="text-xl font-bold">De onde vêm os dados e os combinados</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-[16px] leading-relaxed">
          <li>Rede: GTFS da SPTrans. Situação das linhas: agregador público dos avisos das operadoras (a linha 7 não aparece). Chuva: INMET. Alagamentos: CGE e GeoSampa da Prefeitura. Segurança: SSP-SP, por estação. Energia: MCTI, Metrô, INMETRO e ANP.</li>
          <li>Não é canal oficial das operadoras nem da Defesa Civil, e avisa isso. A Lia só afirma o que as ferramentas trouxeram.</li>
          <li>O que a pessoa escreve para a Lia não fica guardado. A mensagem de atraso é montada pelo sistema, mas quem envia é a pessoa.</li>
        </ul>
        <Link to="/documentacao" className="inline-flex items-center gap-1 text-[15px] font-semibold text-marca-forte">
          Ler a documentação funcional<ArrowRight className="size-4" aria-hidden />
        </Link>
      </section>
    </div>
  );
}
