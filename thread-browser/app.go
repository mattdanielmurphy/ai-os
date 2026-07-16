package main

import (
	"bufio"
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"sync"

	_ "modernc.org/sqlite"
)

// App struct
type App struct {
	ctx          context.Context
	homeDir      string
	dbPath       string
	brainDirs    []string
	cacheMutex   sync.Mutex
	cachedThs    map[string]*cachedThread
	cacheLoaded  bool
}

type cachedThread struct {
	ID         string          `json:"id"`
	Path       string          `json:"path"`
	Title      string          `json:"title"`
	MTime      int64           `json:"mtime"`
	ParentID   string          `json:"parentId"`
	Messages   []cachedMessage `json:"-"`
	Snippet    string          `json:"snippet"`
	Source     string          `json:"source"`
}

type cachedMessage struct {
	Role    string
	Content string
}

type ThreadResult struct {
	ID        string   `json:"id"`
	Title     string   `json:"title"`
	StartedAt float64  `json:"startedAt"`
	Source    string   `json:"source"`
	Score     int64    `json:"score"`
	Snippet   string   `json:"snippet"`
	Matches   []string `json:"matches"`
	FilePath  string   `json:"filePath"`
	WebURL    string   `json:"webUrl"`
}

type Message struct {
	Role      string  `json:"role"`
	Content   string  `json:"content"`
	ToolName  string  `json:"toolName"`
	ToolCalls string  `json:"toolCalls"`
	Timestamp float64 `json:"timestamp"`
}

// NewApp creates a new App application struct
func NewApp() *App {
	home, err := os.UserHomeDir()
	if err != nil {
		home = "/Users/matt"
	}
	dbPath := filepath.Join(home, ".hermes", "state.db")
	brainDirs := []string{
		filepath.Join(home, ".gemini", "antigravity-cli", "brain"),
		filepath.Join(home, ".gemini", "antigravity-ide", "brain"),
	}

	return &App{
		homeDir:   home,
		dbPath:    dbPath,
		brainDirs: brainDirs,
		cachedThs: make(map[string]*cachedThread),
	}
}

// startup is called when the app starts.
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	// Trigger cache load in background for fallback mode
	go a.loadFSThreadsCache()
}

// CheckDBExists helper
func (a *App) isDBAvailable() bool {
	_, err := os.Stat(a.dbPath)
	return err == nil
}

