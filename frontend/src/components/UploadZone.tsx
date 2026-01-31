import React from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from './ui/Button'
import { UploadCloud, File, FileIcon } from 'lucide-react'

type Props = {
  file: File | null
  setFile: (f: File | null) => void
  onVerify: () => void
  loading: boolean
}

export default function UploadZone({ file, setFile, onVerify, loading }: Props) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': [],
      'video/*': [],
      'text/*': [],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setFile(acceptedFiles[0])
    },
  })

  return (
    <div className="card p-8">
      <div
        {...getRootProps()}
        className={`rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
          isDragActive ? 'border-0g-purple bg-0g-dark/70' : 'border-white/10 bg-[#070707]'
        }`}
        style={{ cursor: 'pointer' }}
      >
        <input {...getInputProps()} />
        <UploadCloud className="mx-auto mb-4 text-0g-purple" size={36} />
        <p className="text-gray-400">Drag & drop an image or video here</p>
        <p className="text-sm text-gray-500">Or click to select a file</p>
      </div>

      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileIcon />
          <div>
            <div className="text-sm text-gray-300">{file ? file.name : 'No file selected'}</div>
            {file && <div className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</div>}
          </div>
        </div>

        <Button onClick={onVerify} disabled={!file || loading}>
          {loading ? 'Verifying...' : 'Verify Truth'}
        </Button>
      </div>
    </div>
  )
}
