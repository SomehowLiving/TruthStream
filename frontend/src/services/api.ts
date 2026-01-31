import axios from 'axios'
import type { InvestigationResult } from '../types'

const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 20000,
})

export async function uploadAndVerify(file: File): Promise<InvestigationResult> {
    const formData = new FormData()
    formData.append('file', file)
    try {
        const resp = await api.post('/verify/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return resp.data as InvestigationResult
    } catch (err: any) {
        if (err.code === 'ECONNABORTED') {
            throw new Error('Request timed out. File may be too large.')
        }
        if (err.response) {
            if (err.response.status === 500) {
                throw new Error('Verification service temporarily unavailable')
            }
            const msg = err.response.data?.detail || 'Verification failed'
            throw new Error(msg)
        }
        throw new Error('Cannot connect to backend. Ensure it\'s running on localhost:8000')
    }
}
