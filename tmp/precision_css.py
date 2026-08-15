import re

with open('src/styles.css', 'r') as f:
    content = f.read()

# Replace the old generic thread-history-item selectors with the new semantic ones
old_thread_css = """/* Generic styling for thread items */
.thread-history-item > div:first-child,
.thread-history-item-alt > div:first-child,
.thread-placeholder-item > div:first-child,
.thread-placeholder-item-active > div:first-child {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.thread-history-item > div:first-child > span:first-child,
.thread-history-item-alt > div:first-child > span:first-child,
.thread-placeholder-item > div:first-child > span:first-child,
.thread-placeholder-item-active > div:first-child > span:first-child {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-main);
}
.thread-history-item > div:first-child > span:last-child,
.thread-history-item-alt > div:first-child > span:last-child,
.thread-placeholder-item > div:first-child > span:last-child,
.thread-placeholder-item-active > div:first-child > span:last-child {
  font-size: 0.7rem;
  opacity: 0.7;
  flex-shrink: 0;
}
.thread-history-item > div:nth-child(2),
.thread-history-item-alt > div:nth-child(2),
.thread-placeholder-item > div:nth-child(2),
.thread-placeholder-item-active > div:nth-child(2) {
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.8;
}
.thread-history-item > div:nth-child(3),
.thread-history-item-alt > div:nth-child(3),
.thread-placeholder-item > div:nth-child(3),
.thread-placeholder-item-active > div:nth-child(3) {
  font-size: 0.75rem;
  color: var(--primary);
  margin-top: 2px;
}"""

new_thread_css = """/* Semantic styling for thread items */
.thread-history-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.thread-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  gap: 2px;
  flex: 1;
}
.thread-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.thread-id {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-main);
}
.thread-date {
  font-size: 0.7rem;
  opacity: 0.7;
  flex-shrink: 0;
}
.thread-title {
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.8;
}
.thread-snippet {
  font-size: 0.75rem;
  color: var(--primary);
  margin-top: 2px;
}
.delete-thread-btn {
  opacity: 0;
  transition: opacity 0.2s;
  padding: 4px;
}
.thread-history-item:hover .delete-thread-btn {
  opacity: 1;
}
.delete-thread-btn:hover {
  color: var(--text-main);
}"""

if old_thread_css in content:
    content = content.replace(old_thread_css, new_thread_css)
else:
    print("Failed to find old generic thread styling block")


# Also need to replace the active state for the thread wrapper:
old_active_thread_css = """.thread-history-item-active, .thread-placeholder-item-active {
  background: rgba(86, 69, 197, 0.1);
  color: var(--primary);
}
.thread-history-item-active *, .thread-placeholder-item-active * {
  color: inherit !important;
}"""

new_active_thread_css = """.thread-history-item.active {
  background: rgba(86, 69, 197, 0.1);
  color: var(--primary);
}
.thread-history-item.active * {
  color: inherit !important;
}"""
content = content.replace(old_active_thread_css, new_active_thread_css)

# And add the chat layout css to the end of the file
chat_css = """

/* Chat Message Styling */
.markdown-preview-pane {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px 24px;
}

.chat-message {
  display: flex;
  width: 100%;
}

.chat-message.user {
  justify-content: flex-end;
}

.chat-message.agent {
  justify-content: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 8px;
  position: relative;
}

.chat-message.user .message-content {
  background-color: var(--primary);
  color: #fff;
  border-bottom-right-radius: 2px;
}

.chat-message.agent .message-content {
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-bottom-left-radius: 2px;
}

.chat-message.agent.historical .message-content {
  background-color: transparent;
  border: 1px dashed var(--border-color);
  opacity: 0.8;
}

.text-content, .message-content.prose {
  /* Line width constraint */
  max-width: 65ch;
  line-height: 1.5;
  word-wrap: break-word;
}

.chat-message.user .text-content {
  white-space: pre-wrap;
}

.copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 0.75rem;
  background: rgba(0,0,0,0.2);
  padding: 4px 8px;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  color: inherit;
}
.message-content:hover .copy-btn {
  opacity: 1;
}
.copy-btn:hover {
  background: rgba(0,0,0,0.4);
}

.historical-summary {
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  font-weight: 600;
  user-select: none;
}
.historical-details {
  margin-top: 12px;
  font-size: 0.85rem;
  white-space: pre-wrap;
  max-width: 65ch;
}
.toggle-icon {
  font-size: 0.7rem;
  transition: transform 0.2s;
}
details[open] .toggle-icon {
  transform: rotate(90deg);
}

.tool-call-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}
"""
content += chat_css

with open('src/styles.css', 'w') as f:
    f.write(content)
print("Updated src/styles.css")
