"use client"

import { useState, useCallback, useEffect } from "react"
import { apiClient } from "@/lib/api-client"
import type { UserDocument, DocumentUploadResponse } from "@/lib/api-types"

export function useDocuments(userId = "default-user") {
  const [documents, setDocuments] = useState<UserDocument[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})

  const loadDocuments = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      console.log("[v0] Loading documents for user:", userId)
      const docs = await apiClient.getUserDocuments(userId)
      console.log("[v0] Documents loaded:", docs.length)
      setDocuments(docs)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error al cargar documentos"
      console.error("[v0] Failed to load documents:", err)
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }, [userId])

  const uploadDocument = useCallback(
    async (file: File, category?: string): Promise<DocumentUploadResponse> => {
      setIsUploading(true)
      setError(null)

      const fileId = `${file.name}-${Date.now()}`
      setUploadProgress((prev) => ({ ...prev, [fileId]: 0 }))

      try {
        console.log("[v0] Uploading document:", file.name, file.size, "bytes")

        // Simulate upload progress
        const progressInterval = setInterval(() => {
          setUploadProgress((prev) => {
            const current = prev[fileId] || 0
            if (current < 90) {
              return { ...prev, [fileId]: current + 10 }
            }
            return prev
          })
        }, 200)

        const response = await apiClient.uploadDocument(file, userId, category)

        clearInterval(progressInterval)
        setUploadProgress((prev) => ({ ...prev, [fileId]: 100 }))

        console.log("[v0] Document uploaded successfully:", response)

        // Add to documents list
        const newDoc: UserDocument = {
          id: response.id,
          filename: response.filename,
          size: response.size,
          type: response.type,
          uploadedAt: response.uploadedAt,
          status: response.status,
          category,
        }

        setDocuments((prev) => [newDoc, ...prev])

        // Clean up progress after delay
        setTimeout(() => {
          setUploadProgress((prev) => {
            const { [fileId]: _, ...rest } = prev
            return rest
          })
        }, 2000)

        return response
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Error al subir documento"
        console.error("[v0] Document upload failed:", err)
        setError(errorMessage)

        setUploadProgress((prev) => {
          const { [fileId]: _, ...rest } = prev
          return rest
        })

        throw err
      } finally {
        setIsUploading(false)
      }
    },
    [userId],
  )

  const deleteDocument = useCallback(async (documentId: string) => {
    try {
      console.log("[v0] Deleting document:", documentId)
      await apiClient.deleteDocument(documentId)

      setDocuments((prev) => prev.filter((doc) => doc.id !== documentId))
      console.log("[v0] Document deleted successfully")
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error al eliminar documento"
      console.error("[v0] Failed to delete document:", err)
      setError(errorMessage)
      throw err
    }
  }, [])

  const getDocumentStats = useCallback(() => {
    const totalSize = documents.reduce((sum, doc) => sum + doc.size, 0)
    const byStatus = documents.reduce(
      (acc, doc) => {
        acc[doc.status] = (acc[doc.status] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const byType = documents.reduce(
      (acc, doc) => {
        const type = doc.type.split("/")[1] || doc.type
        acc[type] = (acc[type] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    return {
      total: documents.length,
      totalSize,
      byStatus,
      byType,
    }
  }, [documents])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  return {
    documents,
    isLoading,
    isUploading,
    error,
    uploadProgress,
    uploadDocument,
    deleteDocument,
    loadDocuments,
    getDocumentStats,
  }
}
