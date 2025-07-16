/** @type {import('next').NextConfig} */
const nextConfig = {
  devIndicators: false,
  output: 'standalone',
  // Proxy /chat requests to the backend server
  async rewrites() {
    return [
      {
        source: "/chat",
        destination: process.env.BACKEND_URL || "http://127.0.0.1:8000/chat",
      },
    ];
  },
};

export default nextConfig;
