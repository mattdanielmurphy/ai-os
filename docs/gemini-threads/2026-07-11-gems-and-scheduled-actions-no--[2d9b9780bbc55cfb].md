---
title: "Gems and Scheduled Actions... no threads? What?"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "2d52c775-c26f-5062-a7f6-1c062fcc9b7f"
url: ""
---

# Gems and Scheduled Actions... no threads? What?

> [!NOTE]
> Archived Gemini Thread: [Gems and Scheduled Actions... no threads? What?]() | Date: 2026-08-13

## User

Gems and Scheduled Actions... no threads? What?

---

## Gemini

It looks like you've run into a classic quirk of how Google categories things behind the scenes.


When you export Gemini data via Google Takeout, that specific checkbox only handles your custom Gems (their names and instructions) and any Scheduled Actions you've set up.


Your actual conversation history—the chat threads themselves—isn't stored under the "Gemini" product label. Instead, Google lumps all your prompt history and chat threads into My Activity.


To grab your actual threads, close that popup and look for My Activity further down the page. When you select it, click on "All activity data included" to filter it down specifically to Gemini if you don't want a massive dump of your entire Google search and app history.

---

## User

shit. I did exactly what you said, and I got a folder of all the audio recordings for when I talk to gemini in voice mode and all the media that's ever been shared/produced in conversations. Which IS cool, but it's obviously NOT the text of all the threads I want

---

## Gemini

Ah, the classic Google Takeout misdirection.


Since you checked My Activity, Google gave you the raw interaction attachments (the audio files of your voice prompts and the images/media exchanged) rather than the actual text transcripts of the conversations.


To get the actual text history of your threads, you have to look for a completely different section in the archive.


Inside your downloaded export zip, look for a folder named Gemini (not the one inside My Activity). If you included the "Gemini" product during the export, the text of your threads is actually stored in there, usually as a file named chats.html or chats.json.


If you only exported "My Activity" this time, here is how to get the text:



* Go back to the main Google Takeout page.

* Scroll down to Gemini.

* Make sure the checkbox next to Gemini is selected. (Even though the subtitle only mentions Gems and Actions, this is actually where the chats data file is housed).

* Generate the export again.


Once it's ready, open the zip, go to the Gemini folder, and you'll find the complete text transcripts of your threads.

---

## User

I DID check Gemini because I thought that might be the case;
This is all it has
/Users/matt/Downloads/Takeout/Gemini/gemini_gems_data.html /Users/matt/Downloads/Takeout/Gemini/gemini_scheduled_actions_data.html

---

## Gemini

Well, that confirms Google is actively splitting things up in the worst way possible.


The text of your threads actually is inside My Activity, but you have to filter it completely differently to avoid getting buried in an avalanche of raw voice memos and media attachments.


When you select My Activity on the Google Takeout page, don't just leave it on the default settings. You need to change the export format:



* Look for the "Multiple formats" button right next to or under My Activity.

* Click it, and look for the dropdown or toggle for Activity history.

* Switch the format from HTML to JSON.


Why this matters:

* HTML Format (What you just got): Google breaks every single interaction into its own separate folder containing raw assets (like .mp3 voice recordings and images) alongside an HTML file that is incredibly messy to parse.

* JSON Format (What you want): Google compresses your entire text prompt and response history into a single, clean text file (usually named MyActivity.json). This file contains the exact text of your conversations without downloading any of the heavy media or audio attachments.


Uncheck everything else, run a new export with My Activity set strictly to JSON, and you'll get the clean text threads you're looking for.

---

## User

