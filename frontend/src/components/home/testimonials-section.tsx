'use client';

import { motion } from 'framer-motion';
import { Star, Quote } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

interface Testimonial {
  name: string;
  role: string;
  company: string;
  avatar: string;
  content: string;
  rating: number;
}

const testimonials: Testimonial[] = [
  {
    name: 'Sarah Chen',
    role: 'CTO',
    company: 'TechFlow Inc',
    avatar: '/avatars/sarah.jpg',
    content:
      'Suna Ultra has transformed how we build autonomous workflows. The multi-agent orchestration is light years ahead of anything else on the market. We replaced 3 different tools with just Suna Ultra.',
    rating: 5,
  },
  {
    name: 'Marcus Rodriguez',
    role: 'Founder',
    company: 'DataPulse AI',
    avatar: '/avatars/marcus.jpg',
    content:
      'The self-hosted option was a game-changer for us. Full control over our data while having enterprise-grade AI capabilities. The agent debugging tools saved us weeks of development time.',
    rating: 5,
  },
  {
    name: 'Emily Watson',
    role: 'Product Manager',
    company: 'CloudSync',
    avatar: '/avatars/emily.jpg',
    content:
      'We tried Manus, but Suna Ultra is simply better. The visual workflow builder and 200+ integrations make it incredibly powerful. Our team productivity increased by 40% in the first month.',
    rating: 5,
  },
  {
    name: 'David Kim',
    role: 'VP of Engineering',
    company: 'AutoScale Systems',
    avatar: '/avatars/david.jpg',
    content:
      'The asynchronous task execution is phenomenal. We can now run complex multi-hour workflows without any user interaction. The webhook notifications keep our team in sync perfectly.',
    rating: 5,
  },
  {
    name: 'Lisa Anderson',
    role: 'Head of AI',
    company: 'Quantum Labs',
    avatar: '/avatars/lisa.jpg',
    content:
      'Open source and transparent - that\'s what sealed the deal for us. No black box, no vendor lock-in. The community is amazing, and the SDK makes integration a breeze.',
    rating: 5,
  },
  {
    name: 'Alex Turner',
    role: 'Solo Developer',
    company: 'IndieLab',
    avatar: '/avatars/alex.jpg',
    content:
      'As a solo developer, Suna Ultra feels like having a whole team. The agent marketplace has templates for everything. Started with the free plan and upgraded within a week.',
    rating: 5,
  },
];

function TestimonialCard({ testimonial }: { testimonial: Testimonial }) {
  return (
    <div className="relative rounded-xl border bg-card p-6 shadow-sm transition-all hover:shadow-md">
      <Quote className="absolute top-6 right-6 w-8 h-8 text-muted-foreground/20" />
      
      <div className="flex gap-1 mb-4">
        {Array.from({ length: testimonial.rating }).map((_, i) => (
          <Star key={i} className="w-4 h-4 fill-yellow-500 text-yellow-500" />
        ))}
      </div>

      <p className="text-sm md:text-base text-foreground/90 mb-6 leading-relaxed">
        &ldquo;{testimonial.content}&rdquo;
      </p>

      <div className="flex items-center gap-3">
        <Avatar>
          <AvatarImage src={testimonial.avatar} alt={testimonial.name} />
          <AvatarFallback>
            {testimonial.name
              .split(' ')
              .map((n) => n[0])
              .join('')}
          </AvatarFallback>
        </Avatar>
        <div>
          <p className="font-semibold text-sm">{testimonial.name}</p>
          <p className="text-xs text-muted-foreground">
            {testimonial.role} at {testimonial.company}
          </p>
        </div>
      </div>
    </div>
  );
}

export function TestimonialsSection() {
  return (
    <section className="w-full px-6 py-16 md:py-24 lg:py-32 bg-muted/30">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12 md:mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Trusted by Teams Worldwide
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Don&apos;t just take our word for it. Here&apos;s what our users have to say.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <TestimonialCard testimonial={testimonial} />
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="text-center mt-12"
        >
          <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
            <div className="flex -space-x-2">
              {[1, 2, 3, 4].map((i) => (
                <Avatar key={i} className="w-8 h-8 border-2 border-background">
                  <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                    {String.fromCharCode(64 + i)}
                  </AvatarFallback>
                </Avatar>
              ))}
            </div>
            <span>Join 10,000+ users building with Suna Ultra</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
