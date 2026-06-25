import pty from 'node-pty';

const ptyProcess = pty.spawn('/bin/zsh', ['-c', 'export PS1="Ready for input> " && bash --norc --noprofile -i'], {
  name: 'xterm-color',
  cols: 80,
  rows: 30,
  cwd: process.cwd(),
  env: process.env
});

ptyProcess.onData((data) => {
  console.log('PTY DATA:', JSON.stringify(data));
  if (data.includes('Ready for input>')) {
    console.log('Got prompt! Exiting...');
    process.exit(0);
  }
});
