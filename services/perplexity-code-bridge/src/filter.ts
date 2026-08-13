import { existsSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import ignore from "ignore";

const ALWAYS_EXCLUDED_PATTERNS = [
  ".git",
  "node_modules",
  ".env",
  ".env.*",
  "*.pem",
  "*.key",
  "id_rsa*",
  ".DS_Store",
  "*.db",
  "*.sqlite"
];

export class PathFilter {
  private ig = ignore();

  constructor(public rootDir: string) {
    this.ig.add(ALWAYS_EXCLUDED_PATTERNS);
    this.loadGitignore();
  }

  private loadGitignore() {
    const gitignorePath = join(this.rootDir, ".gitignore");
    if (existsSync(gitignorePath)) {
      try {
        const content = readFileSync(gitignorePath, "utf-8");
        this.ig.add(content);
      } catch {
        // Ignore read errors
      }
    }
  }

  public isIgnored(absolutePath: string): boolean {
    const relPath = relative(this.rootDir, absolutePath);
    if (!relPath || relPath.startsWith("..")) {
      return true; // Outside root
    }

    const segments = relPath.split("/");
    for (const seg of segments) {
      if (ALWAYS_EXCLUDED_PATTERNS.some(p => p === seg || (p.endsWith("*") && seg.startsWith(p.slice(0, -1))))) {
        return true;
      }
    }

    return this.ig.ignores(relPath);
  }
}
