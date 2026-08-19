---
title: "Implement Whisper Audio Transcription"
date: "2026-08-03"
conversation_id: "db1d4448-ed35-46e9-a063-b9ea122f85c7"
source: "antigravity"
---

# Implement Whisper Audio Transcription

## User

Please update `/Users/matt/projects/video-context-agent/src/subs-extractor.ts` to add Stage 5: Local audio transcription via `whisper-cli`.

In `ensureSubtitlesCached()`:
After Step 4 (yt-dlp), add Step 5:
- Check if `whisper-cli` model file exists at `~/.cache/whisper/ggml-base.en.bin` (expand `~` to `process.env.HOME || ''`).
- Log `'No online subtitles found. Running fast audio transcription via whisper-cli...'`.
- Extract audio using `ffmpeg`: `ffmpeg -y -i ${filePath} -ar 16000 -ac 1 -c:a pcm_s16le ${wavPath}` (where wavPath is `${this.tmpDir}/${hash}.wav`).
- Run `whisper-cli -m ${modelPath} -f ${wavPath} -osrt -of ${outPrefix}` (where outPrefix is `${this.tmpDir}/${hash}`).
- If `${outPrefix}.srt` is generated, copy to `cachedPath` and return `cachedPath`.
- Clean up temporary wav file if created.
- Handle any errors gracefully.

---

## Assistant

Created At: 2026-08-03T17:21:40-06:00
Completed At: 2026-08-03T17:21:40-06:00
File Path: `file:///Users/matt/projects/video-context-agent/src/subs-extractor.ts`
Total Lines: 214
Total Bytes: 7476
Showing lines 1 to 214
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { $ } from 'bun';
2: import fs from 'fs';
3: import path from 'path';
4: import crypto from 'crypto';
5: 
6: export class SubsExtractor {
7:   private tmpDir: string;
8: 
9:   constructor(tmpDir: string = './tmp') {
10:     this.tmpDir = tmpDir;
11:     if (!fs.existsSync(this.tmpDir)) {
12:       fs.mkdirSync(this.tmpDir, { recursive: true });
13:     }
14:   }
15: 
16:   private hashFilePath(filePath: string): string {
17:     return crypto.createHash('md5').update(filePath).digest('hex');
18:   }
19: 
20:   private isValidFile(filePath: string): boolean {
21:     try {
22:       return fs.existsSync(filePath) && fs.statSync(filePath).size > 0;
23:     } catch {
24:       return false;
25:     }
26:   }
27: 
28:   private removeEmptyFile(filePath: string): void {
29:     try {
30:       if (fs.existsSync(filePath) && fs.statSync(filePath).size === 0) {
31:         fs.unlinkSync(filePath);
32:       }
33:     } catch {}
34:   }
35: 
36:   public convertVttToSrt(vttContent: string): string {
37:     const content = vttContent.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
38:     const rawBlocks = content.split(/\n\s*\n/);
39:     const srtBlocks: string[] = [];
40:     let counter = 1;
41: 
42:     for (const block of rawBlocks) {
43:       const lines = block.split('\n').map(l => l.trim()).filter(l => l.length > 0);
44:       if (lines.length === 0) continue;
45: 
46:       const timeLineIndex = lines.findIndex(l => l.includes('-->'));
47:       if (timeLineIndex === -1) continue;
48: 
49:       const timeLine = lines[timeLineIndex];
50:       if (!ti
<truncated 4886 bytes>
 file);
171:           if (this.isValidFile(fullPath)) {
172:             if (file.endsWith('.vtt')) {
173:               const content = fs.readFileSync(fullPath, 'utf-8');
174:               fs.writeFileSync(cachedPath, this.convertVttToSrt(content));
175:             } else if (fullPath !== cachedPath) {
176:               fs.copyFileSync(fullPath, cachedPath);
177:             }
178:             if (this.isValidFile(cachedPath)) return cachedPath;
179:           }
180:         }
181:       } catch {}
182:     }
183: 
184:     // Step 4: If filePath is a streaming URL (http/https), attempt yt-dlp --skip-download --write-sub --write-auto-sub --sub-lang en
185:     if (isUrl) {
186:       try {
187:         const outTemplate = path.join(this.tmpDir, hash);
188:         await $`yt-dlp --skip-download --write-sub --write-auto-sub --sub-lang en -o ${outTemplate} ${filePath}`.quiet();
189:         if (this.isValidFile(cachedPath)) return cachedPath;
190: 
191:         const files = fs.readdirSync(this.tmpDir).filter(f => f.startsWith(hash));
192:         for (const file of files) {
193:           const fullPath = path.join(this.tmpDir, file);
194:           if (this.isValidFile(fullPath)) {
195:             if (file.endsWith('.vtt')) {
196:               const vttContent = fs.readFileSync(fullPath, 'utf-8');
197:               const srtContent = this.convertVttToSrt(vttContent);
198:               fs.writeFileSync(cachedPath, srtContent);
199:               if (this.isValidFile(cachedPath)) return cachedPath;
200:             } else if (file.endsWith('.srt')) {
201:               if (fullPath !== cachedPath) {
202:                 fs.copyFileSync(fullPath, cachedPath);
203:               }
204:               if (this.isValidFile(cachedPath)) return cachedPath;
205:             }
206:           }
207:         }
208:       } catch {}
209:     }
210: 
211:     return this.isValidFile(cachedPath) ? cachedPath : null;
212:   }
213: }
214: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-03T17:21:44-06:00
Completed At: 2026-08-03T17:21:44-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/video-context-agent/src/subs-extractor.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -206,6 +206,36 @@
           }
         }
       } catch {}
