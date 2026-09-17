import { Eraser, Sparkles } from 'lucide-react'

export const EXAMPLES = [
  'Create a modern portfolio website for an AI and data science student',
  'Create an expense tracker with income and expense categories',
  'Create a responsive food ordering website with search and a cart',
  'Create a todo application with priorities and filters',
]

export default function PromptInput({ prompt, setPrompt, onGenerate, loading }) {
  return <section className="rounded-2xl border border-white/10 bg-panel p-5 shadow-2xl shadow-black/10 sm:p-6">
    <div className="mb-5 flex items-start justify-between gap-3">
      <div><p className="mb-2 font-mono text-[10px] uppercase tracking-[.22em] text-accent">01 / Describe</p><h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">What should we build?</h1></div>
      <Sparkles className="mt-1 text-accent" size={21} />
    </div>
    <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder="Describe the website you want to create..." className="min-h-44 w-full resize-y rounded-xl border border-white/10 bg-ink/70 p-4 text-sm leading-7 text-white outline-none transition placeholder:text-slate-600 focus:border-accent/70 focus:ring-2 focus:ring-accent/10" maxLength={4000} />
    <div className="mt-2 flex justify-between font-mono text-[11px] text-slate-500"><span>Natural language is enough</span><span>{prompt.length} / 4000</span></div>
    <div className="mt-5 flex flex-col gap-3 sm:flex-row"><button onClick={onGenerate} disabled={loading || prompt.trim().length < 10} className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-ink transition hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-40"><Sparkles size={17} />{loading ? 'Generating...' : 'Generate website'}</button><button onClick={() => setPrompt('')} disabled={!prompt} className="flex items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-sm text-slate-300 transition hover:bg-white/5 disabled:opacity-30"><Eraser size={16} />Clear</button></div>
    <div className="mt-6"><p className="mb-3 text-xs font-medium text-slate-500">Try an example</p><div className="flex flex-wrap gap-2">{EXAMPLES.map((example) => <button key={example} onClick={() => setPrompt(example)} className="rounded-lg border border-white/10 px-3 py-2 text-left text-xs text-slate-400 transition hover:border-accent/50 hover:text-white">{example}</button>)}</div></div>
  </section>
}
