'use client';

import { motion } from 'framer-motion';
import { Check, Sparkles, Zap, Crown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface PricingTier {
  name: string;
  price: string;
  description: string;
  features: string[];
  icon: any;
  popular?: boolean;
  cta: string;
}

const pricingTiers: PricingTier[] = [
  {
    name: 'Free',
    price: '$0',
    description: 'Perfect for getting started',
    icon: Sparkles,
    features: [
      '5 agents per month',
      'Basic agent templates',
      '1,000 API calls/month',
      'Community support',
      'Basic analytics',
      'Single user workspace',
    ],
    cta: 'Get Started Free',
  },
  {
    name: 'Pro',
    price: '$29',
    description: 'For power users and small teams',
    icon: Zap,
    popular: true,
    features: [
      'Unlimited agents',
      'All agent templates',
      '50,000 API calls/month',
      'Priority support',
      'Advanced analytics',
      'Team collaboration (5 users)',
      'Custom workflows',
      'Browser automation',
      'Multi-modal capabilities',
    ],
    cta: 'Start Pro Trial',
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    description: 'For organizations at scale',
    icon: Crown,
    features: [
      'Everything in Pro',
      'Unlimited API calls',
      'Dedicated support',
      'Custom integrations',
      'SSO & SAML',
      'Advanced security (RBAC)',
      'Audit logs',
      'SLA guarantee',
      'On-premise deployment',
      'Custom agent development',
    ],
    cta: 'Contact Sales',
  },
];

export function PricingSection() {
  return (
    <section className="w-full px-6 py-16 md:py-24 lg:py-32">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12 md:mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Start free, scale as you grow. No hidden fees, cancel anytime.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {pricingTiers.map((tier, index) => {
            const Icon = tier.icon;
            return (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={cn(
                  'relative rounded-2xl border bg-card p-8 shadow-sm transition-all hover:shadow-lg',
                  tier.popular && 'border-primary shadow-primary/20 scale-105'
                )}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="inline-flex items-center gap-1 rounded-full bg-primary px-4 py-1 text-xs font-semibold text-primary-foreground">
                      <Sparkles className="w-3 h-3" />
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={cn(
                      'flex items-center justify-center w-10 h-10 rounded-lg',
                      tier.popular ? 'bg-primary text-primary-foreground' : 'bg-muted'
                    )}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="text-2xl font-bold">{tier.name}</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">{tier.description}</p>
                </div>

                <div className="mb-6">
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold">{tier.price}</span>
                    {tier.price !== 'Custom' && (
                      <span className="text-muted-foreground">/month</span>
                    )}
                  </div>
                </div>

                <Button
                  className={cn(
                    'w-full mb-6',
                    tier.popular && 'bg-primary hover:bg-primary/90'
                  )}
                  variant={tier.popular ? 'default' : 'outline'}
                >
                  {tier.cta}
                </Button>

                <ul className="space-y-3">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            );
          })}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-center mt-12"
        >
          <p className="text-sm text-muted-foreground mb-4">
            All plans include 14-day free trial. No credit card required.
          </p>
          <p className="text-sm text-muted-foreground">
            Need a custom plan? <a href="#" className="text-primary hover:underline">Contact our sales team</a>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
