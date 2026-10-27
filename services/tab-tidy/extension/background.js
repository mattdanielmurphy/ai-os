// Tab Tidy: collects tabs, asks the local helper (Haiku) what to close and how
// to group, then applies it. The helper archives every tab before we close it.
const HOST = "ca.mattmurphy.tabtidy";
// Groups we own are titled "<day> · <topic>". Any other group is Matt's and is never touched.
const OURS = /^(Today|Yesterday|Mon|Tue|Wed|Thu|Fri|Sat|Sun|Older) · /;

async function domainVisits(hosts) {
  const out = {};
  for (const host of hosts) {
    const items = await chrome.history.search({ text: host, startTime: 0, maxResults: 500 });
    let visits = 0;
    for (const it of items) {
      try { if (new URL(it.url).hostname === host) visits += it.visitCount || 0; } catch {}
    }
    out[host] = visits;
  }
  return out;
}

async function tidy(reason) {
  const groups = await chrome.tabGroups.query({});
  const groupTitle = Object.fromEntries(groups.map(g => [g.id, g.title || ""]));
  const tabs = (await chrome.tabs.query({})).map(t => ({
    id: t.id, windowId: t.windowId, index: t.index, url: t.url || "", title: t.title || "",
    lastAccessed: t.lastAccessed || Date.now(), pinned: t.pinned, audible: t.audible,
    discarded: t.discarded, active: t.active,
    group: t.groupId >= 0 ? groupTitle[t.groupId] : null,
    ourGroup: t.groupId >= 0 && OURS.test(groupTitle[t.groupId]),
  }));
  const hosts = [...new Set(tabs.map(t => { try { return new URL(t.url).hostname; } catch { return ""; } }).filter(Boolean))];
  const plan = await chrome.runtime.sendNativeMessage(HOST, {
    cmd: "tidy", reason, now: Date.now(), tabs, visits: await domainVisits(hosts),
  });
  if (!plan || plan.error) throw new Error(plan?.error || "no reply from helper");

  // Close only what the helper says it archived.
  if (!plan.dry_run && plan.close.length) {
    const open = new Set((await chrome.tabs.query({})).map(t => t.id));
    await chrome.tabs.remove(plan.close.filter(id => open.has(id)));
  }

  // Group: plan.groups is ordered oldest → newest per window; moving each to the end sorts them.
  const existing = Object.fromEntries((await chrome.tabGroups.query({}))
    .filter(g => OURS.test(g.title || "")).map(g => [`${g.windowId}|${g.title}`, g.id]));
  for (const g of plan.groups) {
    const live = (await Promise.all(g.tabIds.map(id => chrome.tabs.get(id).catch(() => null))))
      .filter(t => t && t.windowId === g.windowId && !t.pinned).map(t => t.id);
    if (!live.length) continue;
    const key = `${g.windowId}|${g.title}`;
    const id = existing[key] !== undefined
      ? await chrome.tabs.group({ groupId: existing[key], tabIds: live })
      : await chrome.tabs.group({ tabIds: live, createProperties: { windowId: g.windowId } });
    existing[key] = id;
    await chrome.tabGroups.update(id, { title: g.title, color: g.color, collapsed: g.collapsed });
    await chrome.tabGroups.move(id, { index: -1 });
  }

  const n = plan.dry_run ? 0 : plan.close.length;
  chrome.action.setBadgeText({ text: n ? String(n) : "" });
  chrome.action.setTitle({ title: `Tab Tidy: ${plan.summary}. Click to tidy now.` });
  await chrome.alarms.create("tidy", { periodInMinutes: plan.every_minutes || 120 });
}

function run(reason) {
  tidy(reason).catch(e => {
    chrome.action.setBadgeText({ text: "!" });
    chrome.action.setTitle({ title: `Tab Tidy failed: ${e.message}. Click to retry.` });
  });
}

chrome.runtime.onInstalled.addListener(() => run("installed"));
chrome.runtime.onStartup.addListener(() => chrome.alarms.create("tidy", { periodInMinutes: 120 }));
chrome.alarms.onAlarm.addListener(a => { if (a.name === "tidy") run("timer"); });
chrome.action.onClicked.addListener(() => run("clicked"));
