import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

/**
 * 0-Token Metadata Extractor
 * Extracts telemetry from the target file without loading the entire content into memory,
 * preserving token context window space for triage models.
 * 
 * @param {string} filePath - Absolute path to the file.
 * @returns {object} Metadata map containing size, line count, head, tail, and mime-type.
 */
export function extractMetadata(filePath) {
  const absolutePath = path.resolve(filePath);

  if (!fs.existsSync(absolutePath)) {
    throw new Error(`File does not exist: ${absolutePath}`);
  }

  const stat = fs.statSync(absolutePath);
  if (!stat.isFile()) {
    return {
      path: absolutePath,
      isFile: false,
      isDirectory: stat.isDirectory(),
      sizeBytes: stat.size,
    };
  }

  // Get MIME type using macOS native 'file' command to avoid scanning raw binary files
  let mimeType = 'unknown';
  try {
    mimeType = execSync(`file -b --mime-type "${absolutePath}"`, { encoding: 'utf8' }).trim();
  } catch (err) {
    mimeType = 'text/plain'; // Safe default fallback
  }

  // Detect binary signatures
  const isBinary = mimeType.startsWith('image/') || 
                   mimeType.startsWith('video/') || 
                   mimeType.startsWith('audio/') || 
                   mimeType.startsWith('application/octet-stream') || 
                   mimeType.includes('binary') ||
                   /\.(zip|tar|gz|exe|dll|so|dylib|png|jpg|gif|pdf|mp3|mp4|webm)$/i.test(absolutePath);

  let lineCount = 0;
  let headLines = [];
  let tailLines = [];

  if (!isBinary) {
    try {
      // Native fast line counting using 'wc -l'
      const wcOut = execSync(`wc -l "${absolutePath}"`, { encoding: 'utf8' }).trim();
      lineCount = parseInt(wcOut.split(/\s+/)[0], 10);
    } catch (err) {
      // Inline line counting fallback for small files
      if (stat.size < 5 * 1024 * 1024) {
        const content = fs.readFileSync(absolutePath, 'utf8');
        lineCount = content.split('\n').length;
      }
    }

    try {
      // Extract top 5 lines natively
      const headOut = execSync(`head -n 5 "${absolutePath}"`, { encoding: 'utf8' });
      headLines = headOut.split('\n').map(line => line.trimEnd());
    } catch (err) {
      // Fallback
    }

    try {
      // Extract bottom 5 lines natively
      const tailOut = execSync(`tail -n 5 "${absolutePath}"`, { encoding: 'utf8' });
      tailLines = tailOut.split('\n').map(line => line.trimEnd());
    } catch (err) {
      // Fallback
    }
  }

  return {
    path: absolutePath,
    isFile: true,
    sizeBytes: stat.size,
    sizeHuman: (stat.size / 1024).toFixed(2) + ' KB',
    mimeType,
    isBinary,
    lineCount,
    head: headLines.filter(line => line !== ''),
    tail: tailLines.filter(line => line !== ''),
  };
}