// loadFSThreadsCache scans the local directories and caches thread metadata for fallback search
func (a *App) loadFSThreadsCache() {
	a.cacheMutex.Lock()
	if a.cacheLoaded {
		a.cacheMutex.Unlock()
		return
	}
	a.cacheMutex.Unlock()

	tmpCache := make(map[string]*cachedThread)

	for _, brainDir := range a.brainDirs {
		entries, err := os.ReadDir(brainDir)
		if err != nil {
			continue
		}

		for _, entry := range entries {
			if !entry.IsDir() {
				continue
			}
			threadID := entry.Name()
			transcriptPath := filepath.Join(brainDir, threadID, ".system_generated", "logs", "transcript.jsonl")
			info, err := os.Stat(transcriptPath)
			if err != nil {
				continue
			}

			// Read and parse transcript
			tFile, err := os.Open(transcriptPath)
			if err != nil {
				continue
			}

			var msgs []cachedMessage
			parentID := ""
			title := threadID
			snippet := ""
			scanner := bufio.NewScanner(tFile)
			foundTitle := false

			// Buffer for scanning long lines safely
			buf := make([]byte, 0, 64*1024)
			scanner.Buffer(buf, 1024*1024)

			for scanner.Scan() {
				var lineObj map[string]interface{}
				if err := json.Unmarshal(scanner.Bytes(), &lineObj); err == nil {
					roleStr, _ := lineObj["role"].(string)
					typeStr, _ := lineObj["type"].(string)
					contentStr, _ := lineObj["content"].(string)

					// Normalize roles
					if roleStr == "" {
						if typeStr == "USER_INPUT" {
							roleStr = "user"
						} else if typeStr == "PLANNER_RESPONSE" || typeStr == "MODEL" {
							roleStr = "assistant"
						}
					}

					if contentStr != "" {
						msgs = append(msgs, cachedMessage{
							Role:    roleStr,
							Content: contentStr,
						})

						// Extract parent ID
						if parentID == "" {
							if pos := strings.Index(contentStr, "Continuing conversation from history (Thread ID:"); pos != -1 {
								after := contentStr[pos+len("Continuing conversation from history (Thread ID:"):]
								if endPos := strings.Index(after, ")"); endPos != -1 {
									pID := strings.TrimSpace(after[:endPos])
									parentID = pID
								}
							}
						}

						// Extract Title from thread name tags
						if !foundTitle && typeStr == "PLANNER_RESPONSE" {
							if startIdx := strings.Index(contentStr, "<THREAD_NAME>"); startIdx != -1 {
								if endIdx := strings.Index(contentStr[startIdx:], "</THREAD_NAME>"); endIdx != -1 {
									title = strings.TrimSpace(contentStr[startIdx+13 : startIdx+endIdx])
									foundTitle = true
								}
							}
						}

						// Fallback title / snippet from first user request
						if typeStr == "USER_INPUT" {
							rawPrompt := contentStr
							if startIdx := strings.Index(rawPrompt, "<USER_REQUEST>"); startIdx != -1 {
								if endIdx := strings.Index(rawPrompt, "</USER_REQUEST>"); endIdx != -1 {
									rawPrompt = strings.TrimSpace(rawPrompt[startIdx+14 : endIdx])
								}
							}
							if sysIdx := strings.Index(rawPrompt, "<SYSTEM_INSTRUCTIONS>"); sysIdx != -1 {
								rawPrompt = strings.TrimSpace(rawPrompt[:sysIdx])
							}
							
							cleanPrompt := strings.ReplaceAll(rawPrompt, "\n", " ")
							if !foundTitle {
								if len(cleanPrompt) > 40 {
									title = cleanPrompt[:40] + "..."
								} else {
									title = cleanPrompt
								}
							}
							if snippet == "" {
								if len(cleanPrompt) > 120 {
									snippet = cleanPrompt[:120] + "..."
								} else {
									snippet = cleanPrompt
								}
							}
						}
					}
				}
			}
			tFile.Close()

			source := "cli"
			if strings.Contains(brainDir, "antigravity-ide") {
				source = "desktop"
			}

			tmpCache[threadID] = &cachedThread{
				ID:       threadID,
				Path:     filepath.Join(brainDir, threadID),
				Title:    title,
				MTime:    info.ModTime().Unix(),
				ParentID: parentID,
				Messages: msgs,
				Snippet:  snippet,
				Source:   source,
			}
		}
	}

	a.cacheMutex.Lock()
	a.cachedThs = tmpCache
	a.cacheLoaded = true
	a.cacheMutex.Unlock()
}

// SearchThreads exposes thread search capability
func (a *App) SearchThreads(query string) ([]ThreadResult, error) {
	if a.isDBAvailable() {
		return a.searchDBThreads(query)
	}
	return a.searchFSThreads(query)
}

