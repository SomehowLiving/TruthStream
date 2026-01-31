import React, { useState } from 'react'
import type { InvestigationResult } from '../types'
import { truncateMiddle } from '../lib/utils'
import { Clipboard, ExternalLink, Check, X, Copy } from 'lucide-react'

type Props = {
  result: InvestigationResult
  onVerifyAnother: () => void
}

function VerdictBadge({ verdict }: { verdict: string }) {
  const map: Record<string, string> = {
    VERIFIED: 'bg-emerald-500/20 text-emerald-400',
    LIKELY_FALSE: 'bg-red-500/20 text-red-400',
    UNCERTAIN: 'bg-yellow-500/20 text-yellow-400',
  }
  const cls = map[verdict] || 'bg-gray-700 text-gray-200'
  return (
    <div className={`px-3 py-1 rounded-full text-sm font-semibold ${cls}`}>{verdict}</div>
  )
}

export default function TruthCard({ result, onVerifyAnother }: Props) {
  const [copyOk, setCopyOk] = useState(false)

  const copyBlob = async () => {
    if (result.da_blob_id) {
      await navigator.clipboard.writeText(result.da_blob_id)
      setCopyOk(true)
      setTimeout(() => setCopyOk(false), 2000)
    }
  }

  return (
    <div className="card p-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Verification Result</h2>
          <div className="mt-2 flex items-center gap-3">
            <VerdictBadge verdict={result.verdict} />
            <div className="text-sm text-gray-400">Confidence: <span className="text-white">{Math.round(result.confidence * 100)}%</span></div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-400">Verified just now</div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <h3 className="text-lg text-white font-semibold">Summary</h3>
          <p className="mt-2 text-gray-300">{result.summary}</p>

          <h4 className="mt-6 text-sm text-gray-400 font-semibold">Evidence</h4>
          <div className="mt-2 space-y-2 max-h-48 overflow-auto">
            {result.evidence_chain.map((s, i) => (
              <div key={i} className="p-3 rounded-lg bg-white/3">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-200 font-medium">{s.source} <span className="text-xs text-gray-400">· {s.type}</span></div>
                  {s.url ? (
                    <a className="text-xs text-0g-cyan flex items-center gap-2" href={s.url} target="_blank" rel="noreferrer">
                      <ExternalLink size={14} />
                      Source
                    </a>
                  ) : null}
                </div>
                <div className="mt-1 text-xs text-gray-300">{s.result_summary}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-[#0d0d12]">
            <h4 className="text-sm text-gray-400">TOMA Scores</h4>
            <div className="mt-3 space-y-3">
              {Object.entries(result.toma_scores).map(([k, v]) => (
                <div key={k}>
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <div className="capitalize">{k}</div>
                    <div className="font-semibold text-white">{v}</div>
                  </div>
                  <div className="mt-1 h-2 bg-white/6 rounded overflow-hidden">
                    <div style={{ width: `${v}%` }} className="h-full bg-0g-purple" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-lg bg-[#0d0d12] space-y-3">
            <div className="flex items-center justify-between text-sm text-gray-400">
              <div>0G Proof</div>
            </div>
            <div className="text-xs text-gray-300">DA Blob ID</div>
            <div className="flex items-center gap-3">
              <div className="text-sm text-white font-mono">{truncateMiddle(result.da_blob_id || '')}</div>
              <button className="text-gray-400 hover:text-white" onClick={copyBlob}>
                {copyOk ? <Check /> : <Copy />}
              </button>
            </div>

            {result.tx_hash ? (
              <a
                href={`https://chainscan-galileo.0g.ai/tx/${result.tx_hash}`}
                target="_blank"
                rel="noreferrer"
                className="mt-2 inline-block w-full text-center py-2 rounded-lg text-sm font-semibold bg-gradient-to-r from-[#6B46C1] to-[#7C3AED] hover:opacity-90"
              >
                <ExternalLink className="inline mr-2" size={14} /> View on 0G Explorer
              </a>
            ) : (
              <div className="text-xs text-gray-500">Not anchored on chain</div>
            )}
          </div>

          <div className="flex justify-end">
            <button onClick={onVerifyAnother} className="text-sm text-0g-cyan">Verify Another</button>
          </div>
        </div>
      </div>
    </div>
  )
}
