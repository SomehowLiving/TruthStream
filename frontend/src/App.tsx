import React, { useState } from 'react'
import UploadZone from './components/UploadZone'
import LoadingState from './components/LoadingState'
import TruthCard from './components/TruthCard'
import ErrorBanner from './components/ErrorBanner'
import { uploadAndVerify } from './services/api'
import type { InvestigationResult } from './types'
import { Shield } from 'lucide-react'

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<InvestigationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onVerify = async () => {
    if (!file) return
    setError(null)
    setLoading(true)
    setResult(null)
    try {
      const start = Date.now()
      const res = await uploadAndVerify(file)
      // Ensure at least 3 seconds of loading to show animation
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

  return (
    <div className="min-h-screen">
      <ErrorBanner message={error} />
      <header className="max-w-4xl mx-auto px-6 py-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="text-0g-purple" />
          <div>
            <div className="text-xl text-white font-bold">TruthStream</div>
            <div className="text-xs text-gray-400">Decentralized AI Verification on 0G</div>
          </div>
        </div>
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
