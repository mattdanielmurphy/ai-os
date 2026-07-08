---
id: "queuing-of-messages"
status: "todo"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-08T01:22:03.696Z"
modified: "2026-07-08T01:45:50.661Z"
completedAt: null
labels: []
order: "a12V"
---
# Queuing of messages

- The main hurdle to overcome is that if you naively send a /clear along with the prompt, the `/clear` immediately fires, canceling the current task, and the prompt disappears effectively; it's not even run
  - So what we have to do is just hold our messages in our own queue (with a simple UI to show the queued messages and to cancel/edit them), and we'll have to figure out how to determine when the current task has completed.