import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { idDoAparelho } from "../abas/Feed";
import { api, type Perfil } from "../lib/api";

/*
 * Avaliar o Dá Tempo?: o formulário simples. A pessoa diz como conhece o projeto (opcional) e escreve o que
 * achou do sistema. Ninguém se identifica; o comentário aparece em "Avaliação usuários", no grupo dela.
 * O teste completo (tarefas cronometradas e notas, que a PAI pede) fica em /avaliar/teste.
 */

const PERFIS: { valor: Perfil; rotulo: string }[] = [
  { valor: "familia", rotulo: "Família" }, { valor: "faculdade", rotulo: "Faculdade" }, { valor: "trabalho", rotulo: "Trabalho" },
  { valor: "conhecido", rotulo: "Conhecido" }, { valor: "outro", rotulo: "Outro" },
];

export default function Avaliar() {
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [comentario, setComentario] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [erro, setErro] = useState("");

  async function enviar() {
    setEnviando(true);
    setErro("");
    try {
      await api.avaliar({ perfil, comentario: comentario.trim() }, idDoAparelho());
      setEnviado(true);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não deu para enviar agora. Tente de novo.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-2xl space-y-6 px-4 py-8 lg:px-8">
      <header className="space-y-2">
        <Link to="/avaliacao" className="inline-flex items-center gap-1 text-[14px] font-semibold text-marca-forte"><ArrowLeft className="size-4" aria-hidden />Avaliação usuários</Link>
        <h2 className="text-2xl font-bold">Avaliar o Dá Tempo?</h2>
      </header>

      {enviado ? (
        <section className="space-y-3 rounded-2xl border border-linha bg-superficie p-6 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-full bg-marca-suave text-marca-forte"><Check className="size-6" aria-hidden /></span>
          <p className="text-xl font-bold">Obrigado pela avaliação!</p>
          <Link to="/avaliacao" className="inline-flex items-center gap-1 text-[15px] font-semibold text-marca-forte">Ver as avaliações<ArrowRight className="size-4" aria-hidden /></Link>
        </section>
      ) : (
        <section className="space-y-5 rounded-2xl border border-linha bg-superficie p-5">
          <div className="space-y-2">
            <p className="text-[15px] font-semibold">Como você conhece o projeto? <span className="font-normal text-apagado">(opcional)</span></p>
            <div className="flex flex-wrap gap-2">
              {PERFIS.map((p) => (
                <button key={p.valor} type="button" onClick={() => setPerfil(perfil === p.valor ? null : p.valor)} aria-pressed={perfil === p.valor}
                  className={`rounded-full px-4 py-2 text-[15px] font-semibold ring-1 ring-inset ${perfil === p.valor ? "bg-marca text-white ring-marca" : "ring-linha hover:ring-marca/50"}`}>
                  {p.rotulo}
                </button>
              ))}
            </div>
          </div>
          <label className="block space-y-1.5">
            <span className="text-[15px] font-semibold">O que você achou do sistema?</span>
            <textarea value={comentario} onChange={(e) => setComentario(e.target.value)} maxLength={500} rows={5}
              className="w-full rounded-xl border border-linha bg-superficie px-3.5 py-2.5 text-[16px]"
              placeholder="Do que gostou, o que estranhou, o que faria você usar." />
            <span className="block text-right text-[13px] text-apagado">{comentario.length}/500</span>
          </label>
          <p className="text-[13px] text-apagado">Não pedimos nome, e-mail nem telefone. Textos com dado pessoal ou link são recusados.</p>
          {erro && <p className="rounded-xl bg-erro/10 px-3.5 py-2.5 text-[14px] font-semibold text-erro" role="alert">{erro}</p>}
          <button type="button" disabled={enviando || !comentario.trim()} onClick={() => void enviar()}
            className="inline-flex items-center gap-1 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte disabled:opacity-40">
            {enviando ? "Enviando..." : "Enviar avaliação"}
          </button>
        </section>
      )}

      <p className="text-[14px] text-apagado">
        Tem uns 10 minutos? <Link to="/avaliar/teste" className="font-semibold text-marca-forte underline">Faça o teste completo</Link>, com três tarefas no app e notas de 1 a 5.
      </p>
    </div>
  );
}
