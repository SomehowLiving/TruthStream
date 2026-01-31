import React from 'react'
import clsx from 'clsx'

export function Button({ children, onClick, disabled = false }: any) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'px-4 py-2 rounded-lg text-sm font-semibold text-white',
        'bg-gradient-to-r from-[#6B46C1] to-[#7C3AED] hover:opacity-90 disabled:opacity-50'
      )}
    >
      {children}
    </button>
  )
}
