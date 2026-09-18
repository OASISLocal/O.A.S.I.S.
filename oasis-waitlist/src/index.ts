export default {
  async fetch(request: Request, env: Env) {
    const allowedOrigin = "https://oasislocal.github.io";
    const corsHeaders = {
      "Access-Control-Allow-Origin": allowedOrigin,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    const url = new URL(request.url);

    // Endpoint /export — descarga CSV de todos los emails
    if (url.pathname === "/export") {
      const secret = url.searchParams.get("secret");
      if (secret !== env.EXPORT_SECRET) {
        return new Response("Unauthorized", { status: 401 });
      }
      let keys: { name: string }[] = [];
      let cursor: string | undefined;
      do {
        const result = await env.WAITLIST.list({ cursor, limit: 1000 });
        keys = keys.concat(result.keys);
        cursor = result.list_complete ? undefined : result.cursor;
      } while (cursor);
      const rows = await Promise.all(
        keys.map(async (k) => {
          const ts = await env.WAITLIST.get(k.name);
          return `${k.name},${ts || ""}`;
        })
      );
      const csv = "email,joined_at\n" + rows.join("\n");
      return new Response(csv, {
        headers: {
          "Content-Type": "text/csv",
          "Content-Disposition": 'attachment; filename="oasis-waitlist.csv"',
        },
      });
    }

    // Endpoint /collect — recibe emails del formulario
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    const contentLength = parseInt(request.headers.get("Content-Length") || "0");
    if (contentLength > 512) {
      return new Response("Payload too large", { status: 413 });
    }

    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const rlKey = `rl:${ip}`;
    const attempts = parseInt((await env.WAITLIST.get(rlKey)) || "0", 10);
    if (attempts >= 5) {
      return new Response(
        JSON.stringify({ ok: false, error: "too_many_requests" }),
        { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }
    await env.WAITLIST.put(rlKey, String(attempts + 1), { expirationTtl: 3600 });

    let body: { email?: string };
    try {
      body = await request.json();
    } catch {
      return new Response(
        JSON.stringify({ ok: false, error: "invalid_json" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const email = (body.email || "").trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return new Response(
        JSON.stringify({ ok: false, error: "invalid_email" }),
        { status: 422, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const existing = await env.WAITLIST.get(email);
    if (existing) {
      return new Response(
        JSON.stringify({ ok: true, already: true }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    await env.WAITLIST.put(email, new Date().toISOString());

    return new Response(
      JSON.stringify({ ok: true }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  },
};