+    // Step 5: Local audio transcription via whisper-cli
+    const homeDir = process.env.HOME || '';
+    const modelPath = path.join(homeDir, '.cache', 'whisper', 'ggml-base.en.bin');
+
+    if (fs.existsSync(modelPath)) {
+      console.log('No online subtitles found. Running fast audio transcription via whisper-cli...');
+      const wavPath = path.join(this.tmpDir, `${hash}.wav`);
+      const outPrefix = path.join(this.tmpDir, hash);
+      const generatedSrt = `${outPrefix}.srt`;
+
+      try {
+        await $`ffmpeg -y -i ${filePath} -ar 16000 -ac 1 -c:a pcm_s16le ${wavPath}`.quiet();
+        await $`whisper-cli -m ${modelPath} -f ${wavPath} -osrt -of ${outPrefix}`.quiet();
+        if (this.isValidFile(generatedSrt)) {
+          if (generatedSrt !== cachedPath) {
+            fs.copyFileSync(generatedSrt, cachedPath);
+          }
+          if (this.isValidFile(cachedPath)) {
+            return cachedPath;
+          }
+        }
+      } catch {
+        // Handle any errors gracefully
+      } finally {
+        if (fs.existsSync(wavPath)) {
+          try {
+            fs.unlinkSync(wavPath);
+          } catch {}
+        }
+      }
     }
 
     return this.isValidFile(cachedPath) ? cachedPath : null;
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-03T17:21:47-06:00
Completed At: 2026-08-03T17:21:47-06:00
File Path: `file:///Users/matt/projects/video-context-agent/src/subs-extractor.ts`
Total Lines: 244
Total Bytes: 8617
Showing lines 180 to 244
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
180:         }
181:       } catch {}
182:     }
183: 
184:     // Step 4: If filePath is a streaming URL (http/https), attempt yt-dlp --skip-download --write-sub --write-auto-sub --sub-lang en
185:     if (isUrl) {
186:       try {
187:         const outTemplate = path.join(this.tmpDir, hash);
188:         await $`yt-dlp --skip-download --write-sub --write-auto-sub --sub-lang en -o ${outTemplate} ${filePath}`.quiet();
189:         if (this.isValidFile(cachedPath)) return cachedPath;
190: 
191:         const files = fs.readdirSync(this.tmpDir).filter(f => f.startsWith(hash));
192:         for (const file of files) {
193:           const fullPath = path.join(this.tmpDir, file);
194:           if (this.isValidFile(fullPath)) {
195:             if (file.endsWith('.vtt')) {
196:               const vttContent = fs.readFileSync(fullPath, 'utf-8');
197:               const srtContent = this.convertVttToSrt(vttContent);
198:               fs.writeFileSync(cachedPath, srtContent);
199:               if (this.isValidFile(cachedPath)) return cachedPath;
200:             } else if (file.endsWith('.srt')) {
201:               if (fullPath !== cachedPath) {
202:                 fs.copyFileSync(fullPath, cachedPath);
203:               }
204:               if (this.isValidFile(cachedPath)) return cachedPath;
205:             }
206:           }
207:         }
208:       } catch {}
209:     // Step 5: Local audio transcription via whisper-cli
210:     const homeDir = process.env.HOME || '';
211:     const modelPath = path.join(homeDir, '.cache', 'whisper', 'ggml-base.en.bin');
212: 
213:     if (fs.existsSync(modelPath)) {
214:       console.log('No online subtitles found. Running fast audio transcription via whisper-cli...');
215:       const wavPath = path.join(this.tmpDir, `${hash}.wav`);
216:       const outPrefix = path.join(this.tmpDir, hash);
217:       const generatedSrt = `${outPrefix}.srt`;
218: 
219:       try {
220:         await $`ffmpeg -y -i ${filePath} -ar 16000 -ac 1 -c:a pcm_s16le ${wavPath}`.quiet();
221:         await $`whisper-cli -m ${modelPath} -f ${wavPath} -osrt -of ${outPrefix}`.quiet();
222:         if (this.isValidFile(generatedSrt)) {
223:           if (generatedSrt !== cachedPath) {
224:             fs.copyFileSync(generatedSrt, cachedPath);
225:           }
226:           if (this.isValidFile(cachedPath)) {
227:             return cachedPath;
228:           }
229:         }
230:       } catch {
231:         // Handle any errors gracefully
232:       } finally {
233:         if (fs.existsSync(wavPath)) {
234:           try {
235:             fs.unlinkSync(wavPath);
236:           } catch {}
237:         }
238:       }
239:     }
240: 
241:     return this.isValidFile(cachedPath) ? cachedPath : null;
242:   }
243: }
244: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T17:21:50-06:00
Completed At: 2026-08-03T17:21:50-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/video-context-agent/src/subs-extractor.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -206,6 +206,8 @@
           }
         }
       } catch {}
