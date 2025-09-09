"use client"

import { useEffect, useRef, forwardRef } from "react"
import { Textarea } from "@/components/ui/textarea"
import type { TextareaHTMLAttributes } from "react"

interface AutoResizeTextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  value: string
  minRows?: number
  maxRows?: number
}

const AutoResizeTextarea = forwardRef<HTMLTextAreaElement, AutoResizeTextareaProps>(
  ({ value, minRows = 3, maxRows = 10, className, ...props }, ref) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const combinedRef = ref || textareaRef

    useEffect(() => {
      const textarea = typeof combinedRef === "function" ? textareaRef.current : combinedRef?.current
      if (!textarea) return

      // Reset height to auto to get the correct scrollHeight
      textarea.style.height = "auto"

      // Calculate the number of lines
      const lineHeight = Number.parseInt(getComputedStyle(textarea).lineHeight)
      const lines = Math.ceil(textarea.scrollHeight / lineHeight)

      // Constrain between min and max rows
      const constrainedLines = Math.max(minRows, Math.min(maxRows, lines))

      // Set the height
      textarea.style.height = `${constrainedLines * lineHeight}px`
    }, [value, minRows, maxRows, combinedRef])

    return (
      <Textarea
        ref={combinedRef}
        value={value}
        className={`resize-none transition-all duration-200 ${className}`}
        {...props}
      />
    )
  },
)

AutoResizeTextarea.displayName = "AutoResizeTextarea"

export default AutoResizeTextarea
