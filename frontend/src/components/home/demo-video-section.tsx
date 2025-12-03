'use client';

import { motion } from 'framer-motion';
import { Play, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

export function DemoVideoSection() {
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <section className="w-full px-6 py-16 md:py-24 lg:py-32">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            See Suna Ultra in Action
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Watch how autonomous agents collaborate to solve complex tasks in minutes, not hours.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative max-w-5xl mx-auto"
        >
          <div className="relative aspect-video rounded-2xl overflow-hidden border-2 border-primary/20 shadow-2xl bg-gradient-to-br from-primary/5 to-primary/10">
            {!isPlaying ? (
              <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-background/50 to-background/30 backdrop-blur-sm">
                <div className="text-center">
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      size="lg"
                      className="rounded-full w-20 h-20 shadow-xl"
                      onClick={() => setIsPlaying(true)}
                    >
                      <Play className="w-8 h-8 ml-1" />
                    </Button>
                  </motion.div>
                  <p className="mt-4 text-sm font-medium">Watch Demo (2:30)</p>
                </div>
              </div>
            ) : (
              <iframe
                className="absolute inset-0 w-full h-full"
                src="https://www.youtube.com/embed/YOUR_VIDEO_ID?autoplay=1"
                title="Suna Ultra Demo"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
              {/* TODO: Replace YOUR_VIDEO_ID with actual Suna Ultra demo video ID */}
            )}

            {/* Placeholder background - Replace with actual demo screenshot */}
            {!isPlaying && (
              <div className="absolute inset-0 -z-10">
                <div className="w-full h-full bg-gradient-to-br from-primary/20 via-primary/10 to-transparent flex items-center justify-center">
                  <div className="text-center space-y-4 p-8">
                    <Sparkles className="w-16 h-16 mx-auto text-primary/40" />
                    <div className="space-y-2">
                      <div className="h-4 w-64 bg-muted/40 rounded mx-auto" />
                      <div className="h-4 w-48 bg-muted/40 rounded mx-auto" />
                      <div className="h-4 w-56 bg-muted/40 rounded mx-auto" />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Decorative elements */}
          <div className="absolute -top-4 -right-4 w-24 h-24 bg-primary/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-primary/10 rounded-full blur-3xl" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto"
        >
          {[
            {
              title: 'Multi-Agent Collaboration',
              description: 'Watch agents work together seamlessly',
            },
            {
              title: 'Real-Time Execution',
              description: 'See live task progress and results',
            },
            {
              title: 'Complex Workflows',
              description: 'From research to deployment in minutes',
            },
          ].map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
              className="text-center p-6 rounded-lg bg-card border"
            >
              <h3 className="font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
