---
title: "I'm using MyNetDiary. I stupidly fell for the \"Get 50% off, "
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "4de50f8b-1af5-5862-9864-fa870fcfe591"
url: ""
---

# I'm using MyNetDiary. I stupidly fell for the \"Get 50% off, 

> [!NOTE]
> Archived Gemini Thread: [I'm using MyNetDiary. I stupidly fell for the \"Get 50% off, ]() | Date: 2026-08-13

## User

I'm using MyNetDiary.
I stupidly fell for the "Get 50% off, but only right now!" trick instead of actually vetting it properly.
I don't know if I can remove the calorie limit

---

## Gemini

Don’t beat yourself up over the "limited time offer" trap. Every app uses those aggressive countdown timers because they work, especially when you are in a motivated mindset and trying to take action. The good news is that MyNetDiary is actually a highly-rated, incredibly solid tracker with great database accuracy—so if you were going to accidentally buy a premium subscription to something, you at least got a good one.


Since you have the premium features now anyway, you can absolutely override the app's restrictions and make it work for your "data-only" approach. While you can't entirely remove the calorie display from the UI, you can easily trick the app so it stops nagging you or turning red.


Here are the two best ways to do it right now:


Option A: Crank the Limit Way Up (Recommended)
The cleanest way to ignore the limit is to set it so high that you never hit it. This stops the app from screaming "budget exceeded" and lets you just focus on logging.



* Go to the Me tab at the bottom.

* Tap My Weight Goal & Plan (or just My Plan).

* Scroll down to the Custom Calorie section.

* Manually override the number and set your daily target to something massive and arbitrary—like 5,000 calories.

* Tap Save.


Now you have a frictionless canvas. You can log normally, and the app will just stay green while you quietly collect your baseline data.


Option B: Set it to "Weight Maintenance"
If you prefer a target that represents reality but doesn't force a deficit:



* Go to My Weight Goal & Plan.

* Change your target goal from "Lose Weight" to "Maintain Weight".

* This will instantly bump your daily budget up to your actual baseline maintenance level, removing the artificial restriction while you get used to the habit of logging.


Don't worry about the interface perfection right now. Just pick one of those tweaks to get the red bars off your screen, log whatever you ate tonight, and call it a win for taking control of the strategy.

---

## User

wtf is this?

Tried to install this, and I get this:
```
pip install token-count
token-count error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install
    xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a Python library that isn't in Homebrew,
    use a virtual environment:
    
    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install xyz
    
    If you wish to install a Python application that isn't in Homebrew,
    it may be easiest to use 'pipx install xyz', which will manage a
    virtual environment for you. You can install pipx with
    
    brew install pipx
    
    You may restore the old behavior of pip by passing
    the '--break-system-packages' flag to pip, or by adding
    'break-system-packages = true' to your pip.conf file. The latter
    will permanently disable this error.
    
    If you disable this error, we STRONGLY recommend that you additionally
    pass the '--user' flag to pip, or set 'user = true' in your pip.conf
    file. Failure to do this can result in a broken Homebrew installation.
    
    Read more about this behavior here: <https://peps.python.org/pep-0668/>

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

What's the simplest way around this?
I hate python, I run into so many problems trying to do basic shit

---

## Gemini

I feel that frustration. Python's environment management can feel like a maze when you just want a simple tool to work.


The error you're seeing is a safety feature (introduced in PEP 668) designed to prevent pip from accidentally breaking your operating system's core files. Since you're on a Mac (implied by the brew mentions), macOS and Homebrew are now very protective of their "global" Python space.


The simplest way around this depends on how you plan to use this tool.



Option 1: The "I just want the CLI tool" way (Easiest)
If you just want to use token-count in your terminal like wc or ls, use pipx. It installs the tool in its own isolated bubble so it doesn't mess with your system, but still lets you run it from anywhere.



* Install pipx:
brew install pipx
pipx ensurepath



* Install the tool:
pipx install token-count




Now you can just run token-count --text "hello" whenever you want.



Option 2: The "Quick and Dirty" way (Not recommended)
If you truly don't care about "best practices" and just want it installed globally right now, you can force it.


Warning: This is what the error message meant by "breaking your installation." It can cause conflicts with Homebrew later.


pip install token-count --break-system-packages


Option 3: The "I'm writing a script" way
If you are trying to use token-count as a library inside a Python script you're writing, you should use a virtual environment. This keeps your project's junk separate from your computer's junk.


python3 -m venv .venv
source .venv/bin/activate
pip install token-count

(Note: You’ll need to run that source command every time you open a new terminal to work on that script.)



Summary of the repo
The token-count utility you're looking at is essentially a wrapper for OpenAI's tiktoken library. It's handy because it lets you check counts for specific models (like gpt-4 or gpt-3.5-turbo) directly from the command line without writing your own script.


Which of those approaches sounds less like a headache for what you're trying to do?

---

## User

any language setting here?

---

## Gemini

Yes, there is a language setting in this menu. It is the very first option at the top of the list.


Location and Translation

* Label: 显示语言 (Xiǎnshì yǔyán) — Display Language

* Description: 选择界面的显示语言 — Select the display language for the interface.


How to Change It
On the right side of that first row, you will see a dropdown menu that currently says 简体中文 (Simplified Chinese). Click that dropdown to see other available languages, such as English.



Other relevant settings in this view:



* Second Row: App Theme (Light/Dark mode)

* Third Row: Default Terminal (for the CLI)

* Ninth Row: Hide Dock Icon (macOS only)

---

## User

says <2pi, so this answer is wrong; right?
hmmm. nvm 2pi is above 6.28

---

## Gemini

You are exactly right to double-check that. Since $2\pi$ is approximately $6.28318...$, the value 6.28 is just slightly under that limit, making it a valid solution within the interval $[0, 2\pi)$.


Here is why that specific value appears for the equation $\sin(\frac{1}{2}x) = 0$:


The Logic
To find the solutions, you look for where the argument of the sine function equals multiples of $\pi$:



* First solution: Set $\frac{1}{2}x = 0$, which gives $x = 0$.

* Second solution: Set $\frac{1}{2}x = \pi$. Multiplying both sides by 2 gives $x = 2\pi$.


The Interval Constraint
The question likely specifies the domain as $0 \le x < 2\pi$ (or similar).



* If the interval is inclusive ($[0, 2\pi]$), then $2\pi$ (approx. 6.28) is a solution.

* If the interval is exclusive of the upper bound ($[0, 2\pi)$), then $x = 2\pi$ would technically be excluded.


However, in many graphing calculator exercises, $6.28$ is used as the rounded decimal equivalent for the boundary. Since $6.28 < 6.28318$, it technically sits right on the edge of that "less than $2\pi$" requirement.


Because the period of $\sin(\frac{1}{2}x)$ is $4\pi$, the graph stretches out, and the only "zeros" you will hit before reaching the $2\pi$ mark are at the very start ($0$) and the very end ($2\pi$).

---

## User

gpt5.4 thinking thinks there's just one, I'm inclined to believe IT.
but I'm going to check with sympy.
give me the equation in solve(...) Pythonic SymPy Syntax

---

## Gemini

To solve the equation $\sin(\frac{1}{2}x) = 0$ within the interval $[0, 2\pi)$ using SymPy, you can use the following syntax:


from sympy import symbols, sin, Eq, solveset, Interval, pi

x = symbols('x')
equation = Eq(sin(x/2), 0)

# Solves within the interval [0, 2*pi)
solutions = solveset(equation, x, domain=Interval(0, 2*pi, False, True))

print(solutions)

What this code does:

* Eq(sin(x/2), 0): Sets up the equation $\sin(\frac{1}{2}x) = 0$.

* Interval(0, 2*pi, False, True): This defines the range $[0, 2\pi)$. The False means the left side (0) is included, and the True means the right side ($2\pi$) is excluded.


The Mathematical Result
If you run this, SymPy will return {0}.


This confirms your suspicion: if the domain is strictly $x < 2\pi$, then $x = 2\pi$ is excluded. Because $2\pi \approx 6.28318...$, the value 6.28 shown in your practice software is only "correct" because it is a rounded decimal that happens to fall just below the $6.28318$ cutoff. In a strict calculus or trig course, $0$ would be the only solution in that open interval.

---

## User

no, no. I meant like this:
solve(2*cos(z) - sqrt(3), z)

that's sufficient, I'm pasting it into sympy shell. Don't write a script

---

## Gemini

solve(sin(x/2), x)

If you want to restrict it specifically to the interval $0 \le x < 2\pi$ within the shell (to see if $2\pi$ gets kicked out), you can use:


solveset(sin(x/2), x, Interval(0, 2*pi, False, True))

---

## User

Hmm. ok well I was left to think: ok, so 6.28 is not a solution, so it's out.
But then I remembered: it says to solve with a graphing calculator, and the way you use a graphing calculator to solve, which I think is dumb, is you just sort of get an approximation. So they used a calculator and got the approx. 6.28 even though it's not actually a solution.
What do I do here?
Can I claim to have used a graphing calculator and still not get 6.28 and say: "yeah, well it's not in the solution anyway, so it's your problem"
aka is it defensible?

---

## Gemini

It is absolutely defensible from a mathematical standpoint, but you’re running into the classic conflict between pure math and curriculum-specific software.


Here is the breakdown of why you are technically right and how to handle it:


1. The Mathematical Defense
In a rigorous setting, your logic is bulletproof.



* The boundary is $x < 2\pi$.

* The exact solution is $x = 2\pi$.

* Since $2\pi \notin [0, 2\pi)$, the solution set is just ${0}$.


If you were challenged, you could simply state: "The analytical solution is $2\pi$, which is approximately $6.28318$. Since $6.28318 > 6.28$, it falls outside the specified domain."


2. The "Calculator Logic" (Why they included it)
Graphing calculators (like the TI-84 shown in your practice module) work by testing pixels and using numerical algorithms.



* Most students will set their Xmax to $6.28$ (as a shorthand for $2\pi$).

* If the calculator finds a zero at $6.28$, and the student's window ends at $6.28$, they just write it down.

* The software is likely "forgiving" and treats $6.28$ as a rounded synonym for the boundary, rather than checking the strict inequality.


3. What should you do?
If this is for a marks-based system (like the Lauzon Pre-Calculus 12 course you're working through), you have two paths:



* The Pragmatic Path: If the software marks you wrong for excluding it, just include it. In "Calculator Mode" questions, authors often treat "round to the nearest hundredth" as an invitation to ignore the strictness of the boundary.

* The Principled Path: List only $0$. If the system flags it, you have a legitimate case for an appeal or a correction. You are using a higher level of precision (and a better tool like SymPy) than the question expects.


Verdict: It is "dumb," as you put it, because it teaches you to trust a rounded approximation over the actual constraints of the set. You are mathematically superior here—don't let the calculator's limitations gaslight you!


Does the software actually flag you as "Wrong" if you only enter 0?

---

