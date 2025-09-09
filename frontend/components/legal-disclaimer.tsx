'use client'

import { useState, useEffect } from 'react'
import { X, AlertTriangle, Scale } from 'lucide-react'
import { Card, CardContent } from './ui/card'
import { Button } from './ui/button'

interface LegalDisclaimerProps {
  onDismiss?: () => void
}

export default function LegalDisclaimer({ onDismiss }: LegalDisclaimerProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [isClosing, setIsClosing] = useState(false)

  useEffect(() => {
    // Check if disclaimer was already shown in this session
    const disclaimerShown = sessionStorage.getItem('legal-disclaimer-shown')
    
    if (!disclaimerShown) {
      // Show after a small delay for better UX
      const timer = setTimeout(() => {
        setIsVisible(true)
      }, 2000)

      // Auto-hide after 8 seconds
      const autoHideTimer = setTimeout(() => {
        handleClose()
      }, 10000) // 2s delay + 8s display

      return () => {
        clearTimeout(timer)
        clearTimeout(autoHideTimer)
      }
    }
    
    return undefined
  }, [])

  const handleClose = () => {
    setIsClosing(true)
    setTimeout(() => {
      setIsVisible(false)
      sessionStorage.setItem('legal-disclaimer-shown', 'true')
      onDismiss?.()
    }, 300) // Animation duration
  }

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <Card className={`
        max-w-md w-full bg-gradient-to-br from-amber-50/95 to-orange-50/95 
        border-2 border-amber-200/80 shadow-2xl backdrop-blur-md
        transform transition-all duration-300 ease-out
        ${isClosing ? 'scale-95 opacity-0' : 'scale-100 opacity-100'}
      `}>
        <CardContent className="p-6 relative">
          {/* Close button */}
          <Button
            onClick={handleClose}
            variant="ghost"
            size="sm"
            className="absolute top-2 right-2 h-8 w-8 p-0 text-amber-600 hover:text-amber-800 hover:bg-amber-100/50 rounded-full"
          >
            <X className="w-4 h-4" />
          </Button>

          {/* Header with icon */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-amber-500 to-orange-600 rounded-full flex items-center justify-center shadow-lg">
              <Scale className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-amber-900">
                Aviso Importante
              </h3>
              <p className="text-sm text-amber-700">
                Sistema de Apoyo Legal
              </p>
            </div>
          </div>

          {/* Warning icon and content */}
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 mt-1 flex-shrink-0" />
            <div className="space-y-3">
              <p className="text-sm text-amber-900 leading-relaxed">
                Este sistema es una <strong>herramienta de apoyo</strong> desarrollada para 
                proporcionar orientación legal general basada en la legislación colombiana.
              </p>
              
              <p className="text-sm text-amber-900 leading-relaxed">
                <strong>No constituye asesoría legal profesional</strong> y no reemplaza 
                la consulta con un abogado certificado. Para casos específicos, 
                siempre consulte con un profesional del derecho.
              </p>

              <div className="bg-amber-100/50 rounded-lg p-3 border border-amber-200">
                <p className="text-xs text-amber-800 text-center font-medium">
                  Proyecto personal desarrollado como herramienta educativa
                </p>
              </div>
            </div>
          </div>

          {/* Auto-close indicator */}
          <div className="mt-4 flex items-center justify-center">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
              <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
            </div>
            <p className="text-xs text-amber-700 ml-3">
              Se cierra automáticamente
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
