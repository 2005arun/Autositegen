import { Routes, Route } from 'react-router-dom'
import Header from './components/Header.jsx'
import Home from './pages/Home.jsx'
import Project from './pages/Project.jsx'

export default function App() {
  return <div className="min-h-screen bg-ink text-white"><Header /><Routes><Route path="/" element={<Home />} /><Route path="/project/:projectId" element={<Project />} /></Routes></div>
}
