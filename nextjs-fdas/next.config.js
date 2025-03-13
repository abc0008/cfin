/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  webpack: (config) => {
    // Support loading PDF files
    config.module.rules.push({
      test: /\.pdf$/,
      use: [
        {
          loader: 'file-loader',
          options: {
            name: '[path][name].[ext]',
          },
        },
      ],
    });
    return config;
  },
  // For PDF Highlighter compatibility
  transpilePackages: ["react-pdf-highlighter"],
};

module.exports = nextConfig;