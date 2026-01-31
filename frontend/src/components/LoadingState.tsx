import React from 'react'
import { Loader2, Check } from 'lucide-react'

export default function LoadingState() {
  return (
    <div className="card p-8 flex flex-col items-center justify-center">
      <Loader2 className="animate-spin text-0g-cyan" size={48} />
      <h3 className="mt-4 text-lg text-white">Analyzing…</h3>
      <div className="mt-6 w-full max-w-md space-y-3">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-white/5 w-8 h-8 flex items-center justify-center"><Check className="text-green-400" size={16} /></div>
          <div className="text-sm text-gray-300">Analyzing AI…</div>
        </div>
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-white/5 w-8 h-8 flex items-center justify-center">2</div>
          <div className="text-sm text-gray-300">Cross-referencing sources…</div>
        </div>
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-white/5 w-8 h-8 flex items-center justify-center">3</div>
          <div className="text-sm text-gray-300">Anchoring to 0G…</div>
        </div>
      </div>
    </div>
  )
}
