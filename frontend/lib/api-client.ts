const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

// Declare types before using them
type LegalQueryRequest = {}
type LegalQueryResponse = {}
type QuerySuggestion = {}
type VoiceResponse = {}
type DocumentUploadResponse = {}
type UserDocument = {}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("[v0] API request failed:", error)
      throw error
    }
  }

  // RAG Endpoints
  async submitQuery(data: LegalQueryRequest): Promise<LegalQueryResponse> {
    return this.request<LegalQueryResponse>("/rag/query", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getQuerySuggestions(area?: string): Promise<QuerySuggestion[]> {
    try {
      const params = area ? `?area=${encodeURIComponent(area)}` : ""
      const result = await this.request<QuerySuggestion[]>(`/rag/suggestions${params}`)
      return Array.isArray(result) ? result : []
    } catch (error) {
      console.error("[v0] Failed to get query suggestions:", error)
      return []
    }
  }

  async getExampleQueries(area?: string): Promise<QuerySuggestion[]> {
    try {
      const params = area ? `?area=${encodeURIComponent(area)}` : ""
      const result = await this.request<QuerySuggestion[]>(`/rag/examples${params}`)
      return Array.isArray(result) ? result : []
    } catch (error) {
      console.error("[v0] Failed to get example queries:", error)
      return []
    }
  }

  async getQueryResult(id: string): Promise<LegalQueryResponse> {
    return this.request<LegalQueryResponse>(`/rag/result/${id}`)
  }

  // Voice Endpoints
  async speechToText(audioBlob: Blob, userId?: string): Promise<VoiceResponse> {
    const formData = new FormData()
    // Use the correct file extension based on the blob type
    const extension = audioBlob.type.includes("webm") ? "webm" : 
                     audioBlob.type.includes("mp4") ? "mp4" : "wav"
    formData.append("audio_file", audioBlob, `recording.${extension}`)
    formData.append("language", "es")
    if (userId) formData.append("userId", userId)

    return this.request<VoiceResponse>("/voice/speech-to-text", {
      method: "POST",
      headers: {}, // Remove Content-Type to let browser set it for FormData
      body: formData,
    })
  }

  async textToSpeech(text: string): Promise<{ audioUrl: string }> {
    const formData = new FormData()
    formData.append("text", text)
    formData.append("voice_style", "legal")
    formData.append("output_format", "mp3")

    const response = await this.request<any>("/voice/text-to-speech", {
      method: "POST",
      headers: {}, // Remove Content-Type to let browser set it for FormData
      body: formData,
    })

    // Transform backend response format to match frontend expectations
    return {
      audioUrl: response.download_url || ""
    }
  }

  async submitVoiceQuery(audioBlob: Blob, userId?: string, responseMode: string = "text", documentIds?: string[]): Promise<LegalQueryResponse> {
    console.log("[v0] submitVoiceQuery called with:")
    console.log("  - audioBlob.size:", audioBlob.size, "bytes")
    console.log("  - audioBlob.type:", audioBlob.type)
    console.log("  - userId:", userId)
    console.log("  - responseMode:", responseMode)

    const formData = new FormData()
    // Use the correct file extension based on the blob type
    const extension = audioBlob.type.includes("webm") ? "webm" : 
                     audioBlob.type.includes("mp4") ? "mp4" : "wav"
    
    console.log("  - Extension determined:", extension)
    
    formData.append("audio_file", audioBlob, `query.${extension}`)
    formData.append("voice_response_style", "legal")
    formData.append("language", "es")
    formData.append("response_mode", responseMode)
    if (userId) formData.append("userId", userId)
    if (documentIds && documentIds.length > 0) {
      formData.append("document_ids", documentIds.join(","))
    }

    console.log("  - FormData entries:")
    for (const [key, value] of formData.entries()) {
      if (value && typeof value === 'object' && 'size' in value && 'type' in value) {
        console.log(`    ${key}:`, value.constructor.name, `(${value.size} bytes, ${value.type})`)
      } else {
        console.log(`    ${key}:`, String(value))
      }
    }

    return this.request<LegalQueryResponse>("/voice/voice-query", {
      method: "POST",
      headers: {},
      body: formData,
    })
  }

  // Document Endpoints
  async uploadDocument(file: File, userId: string, category?: string): Promise<DocumentUploadResponse> {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("userId", userId)
    if (category) formData.append("category", category)

    return this.request<DocumentUploadResponse>("/documents/upload", {
      method: "POST",
      headers: {},
      body: formData,
    })
  }

  async getUserDocuments(userId: string): Promise<UserDocument[]> {
    return this.request<UserDocument[]>(`/documents/user/${userId}`)
  }

  async deleteDocument(documentId: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(`/documents/${documentId}`, {
      method: "DELETE",
    })
  }

  async getDocumentContent(documentId: string): Promise<{ content: string }> {
    return this.request<{ content: string }>(`/documents/${documentId}/content`)
  }

  // Chat Endpoints
  async getChatSessions(): Promise<any[]> {
    return this.request<any[]>("/chat/sessions")
  }

  async createChatSession(title?: string): Promise<any> {
    return this.request<any>("/chat/sessions", {
      method: "POST",
      body: JSON.stringify({ title }),
    })
  }

  async getChatMessages(sessionId: string): Promise<any[]> {
    return this.request<any[]>(`/chat/sessions/${sessionId}/messages`)
  }

  async addChatMessage(sessionId: string, message: any): Promise<any> {
    return this.request<any>(`/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        ...message
      }),
    })
  }

  async updateChatMessage(sessionId: string, messageId: string, message: any): Promise<any> {
    return this.request<any>(`/chat/sessions/${sessionId}/messages/${messageId}`, {
      method: "PUT",
      body: JSON.stringify(message),
    })
  }

  async deleteChatSession(sessionId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/chat/sessions/${sessionId}`, {
      method: "DELETE",
    })
  }

  async updateChatSessionTitle(sessionId: string, title: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/chat/sessions/${sessionId}/title`, {
      method: "PUT",
      body: JSON.stringify({ title }),
    })
  }
}

export const apiClient = new ApiClient()
export default apiClient