yeah you're right, there was a single html file hidden in that folder of media
MyActivity.html
Here's a snippet:
```

</style></head><body><div class="mdl-grid"><div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"><div class="mdl-grid"><div class="header-cell mdl-cell mdl-cell--12-col"><p class="mdl-typography--title">Gemini Apps<br></p></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">Prompted Gems and Scheduled Actions... no threads? What?<br><a href="https://takeout.google.com/?pli=1">https://takeout.google.com/?pli=1</a><br>Jul 11, 2026, 12:00:47 PM MDT<br><p>It looks like you&#39;ve run into a classic quirk of how Google categories things behind the scenes.</p>
<p>When you export <strong>Gemini</strong> data via Google Takeout, that specific checkbox only handles your custom <strong>Gems</strong> (their names and instructions) and any <strong>Scheduled Actions</strong> you&#39;ve set up.</p>
<p>Your actual conversation history—the chat threads themselves—isn&#39;t stored under the &quot;Gemini&quot; product label. Instead, Google lumps all your prompt history and chat threads into <strong>My Activity</strong>.</p>
<p>To grab your actual threads, close that popup and look for <strong>My Activity</strong> further down the page. When you select it, click on <strong>&quot;All activity data included&quot;</strong> to filter it down specifically to Gemini if you don&#39;t want a massive dump of your entire Google search and app history.</p>
<br></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1 mdl-typography--text-right"></div><div class="content-cell mdl-cell mdl-cell--12-col mdl-typography--caption"><b>Products:</b><br>&emsp;Gemini Apps<br><b>Why is this here?</b><br>&emsp;This activity was saved to your Google Account because the following settings were on:&nbsp;Gemini Apps Activity.&nbsp;You can control these settings &nbsp;<a href="https://myaccount.google.com/activitycontrols">here</a>.</div></div></div><div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"><div class="mdl-grid"><div class="header-cell mdl-cell mdl-cell--12-col"><p class="mdl-typography--title">Gemini Apps<br></p></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">Prompted Saetia and Orchid kind of sound like discordance axis or something<br>Jul 10, 2026, 11:55:29 PM MDT<br><p>You&#39;re picking up on a massive genetic overlap there.</p>
<p>Orchid, in particular, bridges the gap between screamo and grindcore/powerviolence so heavily that the subgenre term <strong>emoviolence</strong> was practically coined just to describe them.</p>
<p>Comparing them to <strong>Discordance Axis</strong> makes total sense when you break down what is happening sonically:</p>
<ul>
<li><strong>The Vocal Delivery:</strong> Both styles completely abandon standard aggressive hardcore growls or metal shouting for frantic, top-of-the-lungs shrieks that sound like genuine physical panic. Jon Chang’s piercing highs in Discordance Axis share the exact same desperate, unhinged energy as Jayson Green’s vocals in Orchid.</li>
<li><strong>The Dissonance:</strong> Neither style relies on traditional, chugging heavy metal riffs. Instead, they use harsh, discordant chord shapes, feedback, and screeching sonic textures that feel incredibly unstable.</li>
<li><strong>Velocity and Structure:</strong> Orchid completely rejected traditional song structures in favor of sub-two-minute blasts of pure speed. They heavily employed the same chaotic blast beats and sudden, whiplash-inducing tempo shifts that define technical grindcore landmarks like <em>The Inalienable Dreamless</em>.</li>
</ul>
<p>While Saetia kept a bit more of the melodic, indie-rock-influenced &quot;quiet-loud&quot; dynamic shifts, Orchid absolutely stole the blueprint from the grind and powerviolence scenes to weaponize their emotional delivery. It was all part of the same late-&#39;90s DIY underground ecosystem where these bands were sharing basement stages, gear, and split vinyl records.</p>
<br></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1 mdl-typography--text-right"></div><div class="content-cell mdl-cell mdl-cell--12-col mdl-typography--caption"><b>Products:</b><br>&emsp;Gemini Apps<br><b>Why is this here?</b><br>&emsp;This activity was saved to your Google Account because the following settings were on:&nbsp;Gemini Apps Activity.&nbsp;You can control these settings &nbsp;<a href="https://myaccount.google.com/activitycontrols">here</a>.</div></div></div><div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"><div class="mdl-grid"><div class="header-cell mdl-cell mdl-cell--12-col"><p class="mdl-typography--title">Gemini Apps<br></p></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">Prompted What are songs that are quintessentially screamo?<br>Jul 10, 2026, 11:50:25 PM MDT<br><p>When discussing &quot;screamo,&quot; the conversation instantly splits into two distinct eras: the chaotic, DIY underground of the late 1990s (often called <strong>skramz</strong> by purists to clear up confusion) and the massive, melodic post-hardcore commercial boom of the mid-2000s.</p>
<p>To get a complete picture of the genre, it helps to look at the tracks that defined both sides of that coin.</p>
<hr>
<h2>1. The DIY Foundations &amp; &quot;Skramz&quot; (Late &#39;90s – Early &#39;00s)</h2>
<p>This is the roots of the genre: raw, deeply emotional, structureless, and intensely abrasive. These bands fused the ethics of hardcore punk with overwhelming sonic desperation.</p>
<ul>
<li><strong>Saetia — &quot;An Open Letter to Horizon&quot; (1998)</strong>
<ul>
<li><em>Why it’s quintessential:</em> Saetia practically drew the blueprint for the genre. This track masterfully handles the classic &quot;quiet-loud-quiet&quot; dynamic, shifting from clean, spoken-word poetry to explosive, throat-shredding grief.</li>
</ul>
</li>
<li><strong>Orchid — &quot;I Am Nietzsche&quot; (1999)</strong>
<ul>
<li><em>Why it’s quintessential:</em> Orchid brought blinding speed, harsh micro-songs, and dense literary references to the table. This track is a sub-two-minute wall of pure, unhinged velocity and blast beats.</li>
</ul>
</li>
<li><strong>Pg.99 — &quot;In Love with an Apparition&quot; (2001)</strong>
<ul>
<li><em>Why it’s quintessential:</em> Document #8 is a landmark album. With a massive lineup that sometimes included three guitarists and two vocalists, this track delivers a chaotic, overwhelming wall of sound that feels like it’s structurally falling apart in the best way possible.</li>
</ul>
</li>
<li><strong>City of Caterpillar — &quot;And You&#39;re Wondering How a Top Happens&quot; (2002)</strong>
<ul>
<li><em>Why it’s quintessential:</em> They introduced cinematic, post-rock atmospheric builds to screamo. This track takes its time, building dark, shimmering tension before absolutely erupting.</li>
</ul>
</li>
</ul>
<hr>
<h2>2. The Post-Hardcore &amp; Mainstream Boom (Mid-2000s)</h2>
<p>By the mid-2000s, the term &quot;screamo&quot; was adopted by the mainstream to describe bands that paired heavy, aggressive screaming with slick, radio-ready pop-punk melodies.</p>
<ul>
<li><strong>Thursday — &quot;Understanding in a Car Crash&quot; (2001)</strong>
<ul>
<li><em>Why it’s quintessential:</em> The ultimate bridge track. It retained the genuine emotional weight and poetic lyricism of the underground DIY scene but packaged it with a driving, driving rhythmic hook that blew the doors open for the entire alternative scene.</li>
</ul>
</li>
<li><strong>The Used — &quot;A Box Full of Sharp Objects&quot; (2002)</strong>
<ul>
<li><em>Why it’s quintessential:</em> Bert McCracken’s manic vocal delivery—switching from frantic singing to literal vomiting sounds and manic laughs—captured the raw, hyper-energetic peak of commercial screamo.</li>
</ul>
</li>
<li><strong>Alexisonfire — &quot;This Could Be Anywhere in the World&quot; (2006)</strong>
<ul>
<li><em>Why it’s quintessential:</em> A masterclass in the &quot;counterpart&quot; vocal style. The track thrives on the stark, deliberate contrast between George Pettit’s aggressive, gritty roaring and Dallas Green’s soaring, melodic clean vocals.</li>
</ul>
</li>
<li><strong>Silverstein — &quot;Smile in Your Sleep&quot; (2005)</strong>
<ul>
<li><em>Why it’s quintessential:</em> A perfect representation of the tight, theatrical, and highly structured side of the 2000s scene, featuring iconic call-and-response vocal arrangements.</li>
</ul>
</li>
</ul>
<hr>
<h2>3. The Modern Wave &amp; Wave Revival (2010s – Present)</h2>
<p>In the 2010s, a new wave of bands stripped away the glossy pop production of the mid-2000s, combining the raw intensity of old-school skramz with a heavier focus on shoegaze textures and post-rock melody.</p>
<ul>
<li><strong>Touché Amoré — &quot;Flowers and You&quot; (2016)</strong>
<ul>
<li><em>Why it’s quintessential:</em> Jeremy Bolm’s vocals don&#39;t hide behind metaphor; the track is a devastatingly direct, poetic look at grief. It&#39;s fast, melodic, and intensely human.</li>
</ul>
</li>
<li><strong>Pianos Become the Teeth — &quot;I&#39;ll Be You, You&#39;ll Be Me&quot; (2011)</strong>
<ul>
<li><em>Why it’s quintessential:</em> From their heavier early era, this track showcases how modern screamo can feel like an exhausting, cathartic weight, driven by intricate, expressive drumming and desperate, strained vocals.</li>
</ul>
</li>
</ul>
<br></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1 mdl-typography--text-right"></div><div class="content-cell mdl-cell mdl-cell--12-col mdl-typography--caption"><b>Products:</b><br>&emsp;Gemini Apps<br><b>Why is this here?</b><br>&emsp;This activity was saved to your Google Account because the following settings were on:&nbsp;Gemini Apps Activity.&nbsp;You can control these settings &nbsp;<a href="https://myaccount.google.com/activitycontrols">here</a>.</div></div></div><div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"><div class="mdl-grid"><div class="header-cell mdl-cell mdl-cell--12-col"><p class="mdl-typography--title">Gemini Apps<br></p></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">Prompted Tell me how you can help me break down and understand a new concept.<br>Jul 10, 2026, 8:31:15 PM MDT<br><h3>Deconstructing New Concepts</h3>
<p>Here is how we can tackle a new or difficult topic together:</p>
<ul>
<li><strong>First Principles Analysis:</strong> We strip the concept down to its absolute foundational truths and build up from there. This prevents relying on shaky assumptions or rote memorization.</li>
<li><strong>Strategic Analogies:</strong> I will bridge the gap between the unknown and the familiar. For example, if we are mapping out signal flow in a complex modular patch or evaluating a new token optimization strategy for a local model, we can map the unfamiliar variables onto systems you already understand.</li>
<li><strong>Iterative Layering:</strong> We start with a high-level, simplified overview. Once the basic framework makes sense, we progressively layer on the technical details, mathematical proofs, or edge cases.</li>
<li><strong>Socratic Questioning:</strong> Instead of just handing you an answer, I can ask targeted questions to test your assumptions, expose gaps in your current understanding, and guide you to the correct conclusion yourself.</li>
<li><strong>Visual Aids &amp; Diagrams:</strong> If the topic involves physical systems, circuits, or geometric proofs, I can generate or retrieve relevant diagrams to make abstract ideas more concrete.</li>
</ul>
<p>What is a concept you are currently trying to wrap your head around?</p>
<br></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1 mdl-typography--text-right"></div><div class="content-cell mdl-cell mdl-cell--12-col mdl-typography--caption"><b>Products:</b><br>&emsp;Gemini Apps<br><b>Why is this here?</b><br>&emsp;This activity was saved to your Google Account because the following settings were on:&nbsp;Gemini Apps Activity.&nbsp;You can control these settings &nbsp;<a href="https://myaccount.google.com/activitycontrols">here</a>.</div></div></div><div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"><div class="mdl-grid"><div class="header-cell mdl-cell mdl-cell--12-col"><p class="mdl-typography--title">Gemini Apps<br></p></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">Prompted [2026-07-10 20:10 MDT-6] [context to this point is 755] should I try to distract them otherwise? Like if I make them look at me, is that kind of like a way to get them to &quot;snap out of it&quot; in terms of their fears, momentarily, but still<br>Jul 10, 2026, 8:10:33 PM MDT<br><p>Trying to force them to look at you or &quot;snap out of it&quot; rarely works with intense fear. When a dog is in a state of true panic, their brain is flooded with cortisol and adrenaline. They aren&#39;t misbehaving or ignoring you—they are in a survival-driven &quot;fight or flight&quot; mode, which makes learning or breaking focus on command almost impossible.</p>
<p>Instead of trying to break their focus, the goal is to gently redirect their energy or simply support them. Here is how to handle distraction and engagement during a storm:</p>
<hr>
<h3>The Problem with Forced Eye Contact</h3>
<p>If you try to hold their head or firmly command them to look at you, it can actually backfire:</p>
<ul>
<li><strong>Added Pressure:</strong> In canine language, direct, prolonged eye contact can be perceived as confrontational or demanding. If they are already terrified, adding pressure to perform a command can increase their anxiety.</li>
<li><strong>Ignoring the Threat:</strong> From their perspective, a massive, unseen threat is looming overhead. Forcing them to look away from it makes them feel more vulnerable, not safer.</li>
</ul>
<hr>
<h3>Better Ways to Redirect Their Mind</h3>
<p>If your dog is still willing to accept treats or interact, you can use <strong>low-pressure distraction</strong>. If they refuse, don&#39;t force it.</p>
<ul>
<li><strong>High-Value, Passive Tasks:</strong> Instead of asking for commands, give them something that requires zero mental pressure but triggers a calming mechanism. A lick mat covered in peanut butter or a frozen KONG toy is perfect. The repetitive physical act of licking actually releases soothing hormones in a dog&#39;s brain.</li>
<li><strong>Touch and Proximity:</strong> You do not need to worry about &quot;rewarding the fear&quot; by comforting them—that is an old myth. You cannot reward an emotion. If they want to press against you, let them. Firm, slow, long strokes along their back or side can help lower their heart rate.</li>
<li><strong>Gently Change the Environment:</strong> If they are pacing, casually walk to a different room (like a basement or a windowless bathroom) to see if they follow. A change of scenery can sometimes break a pacing loop without direct confrontation.</li>
</ul>
<blockquote>
<p><strong>The Litmus Test:</strong> Offer their absolute favorite, high-value treat (like a piece of real chicken or cheese). If they take it and chew it, their brain is still capable of a little distraction. If they turn their head away or drop the treat, they have crossed the threshold into pure panic. At that point, drop the distraction tactics and focus purely on providing a dark, quiet, safe &quot;den&quot; where they can ride it out.</p>
</blockquote>
<br></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1 mdl-typography--text-right"></div><div class="content-cell mdl-cell mdl-cell--12-col mdl-typography--caption"><b>Products:</b><br>&emsp;Gemini Apps<br><b>Why is this here?</b><br>&emsp;This activity was saved to your Google Account because the following settings were on:&nbsp;Gemini Apps Activity.&nbsp;You can control these settings &nbsp;<a href="https://myaccount.google.com/activitycontrols">here</a>.</div></div></div><div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"><div class="mdl-grid"><div class="header-cell mdl-cell mdl-cell--12-col"><p class="mdl-typography--title">Gemini Apps<br></p></div><div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">Prompted [2026-07-10 20:09 MDT-6] [context to this point is 0] does the sound of a waterfall near a dog help them relax from a thunderstorm they&#39;re terrified of?<br>Jul 10, 2026, 8:09:04 PM MDT<br><p>The short answer is yes, but it works as an acoustic shield rather than a magical cure.</p>
<p>While the gentle, continuous drone of a waterfall can help, its effectiveness depends entirely on how you use it. It relies on a principle called <strong>auditory masking</strong>.</p>
<hr>
<h3>How Auditory Masking Works</h3>
<p>The sound of rushing water functions as &quot;pink noise&quot; or &quot;white noise.&quot; It creates a dense wall of sound across a wide range of frequencies.</p>
<p>When a thunderstorm hits, the primary trigger for a terrified dog isn&#39;t just the overall noise level—it is the <strong>sudden, sharp contrast</strong> between a quiet room and a sudden crack of thunder.</p>
<ul>
<li><strong>Without background noise:</strong> The silence makes the sudden spike of thunder incredibly jarring.</li>
<li><strong>With waterfall noise:</strong> The baseline sound level in the room is raised. When thunder cracks, the relative contrast is significantly lower, preventing the sudden startle reflex.</li>
</ul>
<hr>
<h3>Three Rules to
```

