export const colors = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  italic: '\x1b[3m',
  underline: '\x1b[4m',
  
  // Foreground colors
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  
  // Bright/Light foreground colors
  gray: '\x1b[90m',
  lightRed: '\x1b[91m',
  lightGreen: '\x1b[92m',
  lightYellow: '\x1b[93m',
  lightBlue: '\x1b[94m',
  lightMagenta: '\x1b[95m',
  lightCyan: '\x1b[96m',
  lightWhite: '\x1b[97m',
  
  // Background colors
  bgBlack: '\x1b[40m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
  bgMagenta: '\x1b[45m',
  bgWhite: '\x1b[47m',
};

export function drawSection(title, content, colorCode = colors.cyan) {
  const cols = process.stdout.columns || 80;
  const headerText = `  ${title}  `;
  const borderChar = '━';
  const remaining = Math.max(0, cols - headerText.length - 4);
  const header = `${colors.bold}${colorCode}━━${headerText}${borderChar.repeat(remaining)}${colors.reset}`;
  const footer = `${colors.bold}${colorCode}${borderChar.repeat(cols)}${colors.reset}`;

  const indentedContent = content
    .split('\n')
    .map(line => `  ${line}`)
    .join('\n');

  return `${header}\n${indentedContent}\n${footer}`;
}

export class GatewayLogger {
  constructor(mode = 'debug') {
    this.mode = mode; // 'debug' or 'user'
    this.writer = null; // Custom function: (message, type) => {}
  }

  // Logs a debug statement. In 'user' mode, this is suppressed entirely.
  // In 'debug' mode, it is printed in a dim color to separate it from the actual prompt/response.
  debug(message, ...args) {
    if (this.mode === 'debug') {
      const msg = `${colors.gray}[DEBUG] ${message}${colors.reset}` + (args.length ? ' ' + args.join(' ') : '');
      if (this.writer) {
        this.writer(msg, 'debug');
      } else {
        console.log(msg);
      }
    }
  }

  // Logs a user mode progress indicator. In 'user' mode, this shows high-level progress.
  // In 'debug' mode, it prints as a highlighted info log.
  info(message, ...args) {
    let msg;
    if (this.mode === 'user') {
      msg = `${colors.bold}${colors.lightBlue}⚙️  ${message}${colors.reset}` + (args.length ? ' ' + args.join(' ') : '');
    } else {
      msg = `${colors.bold}${colors.lightCyan}[INFO] ${message}${colors.reset}` + (args.length ? ' ' + args.join(' ') : '');
    }
    if (this.writer) {
      this.writer(msg, 'info');
    } else {
      console.log(msg);
    }
  }

  warn(message, ...args) {
    const msg = `${colors.bold}${colors.yellow}⚠️  [WARN] ${message}${colors.reset}` + (args.length ? ' ' + args.join(' ') : '');
    if (this.writer) {
      this.writer(msg, 'warn');
    } else {
      console.log(msg);
    }
  }

  error(message, ...args) {
    const msg = `${colors.bold}${colors.red}❌ [ERROR] ${message}${colors.reset}` + (args.length ? ' ' + args.join(' ') : '');
    if (this.writer) {
      this.writer(msg, 'error');
    } else {
      console.error(msg);
    }
  }

  showQuery(query) {
    const formatted = '\n' + drawSection('USER INPUT', query, colors.lightMagenta) + '\n';
    if (this.writer) {
      this.writer(formatted, 'query');
    } else {
      console.log(formatted);
    }
  }

  showResponse(response, tierName = 'DIRECT_API') {
    const rendered = renderMarkdown(response);
    const formatted = '\n' + drawSection(`GATEWAY RESPONSE (${tierName})`, rendered, colors.lightGreen) + '\n';
    if (this.writer) {
      this.writer(formatted, 'response');
    } else {
      console.log(formatted);
    }
  }
}

export function renderMarkdown(text) {
  if (!text) return '';
  
  let lines = text.split('\n');
  let inCodeBlock = false;
  let codeBlockLines = [];
  let result = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Code block toggle
    if (line.startsWith('```')) {
      if (inCodeBlock) {
        inCodeBlock = false;
        const blockText = codeBlockLines.map(l => `${colors.cyan}│ ${l}${colors.reset}`).join('\n');
        result.push(`${colors.bold}${colors.gray}┌── CODE BLOCK ──────────────────────────${colors.reset}\n${blockText}\n${colors.bold}${colors.gray}└────────────────────────────────────────${colors.reset}`);
        codeBlockLines = [];
      } else {
        inCodeBlock = true;
      }
      continue;
    }
    
    if (inCodeBlock) {
      codeBlockLines.push(line);
      continue;
    }
    
    let renderedLine = line;
    
    // Headers
    if (renderedLine.startsWith('# ')) {
      renderedLine = `${colors.bold}${colors.lightBlue}${renderedLine}${colors.reset}`;
    } else if (renderedLine.startsWith('## ')) {
      renderedLine = `${colors.bold}${colors.lightCyan}${renderedLine}${colors.reset}`;
    } else if (renderedLine.startsWith('### ')) {
      renderedLine = `${colors.bold}${colors.blue}${renderedLine}${colors.reset}`;
    } else if (renderedLine.startsWith('#### ')) {
      renderedLine = `${colors.bold}${colors.cyan}${renderedLine}${colors.reset}`;
    }
    
    // Bold: **text** -> ANSI bold
    renderedLine = renderedLine.replace(/\*\*([^*]+)\*\*/g, `${colors.bold}$1${colors.reset}`);
    
    // Inline code: `code` -> ANSI cyan
    renderedLine = renderedLine.replace(/`([^`]+)`/g, `${colors.bold}${colors.cyan}$1${colors.reset}`);
    
    // Bullet lists: - item -> clean bullet character
    if (renderedLine.trim().startsWith('- ') || renderedLine.trim().startsWith('* ') || renderedLine.trim().startsWith('+ ')) {
      renderedLine = renderedLine.replace(/^\s*[-*+]\s/, `  ${colors.lightMagenta}•${colors.reset} `);
    } else if (renderedLine.trim().match(/^\d+\.\s/)) {
      renderedLine = renderedLine.replace(/^(\s*)(\d+)\.\s/, `$1${colors.lightMagenta}$2.${colors.reset} `);
    }
    
    result.push(renderedLine);
  }
  
  if (inCodeBlock && codeBlockLines.length > 0) {
    const blockText = codeBlockLines.map(l => `${colors.cyan}│ ${l}${colors.reset}`).join('\n');
    result.push(`${colors.bold}${colors.gray}┌── CODE BLOCK ──────────────────────────${colors.reset}\n${blockText}\n${colors.bold}${colors.gray}└────────────────────────────────────────${colors.reset}`);
  }
  
  return result.join('\n');
}
