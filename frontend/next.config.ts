import type { NextConfig } from 'next';

const nextConfig = (): NextConfig => ({
  // For GitHub Pages static export
  output: process.env.GITHUB_PAGES === 'true' ? 'export' : ((process.env.NEXT_OUTPUT as 'standalone') || undefined),
  
  // GitHub Pages base path (repository name)
  basePath: process.env.GITHUB_PAGES === 'true' ? '/suna-enhanced' : '',
  assetPrefix: process.env.GITHUB_PAGES === 'true' ? '/suna-enhanced/' : '',
  
  // For static export, disable features that require server
  trailingSlash: process.env.GITHUB_PAGES === 'true' ? true : undefined,
  
  // Performance optimizations
  experimental: process.env.GITHUB_PAGES === 'true' ? undefined : {
    // Optimize package imports for faster builds and smaller bundles
    optimizePackageImports: [
      'lucide-react',
      'framer-motion',
      '@radix-ui/react-icons',
      'recharts',
      'date-fns',
      '@tanstack/react-query',
      'react-icons',
    ],
  },
  
  // Enable compression
  compress: true,
  
  // Optimize images
  images: {
    unoptimized: process.env.GITHUB_PAGES === 'true' ? true : false,
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
  },
  
  // Rewrites and headers don't work with static export
  async rewrites() {
    if (process.env.GITHUB_PAGES === 'true') return [];
    return [
      {
        source: '/ingest/static/:path*',
        destination: 'https://eu-assets.i.posthog.com/static/:path*',
      },
      {
        source: '/ingest/:path*',
        destination: 'https://eu.i.posthog.com/:path*',
      },
      {
        source: '/ingest/flags',
        destination: 'https://eu.i.posthog.com/flags',
      },
    ];
  },
  
  // HTTP headers for caching and performance
  async headers() {
    if (process.env.GITHUB_PAGES === 'true') return [];
    return [
      {
        source: '/fonts/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/:path*.woff2',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  
  skipTrailingSlashRedirect: true,
});

export default nextConfig;