// searchDBThreads queries the state.db SQLite database
func (a *App) searchDBThreads(query string) ([]ThreadResult, error) {
	db, err := sql.Open("sqlite", a.dbPath)
	if err != nil {
		return nil, err
	}
	defer db.Close()

	var results []ThreadResult
	query = strings.TrimSpace(query)

	if query == "" {
		rows, err := db.Query(`
			SELECT id, source, COALESCE(title, '') as title, started_at, COALESCE(cwd, '') as cwd 
			FROM sessions 
			ORDER BY started_at DESC 
			LIMIT 5000`)
		if err != nil {
			return nil, err
		}
		defer rows.Close()

		for rows.Next() {
			var id, source, title, cwd string
			var startedAt float64
			if err := rows.Scan(&id, &source, &title, &startedAt, &cwd); err != nil {
				fmt.Printf("Scan error in query == '': %v\n", err)
				continue
			}
			filePath := a.findLocalThreadFolder(id)
			webURL := ""
			if source == "gemini-archive" {
				webURL = "https://gemini.google.com/app/" + id
			}
			results = append(results, ThreadResult{
				ID:        id,
				Title:     title,
				StartedAt: startedAt,
				Source:    source,
				FilePath:  filePath,
				WebURL:    webURL,
			})
		}
		return results, nil
	}

	// Decide if query consists of whole alphanumeric tokens
	// If query matches only words/tokens, we use standard fts.
	// We check if it is alphanumeric (or spaces). If so, we use messages_fts.
	// If it has wildcards (*, ?) or non-alphanumeric chars (punctuation), or is very short (e.g. <3 chars),
	// we use trigram FTS.
	useTrigram := false
	trimmed := strings.Trim(query, "*? ")
	if len(trimmed) < 3 {
		useTrigram = true
	} else {
		for _, r := range trimmed {
			if !((r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == ' ' || r == '_') {
				useTrigram = true
				break
			}
		}
	}

	var matchSQL string
	if useTrigram {
		matchSQL = `
		WITH matched_messages AS (
			SELECT m.session_id, m.role
			FROM messages_fts_trigram f
			JOIN messages m ON f.rowid = m.id
			WHERE f.content MATCH ?
		)`
	} else {
		// Escape query to search exactly as a token prefix or token match
		// FTS5 MATCH '"term"' finds exact tokens
		matchSQL = `
		WITH matched_messages AS (
			SELECT m.session_id, m.role
			FROM messages_fts f
			JOIN messages m ON f.rowid = m.id
			WHERE f.content MATCH ?
		)`
	}

	// Calculate score only for the matching sessions subset
	fullSQL := matchSQL + `
		SELECT 
			s.id, 
			s.source,
			COALESCE(s.title, '') as title, 
			s.started_at,
			COALESCE(s.cwd, '') as cwd,
			(
				CASE WHEN s.title LIKE ? THEN 100000000 ELSE 0 END +
				COALESCE((
					SELECT SUM(
						CASE 
							WHEN mm.role = 'user' THEN 50000000 
							WHEN mm.role = 'assistant' THEN 10000000 
							ELSE 5000000 
						END
					)
					FROM matched_messages mm
					WHERE mm.session_id = s.id
				), 0)
			) as relevance_score
		FROM sessions s
		WHERE s.title LIKE ? OR s.id IN (SELECT session_id FROM matched_messages)
		ORDER BY relevance_score DESC, s.started_at DESC
		LIMIT 1000
	`

	stmt, err := db.Prepare(fullSQL)
	if err != nil {
		return nil, err
	}
	defer stmt.Close()

	likePattern := "%" + query + "%"
	// For standard FTS, wrap query in quotes to search exact phrase/tokens if it contains spaces
	searchParam := query
	if !useTrigram && strings.Contains(query, " ") {
		searchParam = `"` + strings.ReplaceAll(query, `"`, `""`) + `"`
	}

	rows, err := stmt.Query(searchParam, likePattern, likePattern)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var id, source, title, cwd string
		var startedAt float64
		var score int64
		if err := rows.Scan(&id, &source, &title, &startedAt, &cwd, &score); err != nil {
			fmt.Printf("Scan error in query != '': %v\n", err)
			continue
		}
		filePath := a.findLocalThreadFolder(id)
		webURL := ""
		if source == "gemini-archive" {
			webURL = "https://gemini.google.com/app/" + id
		}

		// Get matching messages snippet/highlights
		snippet, matches := a.getDBThreadSnippetAndMatches(db, id, query)

		results = append(results, ThreadResult{
			ID:        id,
			Title:     title,
			StartedAt: startedAt,
			Source:    source,
			Score:     score,
			Snippet:   snippet,
			Matches:   matches,
			FilePath:  filePath,
			WebURL:    webURL,
		})
	}

	return results, nil
}

// findLocalThreadFolder checks where the thread directory is located
func (a *App) findLocalThreadFolder(id string) string {
	for _, brainDir := range a.brainDirs {
		p := filepath.Join(brainDir, id)
		if _, err := os.Stat(p); err == nil {
			return p
		}
	}
	return ""
}

