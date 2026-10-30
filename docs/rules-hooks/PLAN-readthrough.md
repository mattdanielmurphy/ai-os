# Rules → hooks: everything being built, in ten minutes

<!-- readthrough project=ai-os -->

This is the middle version of the plan. The [short version](PLAN-summary.md) is a minute; the [full plan](PLAN.md) is about an hour. This one walks through every piece that will be built, in the order it gets built, what it means for you, and where you might want to say no.

## The idea in one breath

Right now, every agent in ai-os starts by reading about seventeen thousand words of rules, and agents in your other projects read an older copy of about four thousand words that has drifted out of date. Some rules, like the school rule and the project freeze, never reach those other projects at all. Long rule files don't work well: agents skim them, forget them, and apply the shouty ones too hard.

The plan flips this around. Agents will load a short core of about fifty-five lines. Everything else arrives at the exact moment it matters, through hooks: small scripts that run when an agent is about to do something, or when it finishes a reply. A hook can block something dangerous, slip in a reminder, or nudge the agent to finish a step it skipped.

The plan also deletes a lot. Deleting matters as much as building.

## Step zero: a text clean-up, no code

Before anything is built, the rules get cleaned. Dead rules are deleted. Rules that contradict each other get fixed, for example the different versions of the rm rule and the "ask before undo" rule. The contradicting memory files go too.

The biggest change here is a single "act or wait" rule. Today there are about six rules that say "wait for Matt" and four that say "just do it", and they collide. That collision is the main reason agents end replies by asking for your OK when they didn't need to. The new rule says plainly when an agent acts on its own and when it stops to ask.

The school rule, the freeze and act-or-wait also get copied into your global settings right away, so every project sees them, not only ai-os.

One more change: the rule "save every new rule in three places" goes. That rule is what caused the drift. From now on there's one place, and a build step copies it everywhere.

**For you:** fewer "can I go ahead?" questions, starting almost immediately.

**Possible veto:** pushes to main stop asking you at all, except the crossword, which stays protected.

## Step one: fill the gaps in the guards that already work

You already have four hooks that work well. The hang guard has stopped seventy-seven risky commands, and the screen-input guard has stopped forty-six unapproved actions. This step adds to them rather than rebuilding them.

First, a school guard. When an agent tries to edit a file in one of your school folders, you get asked first. This protects you from an agent quietly rewriting graded work.

Second, a few more patterns for the hang guard, so a Hammerspoon reload can't freeze a thread.

Third, the screen-input guard becomes strict: if Hammerspoon isn't answering, no input happens, ever. It also starts covering Chrome and computer-use actions, which slipped past it thirty-one times.

Fourth, secret files get one line in settings that blocks agents from reading them.

**For you:** you'll see a prompt when an agent touches school files.

**Possible veto:** that school prompt. If it gets annoying during a clean-up you asked for, there will be an "approved for this session" switch.

## Step two: the end-of-turn checker

This is the main new piece: one small program that runs every time an agent finishes a reply. It looks for a short list of mistakes.

There's an honest limit here. By the time this check runs, you've already seen the reply, and read-aloud may already be speaking it. A hook can't un-send it. So the checks split in two.

Checks that lead to an action happen right away: if the agent forgot to commit and push, wrote a broken Actions line, didn't report a voice task back, or claimed it saved a rule when it didn't, the turn continues and the agent fixes it.

Checks about writing, like a reply that ran too long or used shorthand, become a quiet reminder on the agent's next turn. That way you never read or hear the same reply twice.

This runs in "shadow" mode first: it logs what it would have done, without doing it, for three days. It only goes live if it's right at least nine times out of ten and gives fewer than one false nudge a day. It also has a kill switch.

**For you:** replies should get shorter, and Actions lines should stop having one-word buttons.

## Step three: saving rules and handing off work

When an agent tries to "remember" a rule by putting it in memory instead of a rule file, it gets a reminder to save it properly. When it writes a rule file, it's reminded to run the build. When a coordinator starts a new thread, it's told how fast your weekly usage is going, so it picks the right model.

The forwarder that sends your voice tasks to the coordinator also gets tested end to end, so delivery doesn't depend on an agent reading a file at the right moment.

## Step four: a pack just for coordinators

Coordinators get their own set of rules, loaded when they start and again after their memory is compacted. Today a compacted coordinator has to remember a file it read hours ago, and often doesn't. Workers and coordinators will now see different rules, each only what their job needs.

## The pause: is it working?

After step four, everything stops for a check. The same scripts that measured today's problems run again on the week since the checker went live. You get one simple before-and-after table: how often agents asked for OKs they didn't need, how long replies were, how many one-word buttons there were, and how many complaints you made.

The targets: OK-asks drop from about fifteen percent of replies to under five. Long worker replies drop from about half to under a fifth. One-word buttons go to zero. School edits without your OK go to zero.

**If those numbers are fixed, everything after this is optional.** That's deliberate. The plan admits it's a new system to maintain, which bends the project freeze a little, and this pause keeps it honest.

## Steps five and on, if you want them

Step five moves the remaining rules into one file each, and adds the cheap safety blocks, like no rm outside temp folders, no npm, no system temp folder and private GitHub repos only. Agents already follow these well, so these are insurance, not fixes.

Step five-b is a rules dashboard: one local page showing every rule, whether it's on, and how often it fires. You flip rules on or off from your Tweaks panel, not a new app.

Step six adds small rule packs that load by situation: one for building interfaces, one for Hammerspoon, one for school, and reminders that only fire when you say certain things, like mentioning a reminder or music.

Step seven shrinks the always-loaded rules to about sixty lines. A rule only leaves that core after its replacement hook has run for a week, one rule at a time.

Step eight gives the central coordinator four "judges": a model that checks, in the background, whether the coordinator did something like analysis it should have handed off. They run in shadow for a week, and stay only if you agree with nine of ten of their calls.

Step nine is the learning loop, which is your watcher idea made smaller. Every turn quietly records evidence. Once a week, one review proposes at most three rule changes, each tested, for your 👍. A heartbeat line makes sure it can't die silently, the way older systems did.

From then on, agents can also write "beta" rules that go live without your OK. They can only add reminders, never block anything or loosen another rule. There can be at most five, each is tagged, and each expires after three weeks unless you keep it.

Step ten is Tyler. Rules get sorted into circles: a shared core for you, Tyler and Kristy; Slub rules both of you agree on; your recommended rules, which arrive switched off on Tyler's Mac until he says yes to each; and your private rules, which never leave your Mac. His agent explains each offered rule in plain English.

## The decisions you might veto

There are six, all in the short version.

One: details files are only written when a reply runs long, and Readthroughs and reels only when you ask. This one is a real change from today.

Two: one act-or-wait rule replaces ten, and pushes stop asking you.

Three: the four interface design steps become one: three real examples, you pick one, then it's built.

Four: learning runs weekly, not every turn, with at most three changes for you.

Five: agent edits in school folders ask you first.

Six: beta rules can run without your OK, inside those strict limits.

Two more decisions only you can make: when the freeze ends, and the colour palette. Until the palette is picked, the colour rules can't really be enforced.

## The risks

The biggest is a bug in the end-of-turn checker breaking every session. It's guarded by failing open, a kill switch, shadow mode and replay tests.

Next, reminders turning into wallpaper that agents ignore, the way the long rule files did. They're kept short, shown once, and reviewed weekly.

Blocks can teach agents workarounds, so blocks stay few and the known workarounds are tested.

Writing reminders always arrive one turn late. That's a real limit; reply quality stays mostly judgment.

And the system itself could become a project. The pause after step four is there so it can stop as soon as it has done its job.