+    }
+
     // Step 5: Local audio transcription via whisper-cli
     const homeDir = process.env.HOME || '';
     const modelPath = path.join(homeDir, '.cache', 'whisper', 'ggml-base.en.bin');
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-03T17:21:53-06:00
Completed At: 2026-08-03T17:21:54-06:00
File Path: `file:///Users/matt/projects/video-context-agent/src/subs-extractor.ts`
Total Lines: 246
Total Bytes: 8624
Showing lines 180 to 245
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
180:         }
181:       } catch {}
182:     }
183: 
184:     // Step 4: If filePath is a streaming URL (http/https), attempt yt-dlp --skip-download --write-sub --write-auto-sub --sub-lang en
185:     if (isUrl) {
186:       try {
187:         const outTemplate = path.join(this.tmpDir, hash);
188:         await $`yt-dlp --skip-download --write-sub --write-auto-sub --sub-lang en -o ${outTemplate} ${filePath}`.quiet();
189:         if (this.isValidFile(cachedPath)) return cachedPath;
190: 
191:         const files = fs.readdirSync(this.tmpDir).filter(f => f.startsWith(hash));
192:         for (const file of files) {
193:           const fullPath = path.join(this.tmpDir, file);
194:           if (this.isValidFile(fullPath)) {
195:             if (file.endsWith('.vtt')) {
196:               const vttContent = fs.readFileSync(fullPath, 'utf-8');
197:               const srtContent = this.convertVttToSrt(vttContent);
198:               fs.writeFileSync(cachedPath, srtContent);
199:               if (this.isValidFile(cachedPath)) return cachedPath;
200:             } else if (file.endsWith('.srt')) {
201:               if (fullPath !== cachedPath) {
202:                 fs.copyFileSync(fullPath, cachedPath);
203:               }
204:               if (this.isValidFile(cachedPath)) return cachedPath;
205:             }
206:           }
207:         }
208:       } catch {}
209:     }
210: 
211:     // Step 5: Local audio transcription via whisper-cli
212:     const homeDir = process.env.HOME || '';
213:     const modelPath = path.join(homeDir, '.cache', 'whisper', 'ggml-base.en.bin');
214: 
215:     if (fs.existsSync(modelPath)) {
216:       console.log('No online subtitles found. Running fast audio transcription via whisper-cli...');
217:       const wavPath = path.join(this.tmpDir, `${hash}.wav`);
218:       const outPrefix = path.join(this.tmpDir, hash);
219:       const generatedSrt = `${outPrefix}.srt`;
220: 
221:       try {
222:         await $`ffmpeg -y -i ${filePath} -ar 16000 -ac 1 -c:a pcm_s16le ${wavPath}`.quiet();
223:         await $`whisper-cli -m ${modelPath} -f ${wavPath} -osrt -of ${outPrefix}`.quiet();
224:         if (this.isValidFile(generatedSrt)) {
225:           if (generatedSrt !== cachedPath) {
226:             fs.copyFileSync(generatedSrt, cachedPath);
227:           }
228:           if (this.isValidFile(cachedPath)) {
229:             return cachedPath;
230:           }
231:         }
232:       } catch {
233:         // Handle any errors gracefully
234:       } finally {
235:         if (fs.existsSync(wavPath)) {
236:           try {
237:             fs.unlinkSync(wavPath);
238:           } catch {}
239:         }
240:       }
241:     }
242: 
243:     return this.isValidFile(cachedPath) ? cachedPath : null;
244:   }
245: }
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T17:21:57-06:00
Completed At: 2026-08-03T17:21:58-06:00

				The command exited with code 2.
				Output:
				error: Script not found "check"
