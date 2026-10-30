import type { NextConfig } from "next";
const backend = process.env.BACKEND_URL || "http://127.0.0.1:8000";
const config: NextConfig = {
  allowedDevOrigins: ["*.e2b.app"],
  experimental: { proxyTimeout: 400000 },
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};
export default config;
