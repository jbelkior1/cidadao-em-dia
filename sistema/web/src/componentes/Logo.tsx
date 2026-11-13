/*
 * Logo do Dá Tempo?: uma seta de rota que forma um relógio (o caminho e a hora, juntos).
 * Quadrado preto, arco e seta em laranja vivo, ponteiros em branco. Com `comNome`, vem o nome ao lado.
 */
export function MarcaDaTempo({ tamanho = 36 }: { tamanho?: number }) {
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 32 32" role="img" aria-label="Dá Tempo?" className="shrink-0">
      <rect width="32" height="32" rx="10" fill="#000000" />
      <path d="M23.5 11.5A9 9 0 1 0 25 16" fill="none" stroke="#FF5C00" strokeWidth="2.8" strokeLinecap="round" />
      <path d="M20.5 8.8l3.3 2.9-3.9 1.8" fill="none" stroke="#FF5C00" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 11v5.2l3.2 2" fill="none" stroke="#FFFFFF" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function Logo({ tamanho = 36, comNome = true }: { tamanho?: number; comNome?: boolean }) {
  return (
    <span className="flex items-center gap-2">
      <MarcaDaTempo tamanho={tamanho} />
      {comNome && <span className="text-[20px] leading-none font-extrabold tracking-tight" aria-hidden>dá tempo?</span>}
    </span>
  );
}
