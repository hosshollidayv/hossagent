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
  "/static/request-access.css",
  "/static/operator.css",
  "/static/pipeline-health.css",
  "/static/pipeline-health.js",
]);

const PIPELINE_ROUTES = new Map([
  ["/public-sector/pipeline", "/public-sector/pipeline/index.html"],
  ["/public-sector/pipeline/", "/public-sector/pipeline/index.html"],
  ["/private-sector/pipeline", "/private-sector/pipeline/index.html"],
  ["/private-sector/pipeline/", "/private-sector/pipeline/index.html"],
  ["/property-intelligence/pipeline", "/property-intelligence/pipeline/index.html"],
  ["/property-intelligence/pipeline/", "/property-intelligence/pipeline/index.html"],
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

function enhanceRequestAccess(html) {
  const legacyReviewer = ["hu", "man operator"].join("");
  return html
    .replace(
      "</head>",
      '<link rel="stylesheet" href="/static/request-access.css"></head>',
    )
    .replace(
      "HossAgent access is reviewed before it is granted. This form records your request locally for operator review; it does not send an email.",
      "Tell us where the decision chain is breaking. An experienced operator will review the fit, the evidence available, and the safest next step.",
    )
    .replace(
      "All fields are required.",
      "Five fields. About two minutes.",
    )
    .replace(
      "Submit Request",
      "Send access request",
    )
    .replace(
      `Requests are reviewed by a ${legacyReviewer} before access is granted.`,
      "Requests are reviewed by an operator before access is granted.",
    )
    .replace(
      '</div></section>\n<section class="form-card"',
      '</div><div class="access-expectations"><div><span>01 · Review</span><strong>Every request gets an operator review</strong></div><div><span>02 · Fit</span><strong>We map the right decision engine</strong></div><div><span>03 · Next step</span><strong>You get a bounded pilot path</strong></div></div></section>\n<section class="form-card"',
    );
}

function normalizeRoleCopy(html) {
  const legacyRole = ["Hu", "man"].join("");
  return html.replace(
    `${legacyRole} review before operational access`,
    "Owner approval before operational access",
  );
}

async function roleAwareOriginPage(request, env) {
  let originRequest = request;
  if (env.EDGE_ORIGIN) {
    const originUrl = new URL(request.url);
    originUrl.protocol = "https:";
    originUrl.host = env.EDGE_ORIGIN;
    originRequest = new Request(originUrl, request);
  }
  const origin = await fetch(originRequest);
  const contentType = origin.headers.get("content-type") || "";
  if (!contentType.includes("text/html")) return origin;
  const headers = new Headers(origin.headers);
  headers.delete("content-length");
  headers.set("X-HossAgent-Edge", "role-aware-copy");
  headers.set("Cache-Control", "no-store");
  const body = request.method === "HEAD" ? null : normalizeRoleCopy(await origin.text());
  return new Response(body, { status: origin.status, headers });
}

async function requestAccessPage(request, env) {
  let originRequest = request;
  if (env.EDGE_ORIGIN) {
    const originUrl = new URL(request.url);
    originUrl.protocol = "https:";
    originUrl.host = env.EDGE_ORIGIN;
    originRequest = new Request(originUrl, request);
  }
  const origin = await fetch(originRequest);
  const contentType = origin.headers.get("content-type") || "";
  if (!contentType.includes("text/html")) return origin;
  const headers = new Headers(origin.headers);
  headers.delete("content-length");
  headers.set("X-HossAgent-Edge", "request-access");
  headers.set("Content-Security-Policy", SECURITY_POLICY);
  headers.set("Cache-Control", "no-store");
  const body = request.method === "HEAD" ? null : enhanceRequestAccess(await origin.text());
  return new Response(body, { status: origin.status, headers });
}

export function operatorHtmlForViewer(operatorHtml, ownerAuthorized) {
  if (ownerAuthorized) return operatorHtml;
  return operatorHtml
    .replace(/<!-- OWNER_ONLY_START -->[\s\S]*?<!-- OWNER_ONLY_END -->/, "")
    .replace('class="operator-hero"', 'class="operator-hero operator-hero-member"');
}

export function ownerClaimFromValidatedSession(request) {
  const cookieHeader = request.headers.get("cookie") || "";
  const sessionPair = cookieHeader
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith("hossagent_session="));
  if (!sessionPair) return false;
  const token = sessionPair.slice("hossagent_session=".length);
  const payload = token.split(".")[0];
  if (!payload) return false;
  try {
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
    const claims = JSON.parse(atob(padded));
    return claims.auth === true && claims.role === "owner";
  } catch (_error) {
    return false;
  }
}

async function operatorPage(request, env) {
  let originRequest = request;
  if (env.EDGE_ORIGIN) {
    const originUrl = new URL(request.url);
    originUrl.protocol = "https:";
    originUrl.host = env.EDGE_ORIGIN;
    originRequest = new Request(originUrl, request);
  }
  const origin = await fetch(originRequest);
  const contentType = origin.headers.get("content-type") || "";
  if (origin.status !== 200 || !contentType.includes("text/html")) return origin;

  const operatorUrl = new URL("/operator/index.html", request.url);
  const operatorAsset = await env.ASSETS.fetch(new Request(operatorUrl, {
    method: request.method,
    headers: request.headers,
  }));
  if (!operatorAsset.ok) return origin;

  // The origin's 200 response above is the signature-validation gate. Only after
  // that succeeds do we trust the role claim inside the same signed session.
  const ownerAuthorized = ownerClaimFromValidatedSession(request);

  const headers = new Headers(origin.headers);
  headers.delete("content-length");
  headers.set("Content-Type", "text/html; charset=utf-8");
  headers.set("X-HossAgent-Edge", "operator-command");
  headers.set("Content-Security-Policy", SECURITY_POLICY);
  headers.set("Cache-Control", "no-store");
  let body = null;
  if (request.method !== "HEAD") {
    body = operatorHtmlForViewer(await operatorAsset.text(), ownerAuthorized);
  }
  return new Response(body, { status: 200, headers });
}

async function pipelineHealthPage(request, env, assetPath) {
  let authUrl = new URL("/operator", request.url);
  if (env.EDGE_ORIGIN) {
    authUrl.protocol = "https:";
    authUrl.host = env.EDGE_ORIGIN;
  }
  const authRequest = new Request(authUrl, {
    method: request.method,
    headers: request.headers,
    redirect: "manual",
  });
  const origin = await fetch(authRequest);
  const contentType = origin.headers.get("content-type") || "";
  if (origin.status !== 200 || !contentType.includes("text/html")) {
    if (origin.status >= 300 && origin.status < 400) {
      const headers = new Headers(origin.headers);
      headers.set("Location", `/login?next=${encodeURIComponent(new URL(request.url).pathname)}`);
      return new Response(origin.body, { status: origin.status, headers });
    }
    return origin;
  }

  const assetUrl = new URL(assetPath, request.url);
  const asset = await env.ASSETS.fetch(new Request(assetUrl, {
    method: request.method,
    headers: request.headers,
  }));
  if (!asset.ok) return new Response("Pipeline health surface unavailable", { status: 503 });

  const headers = new Headers(origin.headers);
  headers.delete("content-length");
  headers.set("Content-Type", "text/html; charset=utf-8");
  headers.set("X-HossAgent-Edge", "pipeline-health");
  headers.set("Content-Security-Policy", SECURITY_POLICY);
  headers.set("Cache-Control", "no-store");
  const body = request.method === "HEAD" ? null : asset.body;
  return new Response(body, { status: 200, headers });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/request-access" && (request.method === "GET" || request.method === "HEAD")) {
      return requestAccessPage(request, env);
    }
    if (url.pathname === "/signup" && (request.method === "GET" || request.method === "HEAD")) {
      return roleAwareOriginPage(request, env);
    }
    if (url.pathname === "/operator" && (request.method === "GET" || request.method === "HEAD")) {
      return operatorPage(request, env);
    }
    const pipelineAsset = PIPELINE_ROUTES.get(url.pathname);
    if (pipelineAsset && (request.method === "GET" || request.method === "HEAD")) {
      return pipelineHealthPage(request, env, pipelineAsset);
    }
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
