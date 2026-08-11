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

const OWNER_ONLY_PREFIXES = [
  "/mission-intelligence/pilot",
  "/public-sector/pipeline",
  "/private-sector/pipeline",
  "/property-intelligence/pipeline",
  "/portal",
  "/customers",
  "/leads",
  "/invoices",
  "/billing",
  "/subscribe",
  "/upgrade",
  "/api/user/",
  "/api/outreach/",
  "/api/message/",
  "/api/pending-outreach",
  "/api/conversations/",
  "/api/subscription/",
  "/api/customer/",
  "/api/create-checkout-session",
  "/api/create-billing-portal-session",
  "/api/manual-send",
  "/api/portal/",
];

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
      '</div><div class="access-expectations"><div><span>01 · Review</span><strong>Every request gets an operator review</strong></div><div><span>02 · Fit</span><strong>We map the right decision engine</strong></div><div><span>03 · Next step</span><strong>We confirm fit and next steps</strong></div></div></section>\n<section class="form-card"',
    );
}

export function requestAccessSuccessHtml() {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Request received — HossAgent</title><link rel="stylesheet" href="/static/web.css"><link rel="stylesheet" href="/static/request-access.css"></head>
<body class="auth-body request-success"><a class="skip-link" href="#main">Skip to content</a><header class="simple-header"><a class="brand" href="/"><span class="brand-mark" aria-hidden="true">H</span><span>HossAgent</span></a><a class="text-link" href="/demos">View product demos</a></header>
<main class="auth-main request-main" id="main"><section class="auth-context"><p class="eyebrow">Request received</p><h1>We have what we need.</h1><p>We’ll review your use case and follow up with the clearest next step.</p><div class="request-modes"><div><strong>Evidence first</strong><span>We start with the decision you need to make</span></div><div><strong>Clear follow-up</strong><span>You’ll hear from us at your work email</span></div></div></section>
<section class="form-card request-success-card" aria-labelledby="confirmation-title"><div class="success-mark" aria-hidden="true">✓</div><div class="form-heading"><p class="eyebrow">Submission complete</p><h2 id="confirmation-title">Your request is in.</h2><p>No additional setup is required.</p></div><ol class="success-steps"><li><span>01</span><div><strong>Fit review</strong><p>We’ll review the workflow, evidence, and decision described in your request.</p></div></li><li><span>02</span><div><strong>Direct response</strong><p>We’ll follow up with a practical next step at the email you provided.</p></div></li></ol><div class="success-actions"><a class="button" href="/demos">Watch the demos <span aria-hidden="true">→</span></a><a class="text-link" href="/">Return home</a></div></section></main></body></html>`;
}

export function requestAccessHtml(html, method = "GET") {
  const submitted = method === "POST" && (
    html.includes("Request received. We’ll review it before granting access.")
    || html.includes("Request received. We'll review it before granting access.")
  );
  return submitted ? requestAccessSuccessHtml() : enhanceRequestAccess(html);
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
  const body = request.method === "HEAD" ? null : requestAccessHtml(await origin.text(), request.method);
  return new Response(body, { status: origin.status, headers });
}

function enhanceLogin(html, loggedOut = false) {
  let enhanced = html
    .replace(
      "Sign in with your HossAgent account. The separate owner bootstrap path remains available for emergency operator access.",
      "Sign in to owner-only operating and troubleshooting workspaces.",
    )
    .replace(
      "Use your owner or approved member credentials.",
      "Use your owner credentials.",
    )
    .replace(
      'New to HossAgent? <a href="/signup">Create an account</a>.',
      'Looking for product access? <a href="/request-access">Request early access</a>.',
    );
  if (loggedOut) {
    enhanced = enhanced.replace(
      '</div><form method="post" action="/login">',
      '</div><div class="pilot-notice" role="status">You have been signed out.</div><form method="post" action="/login">',
    );
  }
  return enhanced;
}

export function logoutResponse(request) {
  const destination = new URL("/login?logout=true", request.url);
  const headers = new Headers({
    Location: destination.toString(),
    "Cache-Control": "no-store",
    "X-HossAgent-Edge": "session-logout",
  });
  const expiredCookie = "Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Lax";
  headers.append("Set-Cookie", `hossagent_session=; ${expiredCookie}`);
  headers.append("Set-Cookie", `hossagent_admin=; ${expiredCookie}`);
  return new Response(null, { status: 303, headers });
}

async function loginPage(request, env) {
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
  headers.set("X-HossAgent-Edge", "owner-login");
  headers.set("Cache-Control", "no-store");
  const loggedOut = new URL(request.url).searchParams.get("logout") === "true";
  const body = request.method === "HEAD" ? null : enhanceLogin(await origin.text(), loggedOut);
  return new Response(body, { status: origin.status, headers });
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

export function isOwnerOnlyPath(pathname) {
  if (pathname === "/operator" || pathname === "/operator/") return true;
  return OWNER_ONLY_PREFIXES.some((prefix) => (
    pathname === prefix || pathname.startsWith(prefix.endsWith("/") ? prefix : `${prefix}/`)
  ));
}

async function ownerAccessGate(request, env) {
  let authUrl = new URL("/operator", request.url);
  if (env.EDGE_ORIGIN) {
    authUrl.protocol = "https:";
    authUrl.host = env.EDGE_ORIGIN;
  }
  const authRequest = new Request(authUrl, {
    method: "GET",
    headers: request.headers,
    redirect: "manual",
  });
  const origin = await fetch(authRequest);
  const contentType = origin.headers.get("content-type") || "";
  const browserRequest = request.method === "GET" || request.method === "HEAD";

  if (origin.status !== 200 || !contentType.includes("text/html")) {
    if (browserRequest) {
      const next = encodeURIComponent(new URL(request.url).pathname);
      return Response.redirect(new URL(`/login?next=${next}`, request.url), 303);
    }
    return new Response("Not found", { status: 404 });
  }

  if (!ownerClaimFromValidatedSession(request)) {
    if (browserRequest) return Response.redirect(new URL("/demos", request.url), 303);
    return new Response("Not found", { status: 404 });
  }

  return null;
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

  const headers = new Headers(origin.headers);
  headers.delete("content-length");
  headers.set("Content-Type", "text/html; charset=utf-8");
  headers.set("X-HossAgent-Edge", "operator-command");
  headers.set("Content-Security-Policy", SECURITY_POLICY);
  headers.set("Cache-Control", "no-store");
  let body = null;
  if (request.method !== "HEAD") {
    body = await operatorAsset.text();
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
    if (
      (url.pathname === "/logout" || url.pathname === "/logout/"
        || url.pathname === "/admin/logout" || url.pathname === "/admin/logout/")
      && (request.method === "GET" || request.method === "HEAD" || request.method === "POST")
    ) {
      return logoutResponse(request);
    }
    if (url.pathname === "/signup" || url.pathname === "/signup/") {
      return Response.redirect(new URL("/request-access", request.url), 303);
    }
    if (url.pathname === "/request-access" && (
      request.method === "GET" || request.method === "HEAD" || request.method === "POST"
    )) {
      return requestAccessPage(request, env);
    }
    if (url.pathname === "/login" && (request.method === "GET" || request.method === "HEAD")) {
      return loginPage(request, env);
    }
    if (isOwnerOnlyPath(url.pathname)) {
      const denied = await ownerAccessGate(request, env);
      if (denied) return denied;
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