How's th file even laid out?

---

## Gemini

That snippet makes the layout perfectly clear. Google is using a classic Material Design Lite (mdl-) grid layout to construct this file.


Instead of organizing your history by continuous chat threads, Google logs every single prompt/response interaction as its own self-contained block, stacking them in reverse chronological order (newest to oldest).


Here is the exact structural breakdown of how the file is laid out:


1. The Container (outer-cell)
Every interaction is wrapped in an individual block that acts as a container for that specific turn in a conversation:


<div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp">

2. The Header (header-cell)
Inside that container, the top banner defines which Google service handled the interaction (which will consistently say "Gemini Apps" here):


<div class="header-cell mdl-cell mdl-cell--12-col">
    <p class="mdl-typography--title">Gemini Apps<br></p>
</div>

3. The Content (content-cell)
This is the core section containing your data. It is hardcoded to use a simple text prefix pattern to show who said what:



* Your Prompt: It starts with the plaintext prefix Prompted  followed by the exact text or question you typed.

* The Timestamp: Right below your prompt, it drops a plaintext date and time string (e.g., Jul 11, 2026, 12:00:47 PM MDT).

* The AI Response: Immediately after the timestamp, the model's full response is rendered directly as standard HTML elements (<p>, <ul>, <li>, <strong>, etc.).


