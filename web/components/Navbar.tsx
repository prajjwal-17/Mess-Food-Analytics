export default function Navbar() {
  return (
    <nav className="w-full bg-white border-b">
      <div className="max-w-7xl mx-auto flex justify-between items-center px-6 py-4">

        <h1 className="text-lg font-semibold text-black">
          Mess Analytics
        </h1>

        <div className="space-x-6 text-sm text-gray-700">
          <a href="/dashboard" className="hover:text-black">Home</a>
          <a href="#" className="hover:text-black">Features</a>
          <a href="#" className="hover:text-black">Dashboard</a>
        </div>

      </div>
    </nav>
  )
}