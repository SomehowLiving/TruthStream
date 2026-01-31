import React, { useState } from 'react'
import UploadZone from './components/UploadZone'
import LoadingState from './components/LoadingState'
import TruthCard from './components/TruthCard'
import ErrorBanner from './components/ErrorBanner'
import {About} from './components/About'
import { uploadAndVerify } from './services/api'
import type { InvestigationResult } from './types'
import { Shield, Info } from 'lucide-react'  // Add Info icon

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<InvestigationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showAbout, setShowAbout] = useState(false)  // ADD THIS STATE

  const onVerify = async () => {
    if (!file) return
    setError(null)
    setLoading(true)
    setResult(null)
    try {
      const start = Date.now()
      const res = await uploadAndVerify(file)
      const elapsed = Date.now() - start
      if (elapsed < 3000) await new Promise((r) => setTimeout(r, 3000 - elapsed))
      setResult(res)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const verifyAnother = () => {
    setFile(null)
    setResult(null)
    setError(null)
  }

  // ADD THIS: About page view
  if (showAbout) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0A0A0A] to-[#1A1A2E]">
        <header className="max-w-4xl mx-auto px-6 py-8 flex items-center justify-between">
          <div 
            className="flex items-center gap-3 cursor-pointer"
            onClick={() => setShowAbout(false)}
          >
            <Shield className="text-[#6B46C1]" />
            <div>
              <div className="text-xl text-white font-bold">TruthStream</div>
              <div className="text-xs text-gray-400">Decentralized AI Verification on 0G</div>
            </div>
          </div>
        </header>
        <About />
      </div>
    )
  }

  // MAIN APP VIEW (your existing code)
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0A0A] to-[#1A1A2E]">
      <ErrorBanner message={error} />
      <header className="max-w-4xl mx-auto px-6 py-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="text-[#6B46C1]" />
          <div>
            <div className="text-xl text-white font-bold">TruthStream</div>
            <div className="text-xs text-gray-400">Decentralized AI Verification on 0G</div>
          </div>
        </div>
        
        {/* ADD THIS BUTTON */}
        <button 
          onClick={() => setShowAbout(true)}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <Info size={18} />
          <span className="text-sm">About</span>
        </button>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12 space-y-6">
        {!result && !loading && (
          <UploadZone file={file} setFile={setFile} onVerify={onVerify} loading={loading} />
        )}

        {loading && <LoadingState />}

        {result && <TruthCard result={result} onVerifyAnother={verifyAnother} />}
      </main>
    </div>
  )
}