export interface TOMAScores {
    transparency: number
    ownership: number
    alignment: number
    overall: number
}

export interface SourceEvidence {
    type: string
    source: string
    result_summary: string
    url?: string
}

export interface InvestigationResult {
    content_hash: string
    verdict: string
    confidence: number
    toma_scores: TOMAScores
    summary: string
    evidence_chain: SourceEvidence[]
    da_blob_id?: string
    tx_hash?: string
}
