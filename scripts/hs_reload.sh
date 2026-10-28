#!/bin/sh
# Reload Hammerspoon without hanging: `hs -c 'hs.reload()'` blocks forever because
# the reload kills the IPC port it is talking through. Schedule the reload instead
# and cap the call at 10 s.
perl -e 'alarm 10; exec @ARGV' -- /usr/local/bin/hs -c 'hs.timer.doAfter(0.1, hs.reload); return "reloading"'
