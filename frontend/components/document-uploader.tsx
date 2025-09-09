"use client"

import type React from "react"

import { useState, useCallback, useRef } from "react"
import { Button } from "@/components/ui/button"
import type { DocumentUploadResponse } from "@/lib/api-types"

interface DocumentUploaderProps {
  onUpload: (file: File, category?: string) => Promise<DocumentUploadResponse>
  isUploading: boolean
  uploadProgress: Record<string, number>
  maxFileSize?: number
  acceptedTypes?: string[]
  className?: string
}

export default function DocumentUploader({
  onUpload,
  isUploading,
  uploadProgress,
  maxFileSize = 10 * 1024 * 1024, // 10MB
  acceptedTypes = [".pdf", ".doc", ".docx", ".txt"],
  className,
}: DocumentUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    if (file.size > maxFileSize) {
      return `El archivo es muy grande. Máximo ${Math.round(maxFileSize / 1024 / 1024)}MB`
    }

    const fileExtension = "." + file.name.split(".").pop()?.toLowerCase()
    if (!acceptedTypes.includes(fileExtension)) {
      return `Tipo de archivo no soportado. Acepta: ${acceptedTypes.join(", ")}`
    }

    return null
  }

  const handleFileUpload = useCallback(
    async (files: FileList) => {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        if (!file) continue
        const error = validateFile(file)

        if (error) {
          console.error("[v0] File validation failed:", error)
          continue
        }

        try {
          await onUpload(file, selectedCategory || undefined)
          console.log("[v0] File uploaded successfully:", file.name)
        } catch (error) {
          console.error("[v0] File upload failed:", error)
        }
      }
    },
    [onUpload, selectedCategory, maxFileSize, acceptedTypes],
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)

      const files = e.dataTransfer.files
      if (files.length > 0) {
        handleFileUpload(files)
      }
    },
    [handleFileUpload],
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files && files.length > 0) {
        handleFileUpload(files)
      }
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    },
    [handleFileUpload],
  )

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const formatFileSize = (bytes: number) => {
    return `${Math.round(bytes / 1024 / 1024)}MB`
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Category Selection */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-white/90 mb-2">Categoría (opcional)</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-3 py-2 bg-white/10 border border-white/30 rounded-md text-white"
          >
            <option value="">Sin categoría</option>
            <option value="contratos">Contratos</option>
            <option value="juridicos">Jurídicos</option>
            <option value="corporativo">Corporativo</option>
            <option value="otros">Otros</option>
          </select>
        </div>
      </div>

      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer
          ${
            isDragOver
              ? "border-blue-400/70 bg-blue-500/20"
              : "border-white/30 bg-white/10 hover:border-blue-400/50 hover:bg-white/15"
          }
          ${isUploading ? "pointer-events-none opacity-50" : ""}
        `}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          id="document-upload-input"
          name="document-upload"
          type="file"
          multiple
          accept={acceptedTypes.join(",")}
          onChange={handleFileSelect}
          className="hidden"
          aria-label="Subir documentos legales"
        />

        <svg
          className={`w-12 h-12 mx-auto mb-4 transition-colors ${isDragOver ? "text-blue-400" : "text-white/70"}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>

        <p className="text-lg font-medium text-white mb-2">
          {isDragOver ? "Suelta los archivos aquí" : "Arrastra documentos aquí o haz clic para seleccionar"}
        </p>

        <p className="text-sm text-white/90 mb-4">
          Soportamos {acceptedTypes.join(", ")} hasta {formatFileSize(maxFileSize)}
        </p>

        <Button
          type="button"
          variant="outline"
          disabled={isUploading}
          className="bg-white/15 border-white/30 text-white hover:bg-white/25 backdrop-blur-sm"
        >
          {isUploading ? "Subiendo..." : "Seleccionar Archivos"}
        </Button>
      </div>

      {/* Upload Progress */}
      {Object.keys(uploadProgress).length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-white/90">Subiendo archivos:</h4>
          {Object.entries(uploadProgress).map(([fileId, progress]) => (
            <div key={fileId} className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-white/90 truncate">{fileId.split("-")[0]}</span>
                <span className="text-white/70">{progress}%</span>
              </div>
              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-500 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
