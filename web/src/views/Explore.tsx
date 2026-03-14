const ExploreView = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Explore</h1>
        <p className="text-gray-600 mb-6">
          Discover and analyze acquisition targets. Search through our database of companies,
          properties, and assets available for acquisition.
        </p>

        {/* Search Bar */}
        <div className="flex gap-4 mb-8">
          <input
            type="text"
            placeholder="Search companies, assets, or keywords..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
          <button className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
            Search
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          {['All', 'Companies', 'Real Estate', 'IP Assets', 'Equipment'].map((filter) => (
            <button
              key={filter}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors text-sm font-medium"
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
              <span className="text-gray-400">Image Placeholder</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Acquisition Target {i}</h3>
            <p className="text-gray-600 text-sm mb-4">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
              Description of the asset or company.
            </p>
            <div className="flex justify-between items-center">
              <span className="text-primary-600 font-semibold">$1.2M - $2.5M</span>
              <button className="text-sm text-gray-600 hover:text-primary-600">View Details →</button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-center gap-2 mt-8">
        {['Previous', '1', '2', '3', 'Next'].map((page) => (
          <button
            key={page}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              page === '1'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            {page}
          </button>
        ))}
      </div>
    </div>
  )
}

export default ExploreView