src/metadata-fetcher.ts(24,19): error TS2532: Object is possibly 'undefined'.
src/metadata-fetcher.ts(25,26): error TS2345: Argument of type 'string | undefined' is not assignable to parameter of type 'string'.
  Type 'undefined' is not assignable to type 'string'.
src/metadata-fetcher.ts(26,27): error TS2345: Argument of type 'string | undefined' is not assignable to parameter of type 'string'.
  Type 'undefined' is not assignable to type 'string'.
src/metadata-fetcher.ts(45,12): error TS18046: 'searchData' is of type 'unknown'.
src/metadata-fetcher.ts(45,34): error TS18046: 'searchData' is of type 'unknown'.
src/metadata-fetcher.ts(46,22): error TS18046: 'searchData' is of type 'unknown'.
src/metadata-fetcher.ts(52,30): error TS2339: Property 'credits' does not exist on type '{}'.
src/metadata-fetcher.ts(55,18): error TS2339: Property 'credits' does not exist on type '{}'.
src/metadata-fetcher.ts(55,55): error TS2339: Property 'credits' does not exist on type '{}'.
src/metadata-fetcher.ts(56,18): error TS2339: Property 'credits' does not exist on type '{}'.
src/metadata-fetcher.ts(56,62): error TS2339: Property 'credits' does not exist on type '{}'.
src/metadata-fetcher.ts(58,29): error TS2339: Property 'overview' does not exist on type '{}'.
src/metadata-fetcher.ts(61,81): error TS2339: Property 'name' does not exist on type '{}'.
src/metadata-fetcher.ts(75,22): error TS2339: Property 'name' does not exist on type '{}'.
src/metadata-fetcher.ts(91,23): error TS18046: 'searchData' is of type 'unknown'.
src/metadata-fetcher.ts(101,21): error TS18046: 'contentData' is of type 'unknown'.
src/metadata-fetcher.ts(129,24): error TS18046: 'data' is of type 'unknown'.

Created At: 2026-08-03T17:22:01-06:00
Completed At: 2026-08-03T17:22:01-06:00

				The command exited with code 1.
				Output:
				bun test v1.3.14 (0d9b296a)
No tests found!

Tests need ".test", "_test_", ".spec" or "_spec_" in the filename (ex: "MyApp.test.ts")

Learn more about bun test: https://bun.com/docs/cli/test

Created At: 2026-08-03T17:22:04-06:00
Completed At: 2026-08-03T17:22:06-06:00

				The command exited with code 2.
				Output:
				src/subs-extractor.ts(2,8): error TS1192: Module '"fs"' has no default export.
src/subs-extractor.ts(3,8): error TS1259: Module '"path"' can only be default-imported using the 'esModuleInterop' flag
src/subs-extractor.ts(4,8): error TS1192: Module '"crypto"' has no default export.

Created At: 2026-08-03T17:22:09-06:00
Completed At: 2026-08-03T17:22:09-06:00

				The command exited with code 0.
				Output:
				import { $ } from "bun";
import fs from "fs";
import path from "path";
import crypto from "crypto";

