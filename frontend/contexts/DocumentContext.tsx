"use client"

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'

interface UserDocument {
  id: string
  filename: string
  size: number
  type: string
  uploadedAt: string
  status: string
  category?: string
}

interface DocumentContextType {
  uploadedDocuments: File[]
  uploadedDocumentIds: string[]
  userDocuments: UserDocument[]
  addDocument: (file: File, documentId: string) => void
  removeDocument: (documentId: string) => void
  clearDocuments: () => void
  setUserDocuments: (documents: UserDocument[]) => void
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined)

export function DocumentProvider({ children }: { children: ReactNode }) {
  const [uploadedDocuments, setUploadedDocuments] = useState<File[]>([])
  const [uploadedDocumentIds, setUploadedDocumentIds] = useState<string[]>([])
  const [userDocuments, setUserDocuments] = useState<UserDocument[]>([])

  const addDocument = useCallback((file: File, documentId: string) => {
    setUploadedDocuments(prev => [...prev, file])
    setUploadedDocumentIds(prev => [...prev, documentId])
  }, [])

  const removeDocument = useCallback((documentId: string) => {
    setUploadedDocuments(prev => prev.filter((_, index) => 
      uploadedDocumentIds[index] !== documentId
    ))
    setUploadedDocumentIds(prev => prev.filter(id => id !== documentId))
    setUserDocuments(prev => prev.filter(doc => doc.id !== documentId))
  }, [uploadedDocumentIds])

  const clearDocuments = useCallback(() => {
    setUploadedDocuments([])
    setUploadedDocumentIds([])
    setUserDocuments([])
  }, [])

  return (
    <DocumentContext.Provider
      value={{
        uploadedDocuments,
        uploadedDocumentIds,
        userDocuments,
        addDocument,
        removeDocument,
        clearDocuments,
        setUserDocuments,
      }}
    >
      {children}
    </DocumentContext.Provider>
  )
}

export function useDocuments() {
  const context = useContext(DocumentContext)
  if (context === undefined) {
    throw new Error('useDocuments must be used within a DocumentProvider')
  }
  return context
}
