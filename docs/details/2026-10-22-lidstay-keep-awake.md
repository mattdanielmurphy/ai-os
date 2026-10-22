# lidstay keep-awake check (2026-10-22)

## 11:47 Hammerspoon dependency + lid open

Asked (via coordinator): does a Hammerspoon reload/crash drop lidstay's keep-awake? Does it keep the Mac awake with the lid open too (Matt wants yes)?

### Not tied to Hammerspoon

lidstay is a root LaunchDaemon (`local.lidstay`, KeepAlive) running /usr/local/bin/lidstay every 5s and setting `pmset disablesleep`. Hammerspoon's `modules/lid_sleep.lua` only writes/moves the pause file `/Users/Shared/lidstay/pause_until`. A reload or crash changes nothing. No new process or global rule needed; added a line to lidstay AG_CONTEXT.md: never bootout local.lidstay or flip disablesleep from other tools.

---

### Lid open now stays awake

Before: with the lid open lidstay emulated idle sleep (idle past the Energy "sleep" timer, 30 min, and no assertions → `pmset sleepnow`). Now `IDLE_SLEEP=0` is the default, so it never idle-sleeps; display still sleeps on its 60 min timer. `IDLE_SLEEP=1 ./install.sh` restores the old behaviour. Kept: on battery below 20% normal sleep returns (battery safety). Tested with DRY_RUN fakes (idle 99999s on AC: no sleep with 0, sleepnow with 1).

---

### Needs install to go live

Install needs root (password); only `pmset -a disablesleep` is passwordless. Matt runs `cd ~/projects/lidstay && ./install.sh`. Undo: `IDLE_SLEEP=1 ./install.sh` or `git revert` the commit and reinstall.
