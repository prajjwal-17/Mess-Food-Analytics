export default function Features() {
  return (
    <section className="bg-gray-100 py-24">

      <div className="max-w-7xl mx-auto px-6">

        {/* Section Title */}
        <div className="text-center mb-14">

          <h2 className="text-3xl font-bold text-black mb-3">
            Platform Features
          </h2>

          <p className="text-gray-600 max-w-xl mx-auto">
            Tools designed to help institutions analyze mess operations
            and reduce food waste effectively.
          </p>

        </div>


        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8">

          <div className="bg-white p-7 rounded-xl border border-gray-200 hover:shadow-md transition duration-300">
            <h3 className="text-lg font-semibold mb-3 text-black">
              Demand Forecasting
            </h3>

            <p className="text-gray-600 text-sm leading-relaxed">
              Predict student turnout using historical mess data
              and consumption patterns.
            </p>
          </div>


          <div className="bg-white p-7 rounded-xl border border-gray-200 hover:shadow-md transition duration-300">
            <h3 className="text-lg font-semibold mb-3 text-black">
              Waste Analytics
            </h3>

            <p className="text-gray-600 text-sm leading-relaxed">
              Identify meals generating the highest waste
              and optimize cooking quantities.
            </p>
          </div>


          <div className="bg-white p-7 rounded-xl border border-gray-200 hover:shadow-md transition duration-300">
            <h3 className="text-lg font-semibold mb-3 text-black">
              Procurement Insights
            </h3>

            <p className="text-gray-600 text-sm leading-relaxed">
              Track ingredient demand trends to reduce
              unnecessary purchasing.
            </p>
          </div>

        </div>

      </div>

    </section>
  )
}