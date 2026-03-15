import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
}

interface FAQProps {
  items: FAQItem[];
}

export function FAQ({ items }: FAQProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className="max-w-3xl mx-auto">
      {items.map((item, index) => (
        <div key={index} className="border-b border-slate-800 last:border-b-0">
          <button
            onClick={() => setOpenIndex(openIndex === index ? null : index)}
            className="w-full py-6 flex items-center justify-between text-left group"
          >
            <span className="text-lg font-semibold text-white pr-8 group-hover:text-indigo-300 transition-colors">
              {item.question}
            </span>
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center transition-all ${
                openIndex === index ? 'bg-indigo-500/20' : ''
              }`}
            >
              {openIndex === index ? (
                <ChevronUp className="w-5 h-5 text-indigo-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-slate-400" />
              )}
            </div>
          </button>
          <div
            className={`overflow-hidden transition-all duration-300 ${
              openIndex === index ? 'max-h-96 pb-6' : 'max-h-0'
            }`}
          >
            <p className="text-slate-400 leading-relaxed">{item.answer}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
