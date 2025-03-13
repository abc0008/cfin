'use client'

import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { BarChart, FileText, Home, Settings, User } from 'lucide-react'

export default function Header() {
  const pathname = usePathname()

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          {/* Logo and branding */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <div className="bg-indigo-600 text-white p-1.5 rounded mr-2">
                <BarChart className="h-5 w-5" />
              </div>
              <span className="font-semibold text-xl text-gray-900">FDAS</span>
            </Link>
          </div>

          {/* Main navigation */}
          <nav className="hidden md:flex space-x-1">
            <Link 
              href="/" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                pathname === '/' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center">
                <Home className="h-4 w-4 mr-1.5" />
                Home
              </div>
            </Link>
            <Link 
              href="/dashboard" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                pathname === '/dashboard' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center">
                <BarChart className="h-4 w-4 mr-1.5" />
                Dashboard
              </div>
            </Link>
            <Link 
              href="/workspace" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                pathname === '/workspace' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center">
                <FileText className="h-4 w-4 mr-1.5" />
                Workspace
              </div>
            </Link>
          </nav>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <button className="p-2 text-gray-500 rounded-full hover:bg-gray-100">
              <Settings className="h-5 w-5" />
            </button>
            <div className="flex items-center">
              <button className="flex items-center">
                <div className="bg-gray-200 rounded-full p-0.5">
                  <User className="h-6 w-6 text-gray-600" />
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}