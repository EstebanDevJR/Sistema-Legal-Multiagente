export interface LegalQueryRequest {
  query: string
  method: "text" | "voice" | "document"
  area?: string
  userId?: string
  sessionId?: string
  documentIds?: string[]
}

export interface LegalQueryResponse {
  id: string
  response: string
  confidence: number
  area: string
  sources: LegalSource[]
  relatedQuestions: string[]
  audioUrl?: string
  metadata: {
    processingTime: number
    sourceCount: number
    timestamp: string
    transcription?: string
    voiceProcessing?: boolean
  }
}

export interface LegalSource {
  id: string
  title: string
  type: "ley" | "decreto" | "jurisprudencia" | "doctrina"
  article?: string
  url?: string
  relevance: number
  excerpt: string
}

export interface VoiceRequest {
  audioBlob: Blob
  userId?: string
}

export interface VoiceResponse {
  transcription: string
  audioUrl?: string
  confidence: number
}

export interface DocumentUploadRequest {
  file: File
  userId: string
  category?: string
}

export interface DocumentUploadResponse {
  id: string
  filename: string
  size: number
  type: string
  uploadedAt: string
  status: "processing" | "ready" | "error"
  extractedText?: string
}

export interface UserDocument {
  id: string
  filename: string
  size: number
  type: string
  uploadedAt: string
  status: "processing" | "ready" | "error"
  category?: string
}

export interface QuerySuggestion {
  text: string
  area: string
  popularity: number
}

export interface ApiError {
  message: string
  code: string
  details?: any
}
