import { FileCode2, Folder } from 'lucide-react'
import { useState } from 'react'

export default function CodeViewer({ files = {} }) {
  const names = Object.keys(files).sort()
  const [selected, setSelected] = useState(names[0] || '')
  const active = files[selected] || ''
  return <section className="overflow-hidden rounded-2xl border border-white/10 bg-panel"><div className="border-b border-white/10 px-5 py-4"><p className="mb-1 font-mono text-[10px] uppercase tracking-[.22em] text-accent">04 / Source</p><h2 className="text-lg font-semibold">Generated files</h2></div><div className="grid min-h-[420px] md:grid-cols-[220px_1fr]"><aside className="border-b border-white/10 p-3 md:border-b-0 md:border-r">{names.map((name) => <button key={name} onClick={() => setSelected(name)} className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs ${selected === name ? 'bg-accent/10 text-accent' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}><FileCode2 size={14} />{name.replace('src/', '')}</button>)}{!names.length && <div className="flex items-center gap-2 p-3 text-xs text-slate-600"><Folder size={14} />No files yet</div>}</aside><pre className="overflow-auto bg-[#090b0f] p-5 font-mono text-xs leading-6 text-slate-300"><code>{active}</code></pre></div></section>
}
