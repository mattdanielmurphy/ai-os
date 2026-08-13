import { readdirSync, statSync, readFileSync, existsSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { PathFilter } from "./filter.js";
import { renderDirectoryView, renderFileView, renderManifestView } from "./views.js";

export function createBridgeServer(rootDir: string, expectedToken: string, validateAuth: (req: Request, token: string) => boolean) {
  const absoluteRootDir = resolve(rootDir);
  const filter = new PathFilter(absoluteRootDir);

  return {
    fetch(req: Request): Response {
      if (!validateAuth(req, expectedToken)) {
        return new Response("Unauthorized: Invalid or missing token parameter", {
          status: 401,
          headers: { "Content-Type": "text/plain" }
        });
      }

      const url = new URL(req.url);
      const pathname = decodeURIComponent(url.pathname);

      const headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
      };

      if (pathname === "/manifest") {
        const fileList: { path: string; size: number }[] = [];
        function walk(currentDir: string) {
          const entries = readdirSync(currentDir, { withFileTypes: true });
          for (const entry of entries) {
            const fullPath = join(currentDir, entry.name);
            if (filter.isIgnored(fullPath)) continue;

            if (entry.isDirectory()) {
              walk(fullPath);
            } else if (entry.isFile()) {
              const rel = relative(absoluteRootDir, fullPath);
              const stat = statSync(fullPath);
              fileList.push({ path: rel, size: stat.size });
            }
          }
        }
        walk(absoluteRootDir);
        return new Response(renderManifestView(fileList, expectedToken), { headers });
      }

      const relSubPath = pathname.startsWith("/") ? pathname.slice(1) : pathname;
      const targetPath = relSubPath === "" ? absoluteRootDir : resolve(join(absoluteRootDir, relSubPath));

      if (!targetPath.startsWith(absoluteRootDir)) {
        return new Response("Forbidden: Path traversal blocked", { status: 403, headers: { "Content-Type": "text/plain" } });
      }

      if (!existsSync(targetPath) || (targetPath !== absoluteRootDir && filter.isIgnored(targetPath))) {
        return new Response("Not Found", { status: 404, headers: { "Content-Type": "text/plain" } });
      }

      const stat = statSync(targetPath);
      if (stat.isDirectory()) {
        const entries = readdirSync(targetPath, { withFileTypes: true });
        const items = entries
          .map(entry => {
            const full = join(targetPath, entry.name);
            if (filter.isIgnored(full)) return null;
            const rel = relative(absoluteRootDir, full);
            const isDir = entry.isDirectory();
            const size = isDir ? undefined : statSync(full).size;
            return { name: entry.name, isDir, path: `/${rel}`, size };
          })
          .filter((item): item is NonNullable<typeof item> => item !== null);

        const currentRelDir = relative(absoluteRootDir, targetPath) || "root";
        return new Response(renderDirectoryView(currentRelDir, items, expectedToken), { headers });
      } else {
        try {
          const content = readFileSync(targetPath, "utf-8");
          const relFile = relative(absoluteRootDir, targetPath);
          return new Response(renderFileView(relFile, content), { headers });
        } catch (err) {
          return new Response("Error reading file", { status: 500, headers: { "Content-Type": "text/plain" } });
        }
      }
    }
  };
}
