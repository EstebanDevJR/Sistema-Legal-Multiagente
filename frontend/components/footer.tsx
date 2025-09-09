import Link from "next/link"

export default function Footer() {
  return (
    <footer className="relative z-10 mt-2 border-t border-white/20 pt-3">
      <div className="text-center py-2">
        <p className="text-white/80 text-xs">
          Built by
          <Link 
            href="https://www.linkedin.com/in/esteban-ortiz-restrepo" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-block ml-2 text-red-400 hover:text-red-300 transition-colors hover:scale-110 transform duration-200"
            title="LinkedIn Profile"
          >
            <span className="text-cyan-300 font-medium">Esteban Ortiz</span>
            ❤️
          </Link>
        </p>
      </div>
    </footer>
  )
}
