const EDGE_ROUTES = new Map([
  ["/", "/index.html"],
  ["/demos", "/demos/index.html"],
  ["/demos/", "/demos/index.html"],
  ["/mission-intelligence", "/mission-intelligence/index.html"],
  ["/mission-intelligence/", "/mission-intelligence/index.html"],
  ["/mission-intelligence/demo", "/mission-intelligence/demo/index.html"],
  ["/mission-intelligence/demo/", "/mission-intelligence/demo/index.html"],
  ["/public-sector/demo", "/public-sector/demo/index.html"],
  ["/public-sector/demo/", "/public-sector/demo/index.html"],
  ["/private-sector/demo", "/private-sector/demo/index.html"],
  ["/private-sector/demo/", "/private-sector/demo/index.html"],
  ["/property-intelligence/demo", "/property-intelligence/demo/index.html"],
  ["/property-intelligence/demo/", "/property-intelligence/demo/index.html"],
]);

const EDGE_ASSETS = new Set([
  "/static/web.css",
  "/static/mission-demo.css",
  "/static/mission-demo.js",
  "/static/portfolio-demo.css",
  "/static/product-demo.js",
]);

const SECURITY_POLICY = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data:",
  "connect-src 'self'",
  "base-uri 'none'",
  "frame-ancestors 'none'",
  "form-action 'self'",
].join("; ");

async function edgeAsset(request, env, assetPath, isHtml) {
  const assetUrl = new URL(assetPath, request.url);
  const assetRequest = new Request(assetUrl, {
    method: request.method,
    headers: request.headers,
  });
  const asset = await env.ASSETS.fetch(assetRequest);
  const headers = new Headers(asset.headers);
  headers.set("X-HossAgent-Edge", "product-demos");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("X-Frame-Options", "DENY");
  headers.set("Referrer-Policy", "no-referrer");
  if (isHtml) {
    headers.set("Content-Type", "text/html; charset=utf-8");
    headers.set("Cache-Control", "no-cache");
    headers.set("Content-Security-Policy", SECURITY_POLICY);
  } else {
    headers.set("Cache-Control", "public, max-age=300, must-revalidate");
  }
  return new Response(asset.body, { status: asset.status, headers });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pageAsset = EDGE_ROUTES.get(url.pathname);
    if (pageAsset && (request.method === "GET" || request.method === "HEAD")) {
      return edgeAsset(request, env, pageAsset, true);
    }
    if (EDGE_ASSETS.has(url.pathname) && (request.method === "GET" || request.method === "HEAD")) {
      return edgeAsset(request, env, url.pathname, false);
    }
    return fetch(request);
  },
};
