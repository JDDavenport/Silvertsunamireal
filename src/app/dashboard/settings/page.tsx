export default function SettingsPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-[#0A1628] mb-8">Settings</h1>
      
      <div className="max-w-2xl space-y-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">Profile</h2>
          <p className="text-gray-600">Profile settings coming soon.</p>
        </div>
        
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">Notifications</h2>
          <p className="text-gray-600">Notification preferences coming soon.</p>
        </div>
        
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">Integrations</h2>
          <p className="text-gray-600">Third-party integrations coming soon.</p>
        </div>
      </div>
    </div>
  );
}