// getDBThreadSnippetAndMatches retrieves and highlights matches from the database
func (a *App) getDBThreadSnippetAndMatches(db *sql.DB, sessionID string, query string) (string, []string) {
	rows, err := db.Query(`
		SELECT COALESCE(content, '') as content 
		FROM messages 
		WHERE session_id = ? AND content LIKE ? 
		LIMIT 5`, sessionID, "%"+query+"%")
	if err != nil {
		return "", nil
	}
	defer rows.Close()

	var matches []string
	snippet := ""
	queryLower := strings.ToLower(query)

	for rows.Next() {
		var content string
		if err := rows.Scan(&content); err != nil {
			fmt.Printf("Scan error in snippet: %v\n", err)
			continue
		}
			cleanContent := strings.ReplaceAll(content, "<THREAD_NAME>", "")
			cleanContent = strings.ReplaceAll(cleanContent, "</THREAD_NAME>", "")
			cleanContent = strings.ReplaceAll(cleanContent, "<USER_REQUEST>", "")
			cleanContent = strings.ReplaceAll(cleanContent, "</USER_REQUEST>", "")

			if snippet == "" {
				snippet = extractSnippet(cleanContent, query)
			}

			for _, line := range strings.Split(cleanContent, "\n") {
				if strings.Contains(strings.ToLower(line), queryLower) {
					highlighted := highlightQueryText(strings.TrimSpace(line), query)
					if len(matches) < 5 {
						matches = append(matches, highlighted)
					}
				}
			}
	}

	if snippet == "" {
		snippet = "Matched in title"
	}
	return snippet, matches
}

// searchFSThreads searches the local filesystem threads using cache
func (a *App) searchFSThreads(query string) ([]ThreadResult, error) {
	a.cacheMutex.Lock()
	if !a.cacheLoaded {
		a.cacheMutex.Unlock()
		a.loadFSThreadsCache()
		a.cacheMutex.Lock()
	}
	defer a.cacheMutex.Unlock()

	var results []ThreadResult
	query = strings.TrimSpace(query)
	queryLower := strings.ToLower(query)

	if query == "" {
		var list []*cachedThread
		for _, th := range a.cachedThs {
			list = append(list, th)
		}
		sort.Slice(list, func(i, j int) bool {
			return list[i].MTime > list[j].MTime
		})
		
		limit := 5000
		if len(list) < limit {
			limit = len(list)
		}

		for i := 0; i < limit; i++ {
			th := list[i]
			results = append(results, ThreadResult{
				ID:        th.ID,
				Title:     th.Title,
				StartedAt: float64(th.MTime),
				Source:    th.Source,
				FilePath:  th.Path,
				Snippet:   th.Snippet,
			})
		}
		return results, nil
	}

	for _, th := range a.cachedThs {
		var score int64 = 0
		var snippet = ""
		var matches []string

		if strings.Contains(strings.ToLower(th.Title), queryLower) {
			score += 100000000
		}

		for _, msg := range th.Messages {
			if strings.Contains(strings.ToLower(msg.Content), queryLower) {
				if msg.Role == "user" {
					score += 50000000
				} else {
					score += 10000000
				}

				if snippet == "" {
					snippet = extractSnippet(msg.Content, query)
				}

				for _, line := range strings.Split(msg.Content, "\n") {
					if strings.Contains(strings.ToLower(line), queryLower) {
						highlighted := highlightQueryText(strings.TrimSpace(line), query)
						if len(matches) < 5 {
							matches = append(matches, highlighted)
						}
					}
				}
			}
		}

		if score > 0 {
			score += th.MTime
			results = append(results, ThreadResult{
				ID:        th.ID,
				Title:     th.Title,
				StartedAt: float64(th.MTime),
				Source:    th.Source,
				Score:     score,
				Snippet:   snippet,
				Matches:   matches,
				FilePath:  th.Path,
			})
		}
	}

	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	limit := 1000
	if len(results) < limit {
		limit = len(results)
	}

	return results[:limit], nil
}

