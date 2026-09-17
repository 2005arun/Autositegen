import axios from 'axios'
import { ArrowLeft, Download } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import CodeViewer from '../components/CodeViewer.jsx'
import PreviewPanel from '../components/PreviewPanel.jsx'

const api = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Project() {
  const { projectId } = useParams()
  const [project, setProject] = useState(null)
  useEffect(() => { axios.get(`${api}/api/projects/${projectId}`).then((response) => setProject(response.data)) }, [projectId])
  if (!project) return <main className="mx-auto max-w-6xl px-5 py-16 text-slate-500">Loading project...</main>
  return <main className="mx-auto max-w-[1500px] px-5 py-8 lg:px-8 lg:py-12"><div className="mb-8 flex flex-wrap items-center justify-between gap-4"><div><Link to="/" className="mb-4 flex items-center gap-2 text-xs text-slate-500 hover:text-white"><ArrowLeft size={14} /> Back to workspace</Link><h1 className="text-3xl font-semibold">{project.name}</h1><p className="mt-2 text-sm text-slate-500">{project.prompt}</p></div><a href={`${api}/api/projects/${projectId}/download`} className="flex items-center gap-2 rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-ink"><Download size={16} /> Download project</a></div><div className="space-y-5"><PreviewPanel projectId={projectId} /><CodeViewer files={project.files} /></div></main>
}
