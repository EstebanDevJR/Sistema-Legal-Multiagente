"use client"

import { useEffect, useState } from "react"

interface HydrationBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export default function HydrationBoundary({ 
  children, 
  fallback = null 
}: HydrationBoundaryProps) {
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    // Clean up browser extension attributes that cause hydration mismatches
    const cleanupExtensionAttributes = () => {
      const body = document.body
      if (body) {
        // Remove common browser extension attributes
        const extensionAttributes = [
          /^__processed_/,
          /^bis_/,
          /^data-extension-/,
          /^data-browser-extension/
        ]
        
        extensionAttributes.forEach(pattern => {
          const attributes = Array.from(body.attributes)
          attributes.forEach(attr => {
            if (pattern.test(attr.name)) {
              body.removeAttribute(attr.name)
            }
          })
        })
      }
    }

    // Set hydrated state
    setIsHydrated(true)
    
    // Clean up extension attributes after hydration
    cleanupExtensionAttributes()
    
    // Also clean up on DOM mutations (for dynamic extensions)
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.target === document.body) {
          cleanupExtensionAttributes()
        }
      })
    })
    
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['__processed_*', 'bis_*']
    })
    
    return () => {
      observer.disconnect()
    }
  }, [])

  // Show fallback during hydration
  if (!isHydrated) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
