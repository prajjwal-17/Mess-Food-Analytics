"use client"

import { useEffect, useState } from "react"

export default function Dashboard() {

  const [data, setData] = useState<any>(null)

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analytics/summary")
      .then(res => res.json())
      .then(data => setData(data))
  }, [])

  if (!data) {
    return <div className="p-20">Loading...</div>
  }

  return (
    <main className="bg-gray-100 min-h-screen py-24">

      <div className="max-w-7xl mx-auto px-6 space-y-12">

        {/* Page Title */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Mess Waste Analytics Dashboard
          </h1>

          <p className="text-gray-600 mt-2">
            Monitor waste trends and operational efficiency across hostel mess facilities.
          </p>
        </div>

        {/* Analytics Cards */}
        <div className="grid md:grid-cols-3 gap-8">

          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition">
            <p className="text-gray-500 text-sm mb-2">Total Waste</p>
            <h2 className="text-2xl font-bold text-gray-900">
              {data.total_waste_kg} kg
            </h2>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition">
            <p className="text-gray-500 text-sm mb-2">Financial Loss</p>
            <h2 className="text-2xl font-bold text-gray-900">
              ₹{data.total_financial_loss_inr}
            </h2>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition">
            <p className="text-gray-500 text-sm mb-2">CO₂ Emissions</p>
            <h2 className="text-2xl font-bold text-gray-900">
              {data.co2_emissions_tonnes} tonnes
            </h2>
          </div>

        </div>

      </div>

    </main>
  )
}