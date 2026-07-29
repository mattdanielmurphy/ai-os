# Leaf Subagent Constraints

## Execution Constraints
1. **Direct Action:** Execute requested file edits or research directly.
2. **Synchronous Subagents:** Subagent scripts execute synchronously.
3. **No Quoted Heredocs:** Do not use `cat << 'EOF'`. Use file tools directly.
4. **Strict File Reading:** Use `view_file` or `read_lines` tools for surgical inspections.
5. **Strict Output Truncation:** Cap command outputs to 1,000 tokens / 4,000 characters.
6. **No Transient Artifacts:** Keep checklists internal, do not generate transient planning files.
