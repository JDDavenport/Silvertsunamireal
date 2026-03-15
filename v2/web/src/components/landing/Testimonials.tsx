import { Star, Quote } from 'lucide-react';

interface Testimonial {
  quote: string;
  author: string;
  role: string;
  company: string;
  rating: number;
}

interface TestimonialsProps {
  testimonials: Testimonial[];
}

export function Testimonials({ testimonials }: TestimonialsProps) {
  return (
    <div className="grid md:grid-cols-3 gap-6">
      {testimonials.map((testimonial, index) => (
        <div
          key={index}
          className="relative p-6 rounded-2xl bg-slate-900/30 border border-slate-800/50 hover:border-slate-700 transition-all group"
        >
          <div className="absolute top-6 right-6 text-indigo-500/20 group-hover:text-indigo-500/30 transition-colors">
            <Quote className="w-8 h-8" />
          </div>

          <div className="flex gap-1 mb-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Star
                key={i}
                className={`w-4 h-4 ${
                  i < testimonial.rating
                    ? 'text-amber-400 fill-amber-400'
                    : 'text-slate-700'
                }`}
              />
            ))}
          </div>

          <p className="text-slate-300 mb-6 leading-relaxed text-sm">
            "{testimonial.quote}"
          </p>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold text-sm">
              {testimonial.author
                .split(' ')
                .map((n) => n[0])
                .join('')}
            </div>
            <div>
              <p className="text-white font-medium text-sm">{testimonial.author}</p>
              <p className="text-slate-500 text-xs">
                {testimonial.role}, {testimonial.company}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