<div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">
    Prompted [Your Prompt Text Here]<br>
    [Timestamp Here]<br>
    [AI HTML Response Here]
    <br>
</div>

4. The Metadata Footer (mdl-typography--caption)
At the bottom of each block, Google attaches the tracking metadata explaining why this specific interaction was logged:


<div class="content-cell mdl-cell mdl-cell--12-col mdl-typography--caption">
    <b>Products:</b><br>&emsp;Gemini Apps<br>
    <b>Why is this here?</b><br>&emsp;This activity was saved to your Google Account because...
</div>


The Downside to this Layout
Because it logs everything as isolated interactions rather than grouping them by thread IDs, consecutive turns within the same conversation are just stacked sequentially. If you look closely at your timestamps, you can see how a continuous conversation is reconstructed just by reading the file linearly from bottom to top.

---

## User

it'd be much easier to get a json copy of that right?
especially considering I want to actually import all of this into my Hermes db

---

## Gemini

Absolutely. Processing a structured JSON file is infinitely cleaner than writing an entire scraper just to parse out specific Material Design Lite classes from a giant, poorly formatted HTML document.


Since you are looking to ingest your complete conversation history straight into your Hermes database, the JSON schema from My Activity drops all the layout noise and wraps each interaction into a clean array of objects.


What the JSON Structure Looks Like
Instead of navigating nested <div> containers, your data will look something like this in the MyActivity.json file:


[
  {
    "header": "Gemini Apps",
    "title": "Prompted Saetia and Orchid kind of sound like discordance axis or something",
    "titleUrl": "https://...",
    "time": "2026-07-10T23:55:29.000Z",
    "subtitles": [
      {
        "name": "You're picking up on a massive genetic overlap there.\n\nOrchid, in particular, bridges the gap..."
      }
    ],
    "products": ["Gemini Apps"]
  }
]

Scripting the Import
With this layout, writing a migration script to map the data to your Hermes DB schema becomes trivial. You can easily map the keys over:



* title maps to your user prompt.

* subtitles[0].name maps to the AI text response.

* time gives you an ISO-compatible timestamp right out of the box.


Since you already have the Google Takeout settings panel open to switch the format to JSON, hit OK, kick off the new export, and you'll have a clean data stream ready to parse.

---

