import React from 'react'
import { AlertTriangle } from 'lucide-react'

export default function ErrorBanner({ message }: { message: string | null }) {
  if (!message) return null
  return (
    <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
      <div className="px-4 py-3 rounded-lg bg-red-900/80 border border-red-700 text-sm text-red-100">
        <div className="flex items-center gap-3">
          <AlertTriangle />
          <div>{message}</div>
        </div>
      </div>
    </div>
  )
}
