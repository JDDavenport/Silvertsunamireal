const DashboardView = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
        <p className="text-gray-600">
          Track your acquisition pipeline, monitor saved targets, and analyze market trends.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Saved Targets', value: '12', change: '+3 this week', positive: true },
          { label: 'Active Pipelines', value: '5', change: '+1 this week', positive: true },
          { label: 'Completed Deals', value: '8', change: '2 this month', positive: true },
          { label: 'Total Value', value: '$24.5M', change: '+$5.2M', positive: true },
        ].map((stat) => (
          <div key={stat.label} className="bg-white shadow rounded-lg p-6">
            <p className="text-sm font-medium text-gray-600 mb-1">{stat.label}</p>
            <p className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</p>
            <p className={`text-sm ${stat.positive ? 'text-green-600' : 'text-red-600'}`}>
              {stat.change}
            </p>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Overview</h2>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <span className="text-gray-400">Chart Placeholder - Pipeline Stages</span>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Monthly Activity</h2>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <span className="text-gray-400">Chart Placeholder - Activity Timeline</span>
          </div>
        </div>
      </div>

      {/* Recent Activity & Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {[
              { action: 'New target added', item: 'TechCorp Solutions', time: '2 hours ago' },
              { action: 'Due diligence completed', item: 'Property A-104', time: '5 hours ago' },
              { action: 'Offer submitted', item: 'Manufacturing Co.', time: '1 day ago' },
              { action: 'Document uploaded', item: 'Financial Statements Q4', time: '2 days ago' },
            ].map((activity, i) => (
              <div key={i} className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                  <p className="text-sm text-gray-600">{activity.item}</p>
                  <p className="text-xs text-gray-400 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Tasks</h2>
          <div className="space-y-4">
            {[
              { task: 'Review Q1 financials', due: 'Due today', priority: 'high' },
              { task: 'Schedule site visit', due: 'Due tomorrow', priority: 'high' },
              { task: 'Prepare LOI draft', due: 'Due in 3 days', priority: 'medium' },
              { task: 'Call with legal team', due: 'Due in 5 days', priority: 'low' },
            ].map((task, i) => (
              <div key={i} className="flex items-center space-x-3 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                <input type="checkbox" className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{task.task}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-500">{task.due}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      task.priority === 'high'
                        ? 'bg-red-100 text-red-700'
                        : task.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {task.priority}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button className="w-full mt-4 py-2 text-sm text-primary-600 hover:text-primary-700 font-medium border border-primary-600 rounded-lg hover:bg-primary-50 transition-colors">
            View All Tasks
          </button>
        </div>
      </div>
    </div>
  )
}

export default DashboardView
