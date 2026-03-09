interface Props {
  title: string
  value: string
  subtitle?: string
}

export default function AnalyticsCard({ title, value, subtitle }: Props) {
  return (
    <div className="
      bg-white
      border border-gray-200
      rounded-xl
      p-6
      hover:shadow-md
      transition
      duration-300
    ">

      <p className="text-sm text-gray-500 mb-2">
        {title}
      </p>

      <h2 className="text-2xl font-bold text-gray-900">
        {value}
      </h2>

      {subtitle && (
        <p className="text-sm text-gray-600 mt-2">
          {subtitle}
        </p>
      )}

    </div>
  )
}