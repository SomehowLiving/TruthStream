import { Shield, Zap, Globe, Lock, Github, Twitter, Mail } from 'lucide-react';

export const About = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0A0A] to-[#1A1A2E] text-gray-300">
      <div className="max-w-4xl mx-auto px-6 py-16">
        
        {/* Hero */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-4">
            About <span className="text-[#6B46C1]">Truth</span>Stream
          </h1>
          <p className="text-xl text-[#00D9FF]">
            The First Decentralized AI Operating System for Information Integrity
          </p>
        </div>

        {/* Problem */}
        <section className="mb-12 bg-gray-900/50 p-8 rounded-2xl border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Shield className="text-red-500" /> The Problem
          </h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>Fake news travels 6x faster than truth</li>
            <li>Traditional fact-checking takes 24-48 hours</li>
            <li>Centralized systems can be censored</li>
            <li>No permanent verification audit trail</li>
          </ul>
        </section>

        {/* Solution */}
        <section className="mb-12 bg-gray-900/50 p-8 rounded-2xl border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="text-yellow-500" /> Our Solution
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: 'Real-Time', desc: 'AI analysis + web search in 3 seconds' },
              { title: 'TOMA Scoring', desc: 'Transparency, Ownership, Monetization, Alignment' },
              { title: '0G Blockchain', desc: '50 Gbps DA, permanent anchoring' },
              { title: 'Economic Security', desc: 'Stake 0G tokens, earn for accuracy' }
            ].map((item) => (
              <div key={item.title} className="p-4 bg-black/30 rounded-lg">
                <h3 className="text-[#00D9FF] font-bold">{item.title}</h3>
                <p className="text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Tech Stack */}
        <section className="mb-12 bg-gray-900/50 p-8 rounded-2xl border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Globe className="text-[#6B46C1]" /> Built on 0G
          </h2>
          <p className="mb-4">
            TruthStream leverages 0G's 50 Gbps Data Availability layer to store 
            investigation reports permanently, with sub-second finality and 
            99.99% lower costs than Ethereum.
          </p>
          <div className="flex flex-wrap gap-2">
            {['React', 'FastAPI', 'Claude AI', '0G DA', 'Solidity'].map((tech) => (
              <span key={tech} className="px-3 py-1 bg-[#6B46C1]/20 text-[#6B46C1] rounded-full text-sm">
                {tech}
              </span>
            ))}
          </div>
        </section>

        {/* Contact */}
        <section className="text-center bg-gray-900/50 p-8 rounded-2xl border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-6">Connect With Us</h2>
          <div className="flex justify-center gap-6">
            <a href="#" className="flex items-center gap-2 text-gray-400 hover:text-white">
              <Github size={20} /> GitHub
            </a>
            <a href="#" className="flex items-center gap-2 text-gray-400 hover:text-white">
              <Twitter size={20} /> Twitter
            </a>
            <a href="#" className="flex items-center gap-2 text-gray-400 hover:text-white">
              <Mail size={20} /> Email
            </a>
          </div>
        </section>

      </div>
    </div>
  );
};