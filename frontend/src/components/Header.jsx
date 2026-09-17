import { Code2, History, Plus } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

export default function Header() {
  const location = useLocation()
  return <header className="border-b border-white/10 bg-ink/90 backdrop-blur-xl sticky top-0 z-20">
    <div className="mx-auto flex max-w-[1500px] items-center justify-between px-5 py-4 lg:px-8">
      <Link to="/" className="flex items-center gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-accent text-ink"><Code2 size={19} /></span>
        <span className="text-lg font-semibold tracking-tight">AutoSite<span className="text-accent">Gen</span></span>
      </Link>
      <nav className="flex items-center gap-2 text-sm text-slate-400">
        <Link to="/" className={`hidden items-center gap-2 rounded-lg px-3 py-2 transition hover:bg-white/5 hover:text-white sm:flex ${location.pathname === '/' ? 'text-white' : ''}`}><Plus size={16} /> New project</Link>
        <Link to="/#history" className="flex items-center gap-2 rounded-lg px-3 py-2 transition hover:bg-white/5 hover:text-white"><History size={16} /> History</Link>
      </nav>
    </div>
  </header>
}