export class SubsExtractor {
  tmpDir;
  constructor(tmpDir = "./tmp") {
    this.tmpDir = tmpDir;
    if (!fs.existsSync(this.tmpDir)) {
      fs.mkdirSync(this.tmpDir, { recursive: true });
    }
  }
  hashFilePath(filePath) {
    return crypto.createHash("md5").update(filePath).digest("hex");
  }
  isValidFile(filePath) {
    try {
      return fs.existsSync(filePath) && fs.statSync(filePath).size > 0;
    } catch {
      return false;
    }
  }
  removeEmptyFile(filePath) {
    try {
      if (fs.existsSync(filePath) && fs.statSync(filePath).size === 0) {
        fs.unlinkSync(filePath);
      }
    } catch {}
  }
  convertVttToSrt(vttContent) {
    const content = vttContent.replace(/\r\n/g, `
`).replace(/\r/g, `
`);
    const rawBlocks = content.split(/\n\s*\n/);
    const srtBlocks = [];
    let counter = 1;
    for (const block of rawBlocks) {
      const lines = block.split(`
`).map((l) => l.trim()).filter((l) => l.length > 0);
      if (lines.length === 0)
        continue;
      const timeLineIndex = lines.findIndex((l) => l.includes("-->"));
      if (timeLineIndex === -1)
        continue;
      const timeLine = lines[timeLineIndex];
      if (!timeLine)
        continue;
      const match = timeLine.match(/((?:\d{1,2}:)?\d{1,2}:\d{2}[\.,]\d{1,3})\s*-->\s*((?:\d{1,2}:)?\d{1,2}:\d{2}[\.,]\d{1,3})/);
      if (!match || !match[1] || !match[2])
        continue;
      const formatPart = (t) => {
        const parts = t.replace(".", ",").split(":");
        if (parts.length === 2) {
          parts.unshift("00");
        }
        const h = (parts[0] || "00").padStart(2, "0");
        const m = (parts[1] || "00").padStart(2, "0");
        const sMs = parts[2] || "00,000";
        const sMsParts = sMs.split(",");
        const sec = (sMsParts[0] || "00").padStart(2, "0");
     
<truncated 4003 bytes>
} ${filePath}`.quiet();
        if (this.isValidFile(cachedPath))
          return cachedPath;
        const files = fs.readdirSync(this.tmpDir).filter((f) => f.startsWith(hash));
        for (const file of files) {
          const fullPath = path.join(this.tmpDir, file);
          if (this.isValidFile(fullPath)) {
            if (file.endsWith(".vtt")) {
              const vttContent = fs.readFileSync(fullPath, "utf-8");
              const srtContent = this.convertVttToSrt(vttContent);
              fs.writeFileSync(cachedPath, srtContent);
              if (this.isValidFile(cachedPath))
                return cachedPath;
            } else if (file.endsWith(".srt")) {
              if (fullPath !== cachedPath) {
                fs.copyFileSync(fullPath, cachedPath);
              }
              if (this.isValidFile(cachedPath))
                return cachedPath;
            }
          }
        }
      } catch {}
    }
    const homeDir = process.env.HOME || "";
    const modelPath = path.join(homeDir, ".cache", "whisper", "ggml-base.en.bin");
    if (fs.existsSync(modelPath)) {
      console.log("No online subtitles found. Running fast audio transcription via whisper-cli...");
      const wavPath = path.join(this.tmpDir, `${hash}.wav`);
      const outPrefix = path.join(this.tmpDir, hash);
      const generatedSrt = `${outPrefix}.srt`;
      try {
        await $`ffmpeg -y -i ${filePath} -ar 16000 -ac 1 -c:a pcm_s16le ${wavPath}`.quiet();
        await $`whisper-cli -m ${modelPath} -f ${wavPath} -osrt -of ${outPrefix}`.quiet();
        if (this.isValidFile(generatedSrt)) {
          if (generatedSrt !== cachedPath) {
            fs.copyFileSync(generatedSrt, cachedPath);
          }
          if (this.isValidFile(cachedPath)) {
            return cachedPath;
          }
        }
      } catch {} finally {
        if (fs.existsSync(wavPath)) {
          try {
            fs.unlinkSync(wavPath);
          } catch {}
        }
      }
    }
    return this.isValidFile(cachedPath) ? cachedPath : null;
  }
}

Created At: 2026-08-03T17:22:12-06:00
Completed At: 2026-08-03T17:22:12-06:00
Message sent to "4f839f10-5080-45e1-9e2f-d9c01908298c".

I have updated [`subs-extractor.ts`](file:///Users/matt/projects/video-context-agent/src/subs-extractor.ts) to add **Stage 5: Local audio transcription via `whisper-cli`**.

### Summary of Changes
1. **Model Check**: Checks if `~/.cache/whisper/ggml-base.en.bin` exists (expanding `~` via `process.env.HOME || ''`).
2. **Log Message**: Logs `'No online subtitles found. Running fast audio transcription via whisper-cli...'` when running the stage.
3. **Audio Extraction**: Uses `ffmpeg` to sample 16kHz mono audio (`pcm_s16le`) saved to `${this.tmpDir}/${hash}.wav`.
4. **Whisper Transcription**: Executes `whisper-cli -m ${modelPath} -f ${wavPath} -osrt -of ${outPrefix}`.
5. **Output & Cleanup**: If `${outPrefix}.srt` is generated, copies it to `cachedPath` and returns `cachedPath`. Temporary `.wav` files are cleaned up in a `finally` block and errors are caught gracefully.

---
