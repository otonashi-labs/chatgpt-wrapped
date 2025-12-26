/**
 * Simple dev server for ChatGPT Wrapped
 */

import { readFile } from "fs/promises";
import { join } from "path";

const PORT = 9876;
const HTML_FILE = join(import.meta.dir, "../wrapped.html");

Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);
    
    if (url.pathname === "/" || url.pathname === "/wrapped.html") {
      try {
        const html = await readFile(HTML_FILE, "utf-8");
        return new Response(html, {
          headers: { "Content-Type": "text/html" }
        });
      } catch (e) {
        return new Response("Run 'bun run generate' first to create wrapped.html", {
          status: 404
        });
      }
    }
    
    return new Response("Not found", { status: 404 });
  }
});

console.log(`🚀 Server running at http://localhost:${PORT}`);
console.log(`   Open in browser to view your ChatGPT Wrapped!`);

