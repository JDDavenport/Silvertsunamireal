"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight, Play, Sparkles } from "lucide-react";
import Link from "next/link";

export function Hero() {
  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden bg-gradient-navy">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute top-20 left-10 w-72 h-72 bg-navy-500/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-20 right-10 w-96 h-96 bg-gold-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-navy-400/10 rounded-full blur-3xl"
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 60,
            repeat: Infinity,
            ease: "linear",
          }}
        />
        
        {/* Grid Pattern */}
        <div className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.175, 0.885, 0.32, 1.275] }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gold-500/10 border border-gold-500/20 mb-8"
        >
          <Sparkles className="w-4 h-4 text-gold-400" />
          <span className="text-sm font-medium text-gold-300">AI-Powered Deal Intelligence</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: [0.175, 0.885, 0.32, 1.275] }}
          className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 tracking-tight"
        >
          Discover <span className="text-gradient-gold">Profitable</span>
          <br />
          Businesses to Acquire
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: [0.175, 0.885, 0.32, 1.275] }}
          className="text-lg sm:text-xl text-navy-200 max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          The intelligence platform for serious entrepreneurs acquiring businesses
          in the $200K–$5M range. Source deals, score opportunities, and close faster.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3, ease: [0.175, 0.885, 0.32, 1.275] }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link href="/signup">
            <Button size="lg" className="w-full sm:w-auto bg-gold-500 hover:bg-gold-400 text-navy-950 font-semibold text-base px-8">
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
          
          <Button 
            size="lg" 
            variant="outline" 
            className="w-full sm:w-auto border-navy-400 text-white hover:bg-navy-800/50 hover:text-white bg-transparent"
          >
            <Play className="w-5 h-5 mr-2" />
            Watch Demo
          </Button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5, ease: [0.175, 0.885, 0.32, 1.275] }}
          className="mt-16 relative"
        >
          <div className="relative rounded-2xl overflow-hidden border border-navy-600/50 shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-t from-navy-950/80 via-transparent to-transparent z-10" />
            <div className="bg-navy-900/50 backdrop-blur-sm p-2">
              <div className="bg-navy-800 rounded-xl overflow-hidden">
                {/* Dashboard Preview */}
                <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="col-span-2 bg-navy-900/80 rounded-lg p-4 border border-navy-700">
                    <div className="flex items-center justify-between mb-4">
                      <div className="text-white font-semibold">Deal Pipeline</div>
                      <div className="flex gap-2">
                        <div className="w-20 h-6 bg-navy-700 rounded" />
                      </div>
                    </div>
                    <div className="grid grid-cols-4 gap-3">
                      {['Sourcing', 'LOI', 'Diligence', 'Closing'].map((stage, i) => (
                        <div key={stage} className="bg-navy-800/50 rounded p-3 border border-navy-700/50">
                          <div className="text-xs text-navy-300 mb-2">{stage}</div>
                          <div className="space-y-2">
                            {i < 2 && (
                              <>
                                <div className="h-12 bg-navy-700/50 rounded border-l-2 border-gold-500" />
                                <div className="h-12 bg-navy-700/50 rounded" />
                              </>
                            )}
                            {i === 2 && <div className="h-12 bg-navy-700/50 rounded border-l-2 border-navy-400" />}
                            {i === 3 && <div className="h-12 bg-navy-700/50 rounded border-l-2 border-emerald-500" />}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="bg-navy-900/80 rounded-lg p-4 border border-navy-700">
                      <div className="text-navy-300 text-sm mb-1">Pipeline Value</div>
                      <div className="text-2xl font-bold text-white font-data">$4.2M</div>
                      <div className="text-emerald-400 text-xs mt-1">+23% this month</div>
                    </div>
                    
                    <div className="bg-navy-900/80 rounded-lg p-4 border border-navy-700">
                      <div className="text-navy-300 text-sm mb-1">Active Deals</div>
                      <div className="text-2xl font-bold text-white font-data">12</div>
                      <div className="text-navy-400 text-xs mt-1">3 need attention</div>
                    </div>
                    
                    <div className="bg-navy-900/80 rounded-lg p-4 border border-navy-700">
                      <div className="text-navy-300 text-sm mb-1">Avg Deal Score</div>
                      <div className="text-2xl font-bold text-white font-data">78</div>
                      <div className="flex gap-1 mt-2">
                        <div className="flex-1 h-1.5 bg-navy-700 rounded-full overflow-hidden">
                          <div className="w-[78%] h-full bg-gradient-to-r from-gold-500 to-gold-400 rounded-full" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
