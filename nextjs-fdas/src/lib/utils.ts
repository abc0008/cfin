import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
 
/**
 * Merge multiple class names with Tailwind CSS support
 * This is a utility function used by shadcn components
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function truncateText(text: string, maxLength: number = 60): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function generateUUID(): string {
  return crypto.randomUUID()
}

export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}