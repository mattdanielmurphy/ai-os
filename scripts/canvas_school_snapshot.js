// Dump Matt's Canvas state for refreshing docs/SCHOOL.md.
// Run from the built-in browser pane (javascript tool) on any canvas.ualberta.ca page,
// after Matt is signed in there. Read-only: only GET requests.
// Course ids (Fall 2026): CMPUT 174 = 34976, MUSIC 102 = 35877, PHIL 120 = 34494, XIME (MUSIC 193A) = 37090.
const j = async u => (await fetch(u, { headers: { Accept: 'application/json' } })).json();
const ids = [34976, 35877, 34494, 37090];
const today = new Date().toISOString().slice(0, 10);
const in3w = new Date(Date.now() + 21 * 864e5).toISOString().slice(0, 10);
const ago2w = new Date(Date.now() - 14 * 864e5).toISOString().slice(0, 10);
const ctx = ids.map(i => `context_codes[]=course_${i}`).join('&');
const out = { sections: {}, assignments: {}, modules: {} };
const courses = await j('/api/v1/courses?enrollment_state=active&include[]=sections&per_page=50');
for (const c of courses) out.sections[c.id] = (c.sections || []).map(s => s.name);
for (const id of ids) {
  const a = await j(`/api/v1/courses/${id}/assignments?include[]=submission&per_page=100&order_by=due_at`);
  out.assignments[id] = a.map(x => [x.name, x.due_at, x.submission && x.submission.workflow_state]);
  const m = await j(`/api/v1/courses/${id}/modules?per_page=50`);
  out.modules[id] = Array.isArray(m) ? m.map(x => x.name) : m;
}
const ann = await j(`/api/v1/announcements?${ctx}&start_date=${ago2w}&end_date=${today}&per_page=30`);
out.announcements = ann.map(a => [a.context_code, (a.posted_at || '').slice(0, 10), a.title,
  (a.message || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 300)]);
const ev = await j(`/api/v1/calendar_events?${ctx}&start_date=${today}&end_date=${in3w}&per_page=50`);
out.events = Array.isArray(ev) ? ev.map(e => [e.context_code, e.title, e.start_at, e.location_name]) : ev;
JSON.stringify(out);
