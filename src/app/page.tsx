export default function Home() {
  return (
    <div className="min-h-screen bg-[#0A1628]">
      {/* Hero Section */}
      <section className="relative px-6 lg:px-8 py-24 lg:py-32">
        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl">
              Find and Acquire
              <span className="text-[#C9A227]"> Small Businesses</span>
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-300 max-w-2xl mx-auto">
              ACQUISITOR automates lead discovery, scoring, and outreach so you can focus on closing deals. From first contact to signed agreement.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <a
                href="/signup"
                className="rounded-md bg-[#C9A227] px-6 py-3 text-sm font-semibold text-[#0A1628] shadow-sm hover:bg-[#D4B43D] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#C9A227]"
              >
                Start Free Trial
              </a>
              <a href="#features" className="text-sm font-semibold leading-6 text-white hover:text-[#C9A227]">
                See How It Works <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-[#0F1D32]">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-[#C9A227]">Everything You Need</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              From Discovery to Close
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3">
              {[
                {
                  title: 'Lead Discovery',
                  description: 'Automatically scrape business listings and discover opportunities that match your criteria.',
                },
                {
                  title: 'AI Scoring',
                  description: 'Our AI scores leads 1-100 based on fit, helping you focus on the best opportunities.',
                },
                {
                  title: 'Smart Outreach',
                  description: 'Generate personalized emails with AI and track opens, clicks, and replies.',
                },
              ].map((feature) => (
                <div key={feature.title} className="flex flex-col bg-[#162544] rounded-lg p-8 border border-[#1E3160]">
                  <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-white">
                    {feature.title}
                  </dt>
                  <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-300">
                    <p className="flex-auto">{feature.description}</p>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to Find Your Next Acquisition?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-gray-300">
              Join successful business buyers using ACQUISITOR to discover and close deals.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <a
                href="/signup"
                className="rounded-md bg-[#C9A227] px-6 py-3 text-sm font-semibold text-[#0A1628] shadow-sm hover:bg-[#D4B43D]"
              >
                Get Started Free
              </a>
              <a href="/login" className="text-sm font-semibold leading-6 text-white">
                Sign In <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0A1628] border-t border-[#1E3160]">
        <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
          <div className="flex justify-between items-center">
            <p className="text-gray-400 text-sm">© 2026 ACQUISITOR. All rights reserved.</p>
            <div className="flex gap-6">
              <a href="/login" className="text-gray-400 hover:text-white text-sm">Sign In</a>
              <a href="/signup" className="text-gray-400 hover:text-white text-sm">Sign Up</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
