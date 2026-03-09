export default function HeroSection() {
  return (
    <section className="bg-white py-24">

      <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-12 items-center">

        <div>

          <h1 className="text-5xl font-bold text-black mb-6">
            Data-Driven Hostel Mess Waste Analytics
          </h1>

          <p className="text-gray-600 mb-6">
            Analyze mess consumption trends, forecast meal demand,
            and reduce food waste with data-driven insights.
          </p>

          <div className="flex gap-4">

            <button className="bg-black text-white px-6 py-3 rounded-lg">
              View Dashboard
            </button>

            <button className="border border-gray-300 px-6 py-3 rounded-lg">
              Learn More
            </button>

          </div>

        </div>

        <div className="bg-gray-100 border rounded-xl h-72 flex items-center justify-center text-gray-500">
          Dashboard Preview
        </div>

      </div>

    </section>
  )
}