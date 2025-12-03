'use client';

import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';

interface Feature {
  name: string;
  sunaUltra: boolean | string;
  manus: boolean | string;
  chatgpt: boolean | string;
  claude: boolean | string;
}

const features: Feature[] = [
  {
    name: 'Multi-Agent Orchestration',
    sunaUltra: true,
    manus: false,
    chatgpt: false,
    claude: false,
  },
  {
    name: 'Open Source & Self-Hosted',
    sunaUltra: true,
    manus: false,
    chatgpt: false,
    claude: false,
  },
  {
    name: 'Asynchronous Task Execution',
    sunaUltra: true,
    manus: true,
    chatgpt: false,
    claude: false,
  },
  {
    name: 'Browser Automation',
    sunaUltra: true,
    manus: true,
    chatgpt: false,
    claude: false,
  },
  {
    name: 'Custom Agent Templates',
    sunaUltra: true,
    manus: 'Limited',
    chatgpt: false,
    claude: false,
  },
  {
    name: 'Visual Workflow Builder',
    sunaUltra: true,
    manus: false,
    chatgpt: false,
    claude: false,
  },
  {
    name: 'Agent Debugging & Observability',
    sunaUltra: true,
    manus: 'Basic',
    chatgpt: false,
    claude: false,
  },
  {
    name: 'Local LLM Support',
    sunaUltra: true,
    manus: false,
    chatgpt: false,
    claude: false,
  },
  {
    name: 'Tool Integrations',
    sunaUltra: '200+',
    manus: '50+',
    chatgpt: '10+',
    claude: '5+',
  },
  {
    name: 'Team Collaboration',
    sunaUltra: true,
    manus: true,
    chatgpt: 'Limited',
    claude: false,
  },
  {
    name: 'Enterprise Security (RBAC, Audit)',
    sunaUltra: true,
    manus: true,
    chatgpt: 'Limited',
    claude: false,
  },
  {
    name: 'API & SDK Access',
    sunaUltra: true,
    manus: 'API Only',
    chatgpt: true,
    claude: true,
  },
];

function FeatureCell({ value }: { value: boolean | string }) {
  if (typeof value === 'string') {
    return (
      <div className="flex items-center justify-center">
        <span className="text-sm font-medium text-foreground/80">{value}</span>
      </div>
    );
  }
  
  return (
    <div className="flex items-center justify-center">
      {value ? (
        <Check className="w-5 h-5 text-green-500" />
      ) : (
        <X className="w-5 h-5 text-muted-foreground/30" />
      )}
    </div>
  );
}

export function FeatureComparisonSection() {
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
            Why Choose Suna Ultra?
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            See how we stack up against the competition. Spoiler: We win.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="overflow-x-auto rounded-lg border bg-card"
        >
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-6 py-4 text-left font-semibold">Feature</th>
                <th className="px-6 py-4 text-center font-semibold">
                  <div className="flex flex-col items-center">
                    <span className="text-primary">Suna Ultra</span>
                    <span className="text-xs text-muted-foreground font-normal">(You)</span>
                  </div>
                </th>
                <th className="px-6 py-4 text-center font-semibold">Manus AI</th>
                <th className="px-6 py-4 text-center font-semibold">ChatGPT</th>
                <th className="px-6 py-4 text-center font-semibold">Claude</th>
              </tr>
            </thead>
            <tbody>
              {features.map((feature, index) => (
                <motion.tr
                  key={feature.name}
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="border-b hover:bg-muted/30 transition-colors"
                >
                  <td className="px-6 py-4 font-medium">{feature.name}</td>
                  <td className="px-6 py-4 bg-primary/5">
                    <FeatureCell value={feature.sunaUltra} />
                  </td>
                  <td className="px-6 py-4">
                    <FeatureCell value={feature.manus} />
                  </td>
                  <td className="px-6 py-4">
                    <FeatureCell value={feature.chatgpt} />
                  </td>
                  <td className="px-6 py-4">
                    <FeatureCell value={feature.claude} />
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-center mt-8"
        >
          <p className="text-sm text-muted-foreground">
            * Feature comparison based on publicly available information as of December 2024
          </p>
        </motion.div>
      </div>
    </section>
  );
}