// GetThreadMessages fetches messages for a thread (supports both DB and filesystem)
func (a *App) GetThreadMessages(sessionID string) ([]Message, error) {
	if a.isDBAvailable() {
		db, err := sql.Open("sqlite", a.dbPath)
		if err != nil {
			return nil, err
		}
		defer db.Close()

		rows, err := db.Query(`
			SELECT role, COALESCE(content, '') as content, COALESCE(tool_name, '') as tool_name, COALESCE(tool_calls, '') as tool_calls, timestamp 
			FROM messages 
			WHERE session_id = ? 
			ORDER BY timestamp ASC`, sessionID)
		if err != nil {
			return nil, err
		}
		defer rows.Close()

		var msgs []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Role, &msg.Content, &msg.ToolName, &msg.ToolCalls, &msg.Timestamp); err != nil {
				fmt.Printf("Scan error in messages: %v\n", err)
				continue
			}
			msgs = append(msgs, msg)
		}
		return msgs, nil
	}

	// Filesystem Fallback
	a.cacheMutex.Lock()
	th, exists := a.cachedThs[sessionID]
	a.cacheMutex.Unlock()

	if !exists {
		return nil, fmt.Errorf("thread not found: %s", sessionID)
	}

	transcriptPath := filepath.Join(th.Path, ".system_generated", "logs", "transcript.jsonl")
	tFile, err := os.Open(transcriptPath)
	if err != nil {
		return nil, err
	}
	defer tFile.Close()

	var msgs []Message
	scanner := bufio.NewScanner(tFile)
	buf := make([]byte, 0, 64*1024)
	scanner.Buffer(buf, 1024*1024)
	
	// Create regexes to strip system wrapper blocks
	userReqRegex := regexp.MustCompile(`(?s)<USER_REQUEST>(.*?)</USER_REQUEST>`)

	for scanner.Scan() {
		var lineObj map[string]interface{}
		if err := json.Unmarshal(scanner.Bytes(), &lineObj); err == nil {
			roleStr, _ := lineObj["role"].(string)
			typeStr, _ := lineObj["type"].(string)
			contentStr, _ := lineObj["content"].(string)
			timestampVal, _ := lineObj["timestamp"].(float64)

			// Normalize role
			if roleStr == "" {
				if typeStr == "USER_INPUT" {
					roleStr = "user"
				} else if typeStr == "PLANNER_RESPONSE" || typeStr == "MODEL" {
					roleStr = "assistant"
				}
			}

			// Clean up user inputs to show only request content
			if roleStr == "user" {
				matches := userReqRegex.FindStringSubmatch(contentStr)
				if len(matches) > 1 {
					contentStr = strings.TrimSpace(matches[1])
				}
			}

			// Capture tool calls if present
			toolCallsJSON := ""
			toolNameVal := ""
			if toolCalls, ok := lineObj["tool_calls"].([]interface{}); ok && len(toolCalls) > 0 {
				if tcBytes, err := json.Marshal(toolCalls); err == nil {
					toolCallsJSON = string(tcBytes)
				}
			}
			if tcName, ok := lineObj["tool_name"].(string); ok {
				toolNameVal = tcName
			}

			if contentStr != "" || toolCallsJSON != "" {
				msgs = append(msgs, Message{
					Role:      roleStr,
					Content:   contentStr,
					ToolName:  toolNameVal,
					ToolCalls: toolCallsJSON,
					Timestamp: timestampVal,
				})
			}
		}
	}

	return msgs, nil
}

// OpenPath opens a file or directory using the macOS 'open' command
func (a *App) OpenPath(path string) error {
	if strings.HasPrefix(path, "~/") {
		path = filepath.Join(a.homeDir, path[2:])
	}
	return exec.Command("open", path).Run()
}

// OpenURL opens a URL in the default browser
func (a *App) OpenURL(url string) error {
	return exec.Command("open", url).Run()
}

// Helper: Extracts a snippet from a text around the query
func extractSnippet(content string, query string) string {
	contentClean := strings.ReplaceAll(content, "\r", "")
	lowerContent := strings.ToLower(contentClean)
	lowerQuery := strings.ToLower(query)
	idx := strings.Index(lowerContent, lowerQuery)
	if idx == -1 {
		if len(contentClean) > 100 {
			return contentClean[:100] + "..."
		}
		return contentClean
	}
	start := idx - 30
	if start < 0 {
		start = 0
	}
	end := idx + len(query) + 80
	if end > len(contentClean) {
		end = len(contentClean)
	}
	snippet := contentClean[start:end]
	snippet = strings.ReplaceAll(snippet, "\n", " ")
	if start > 0 {
		snippet = "..." + snippet
	}
	if end < len(contentClean) {
		snippet = snippet + "..."
	}
	return snippet
}

// Helper: Highlights query instances in lines using HTML mark tag
func highlightQueryText(text string, query string) string {
	lowerText := strings.ToLower(text)
	lowerQuery := strings.ToLower(query)
	var result strings.Builder
	lastIdx := 0
	for {
		idx := strings.Index(lowerText[lastIdx:], lowerQuery)
		if idx == -1 {
			result.WriteString(text[lastIdx:])
			break
		}
		matchStart := lastIdx + idx
		result.WriteString(text[lastIdx:matchStart])
		result.WriteString("<mark>")
		result.WriteString(text[matchStart : matchStart+len(query)])
		result.WriteString("</mark>")
		lastIdx = matchStart + len(query)
	}
	return result.String()
}
