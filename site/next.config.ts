import type { NextConfig } from "next";
import { BASE } from "./lib/config";

const nextConfig: NextConfig = {
  output: "export",
  basePath: BASE,
  assetPrefix: BASE,
  trailingSlash: true,
  images: { unoptimized: true },
  reactStrictMode: true,
};

export default nextConfig;
