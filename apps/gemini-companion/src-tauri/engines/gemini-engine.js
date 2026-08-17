// AI-OS — Unified Gemini Engine.
// Performs StreamGenerate request routing, Scotty file uploads, and session management.

(function () {
    if (window.__aiosGeminiUnified) return;

    var TIMEOUT = 360000;
    var TOKEN_TTL = 300000;
    var _tokens = null;
    var _tokensFetchedAt = 0;

    function generateUuid() {
        return (window.crypto && window.crypto.randomUUID) ? window.crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    var _conversationId = '';
    var _responseId = '';
    var _choiceId = '';
    var _contextToken = '';
    var _sessionUuid = generateUuid().toUpperCase();
    var _workspaces = { fast: [], thinking: [] };

    var _sessions = {};
    var _currentSessionId = null;
    try {
        var saved = localStorage.getItem('aios_sessions');
        if (saved) {
            _sessions = JSON.parse(saved);
            console.log('[AI-OS API] Restored', Object.keys(_sessions).length, 'sessions from localStorage');
        }
    } catch (e) {
        console.error('[AI-OS API] Failed to restore sessions:', e);
    }

    var MAX_SESSIONS = 200;
    function _pruneSessions() {
        var keys = Object.keys(_sessions);
        for (var i = 0; i < keys.length && Object.keys(_sessions).length > MAX_SESSIONS; i++) {
            if (keys[i] !== _currentSessionId) delete _sessions[keys[i]];
        }
    }

    function activateSession(sessionId) {
        if (!sessionId) sessionId = 'default';
        _currentSessionId = sessionId;
        if (!_sessions[sessionId]) {
            _sessions[sessionId] = {
                conversationId: '',
                responseId: '',
                choiceId: '',
                contextToken: '',
                sessionUuid: generateUuid().toUpperCase()
            };
        }
        var sess = _sessions[sessionId];
        if (!sess.sessionUuid) {
            sess.sessionUuid = generateUuid().toUpperCase();
        }
        _conversationId = sess.conversationId;
        _responseId = sess.responseId;
        _choiceId = sess.choiceId;
        _contextToken = sess.contextToken || '';
        _sessionUuid = sess.sessionUuid;
        return sess;
    }

    function saveSession(sessionId) {
        if (!sessionId) sessionId = 'default';
        var sess = _sessions[sessionId];
        if (sess) {
            sess.conversationId = _conversationId;
            sess.responseId = _responseId;
            sess.choiceId = _choiceId;
            sess.contextToken = _contextToken;
            sess.sessionUuid = _sessionUuid;
        }
        try {
            _pruneSessions();
            localStorage.setItem('aios_sessions', JSON.stringify(_sessions));
        } catch (e) { }
    }

    function _detectWorkspaces() {
        try {
            if (window.WIZ_global_data) {
                for (var key in window.WIZ_global_data) {
                    var val = window.WIZ_global_data[key];
                    if (typeof val === 'string' && val.indexOf('thinking=') !== -1) {
                        var parts = val.replace(/\\u003d/g, '=').split('","');
                        parts.forEach(function (part) {
                            var cleanPart = part.replace(/"/g, '');
                            if (cleanPart.indexOf('thinking=') === 0) {
                                _workspaces.thinking = cleanPart.replace('thinking=', '').split(',');
                            } else if (cleanPart.indexOf('fast=') === 0) {
                                _workspaces.fast = cleanPart.replace('fast=', '').split(',');
                            }
                        });
                    }
                }
            }

            if (_workspaces.fast.length === 0) {
                var html = document.documentElement.innerHTML;
                var m3Idx = html.indexOf('m3eQte');
                if (m3Idx !== -1) {
                    var m3Snippet = html.substring(m3Idx, m3Idx + 400);
                    var startIdx = m3Snippet.indexOf('[[');
                    var endIdx = m3Snippet.indexOf(']]');
                    if (startIdx !== -1 && endIdx !== -1) {
                        var content = m3Snippet.substring(startIdx + 2, endIdx);
                        var rawConfig = content
                            .replace(/\\\\u003d/g, '=')
                            .replace(/\\u003d/g, '=')
                            .replace(/\\\\/g, '')
                            .replace(/\\"/g, '"');

                        var parts = rawConfig.split('","');
                        parts.forEach(function (part) {
                            var cleanPart = part.replace(/"/g, '');
                            if (cleanPart.indexOf('thinking=') === 0) {
                                _workspaces.thinking = cleanPart.replace('thinking=', '').split(',');
                            } else if (cleanPart.indexOf('fast=') === 0) {
                                _workspaces.fast = cleanPart.replace('fast=', '').split(',');
                            }
                        });
                    }
                }
            }

            console.log('[AI-OS API] Detected Workspaces:', JSON.stringify(_workspaces));
        } catch (e) {
            console.error('[AI-OS API] Workspace detection error:', e);
        }
    }

    async function _getTokens(forceRefresh) {
        var isExpired = (Date.now() - _tokensFetchedAt) > TOKEN_TTL;
        if (_tokens && !forceRefresh && !isExpired) return _tokens;

        // Extract from active page context to avoid multi-account mismatch
        var at = null;
        var bl = null;
        try {
            // 1. Try WIZ_global_data
            if (window.WIZ_global_data) {
                for (var key in window.WIZ_global_data) {
                    var val = window.WIZ_global_data[key];
                    if (Array.isArray(val)) {
                        var foundAt = null;
                        var foundBl = null;
                        function searchArray(arr) {
                            for (var i = 0; i < arr.length; i++) {
                                if (typeof arr[i] === 'string') {
                                    if (arr[i] === 'SNlM0e' && typeof arr[i+1] === 'string') {
                                        foundAt = arr[i+1];
                                    } else if (arr[i] === 'cfb2h' && typeof arr[i+1] === 'string') {
                                        foundBl = arr[i+1];
                                    }
                                }
                                if (Array.isArray(arr[i])) searchArray(arr[i]);
                            }
                        }
                        searchArray(val);
                        if (foundAt) at = foundAt;
                        if (foundBl) bl = foundBl;
                    }
                }
            }

            // 2. Try raw HTML of the current document
            var html = document.documentElement.innerHTML;
            if (!at) {
                var atMatch = html.match(/"SNlM0e"\s*:\s*"([^"]+)"/) || html.match(/SNlM0e":"([^"]+)"/);
                if (atMatch) at = atMatch[1];
            }
            if (!bl) {
                var blMatch = html.match(/"cfb2h"\s*:\s*"([^"]+)"/) || html.match(/cfb2h":"([^"]+)"/) || html.match(/boq_assistant-bard-web-server_[a-zA-Z0-9_\.\-]+/);
                if (blMatch) bl = blMatch[1] || blMatch[0];
            }
        } catch (e) {
            console.error('[AI-OS API] Failed to extract tokens from page context:', e);
        }

        if (at && bl) {
            _tokens = { at: at, bl: bl };
            _tokensFetchedAt = Date.now();
            console.log('[AI-OS API] Dynamically extracted active tokens from page memory. AT:', at.substring(0, 15) + '...', 'BL:', bl);
            return _tokens;
        }

        console.log('[AI-OS API] Mismatch/Missing tokens in memory. Fetching fallback tokens from /faq...');
        var controller = new AbortController();
        var tid = setTimeout(function () { controller.abort(); }, 30000);

        var res = await fetch('/faq', { credentials: 'include', signal: controller.signal });
        clearTimeout(tid);

        if (!res.ok) throw new Error('Gemini page fetch failed (' + res.status + ')');
        var html = await res.text();

        if (html.indexOf('$authuser') === -1) {
            throw new Error('Not logged into Google');
        }

        try {
            at = html.split('SNlM0e')[1].split('":"')[1].split('"')[0];
        } catch (e) { throw new Error('Failed to extract SNlM0e token'); }

        try {
            bl = html.split('cfb2h')[1].split('":"')[1].split('"')[0];
        } catch (e) { throw new Error('Failed to extract cfb2h token'); }

        _tokens = { at: at, bl: bl };
        _tokensFetchedAt = Date.now();
        return _tokens;
    }

    function _parseResponse(rawText, commitIds) {
        var cleanText = rawText.replace(/^\)\]}'?\s*\n?/, '');
        var lines = cleanText.split('\n').filter(function (l) { return l.trim().length > 0; });

        var allItems = [];
        var dataIndices = [];

        for (var li = 0; li < lines.length; li++) {
            try {
                var arr = JSON.parse(lines[li]);
                if (Array.isArray(arr) && arr.length > 0) {
                    for (var ai = 0; ai < arr.length; ai++) {
                        var item = arr[ai];
                        if (!Array.isArray(item)) continue;
                        for (var idx = 0; idx < Math.min(item.length, 6); idx++) {
                            if (typeof item[idx] === 'string' && item[idx].length > 50) {
                                try {
                                    JSON.parse(item[idx]);
                                    allItems.push(item);
                                    dataIndices.push(idx);
                                    break;
                                } catch (e) { }
                            }
                        }
                    }
                }
            } catch (e) { }
        }

        if (allItems.length === 0) {
            var jsonStrings = [];
            function deepSearch(obj) {
                if (typeof obj === 'string' && obj.length > 50) {
                    try { JSON.parse(obj); jsonStrings.push(obj); } catch (e) { }
                } else if (Array.isArray(obj)) {
                    for (var i = 0; i < obj.length; i++) deepSearch(obj[i]);
                }
            }
            for (var i = 0; i < lines.length; i++) {
                try { deepSearch(JSON.parse(lines[i])); } catch (e) { }
            }
            if (jsonStrings.length > 0) {
                for (var j = 0; j < jsonStrings.length; j++) {
                    allItems.push([null, null, jsonStrings[j]]);
                    dataIndices.push(2);
                }
            }
        }

        if (allItems.length === 0) {
            console.error('[AI-OS API] Parse error: Raw response length is ' + rawText.length + '. Content: ' + rawText.substring(0, 500));
            throw new Error('Failed to parse Gemini response');
        }

        var extracted = { conversationId: null, responseId: null, choiceId: null, contextToken: null };
        var _answerFrameSeen = false;

        for (var ci = 0; ci < allItems.length; ci++) {
            try {
                var innerC = JSON.parse(allItems[ci][dataIndices[ci] || 2]);
                var hasChoice = innerC[4] && innerC[4][0]
                    && typeof innerC[4][0][0] === 'string' && innerC[4][0][0].length > 5;

                if (hasChoice) {
                    if (innerC[1] && Array.isArray(innerC[1])) {
                        if (typeof innerC[1][0] === 'string' && innerC[1][0].length > 5) {
                            extracted.conversationId = innerC[1][0];
                        }
                        if (typeof innerC[1][1] === 'string' && innerC[1][1].length > 5) {
                            extracted.responseId = innerC[1][1];
                        }
                    }
                    extracted.choiceId = innerC[4][0][0];
                    _answerFrameSeen = true;
                } else if (!_answerFrameSeen && innerC[1] && Array.isArray(innerC[1])) {
                    if (typeof innerC[1][0] === 'string' && innerC[1][0].length > 5) {
                        extracted.conversationId = innerC[1][0];
                    }
                    if (typeof innerC[1][1] === 'string' && innerC[1][1].length > 5) {
                        extracted.responseId = innerC[1][1];
                    }
                }

                if (innerC[2] && typeof innerC[2] === 'object' && !Array.isArray(innerC[2])
                    && typeof innerC[2]['26'] === 'string' && innerC[2]['26'].length > 5) {
                    extracted.contextToken = innerC[2]['26'];
                }
            } catch (e) { }
        }

        if (commitIds) {
            if (extracted.conversationId) _conversationId = extracted.conversationId;
            if (extracted.responseId) _responseId = extracted.responseId;
            if (extracted.choiceId) _choiceId = extracted.choiceId;
            if (extracted.contextToken) _contextToken = extracted.contextToken;
        }

        var replyText = '';

        for (var i = 0; i < allItems.length; i++) {
            var item = allItems[i];
            var idx = dataIndices[i] || 2;
            try {
                var inner = JSON.parse(item[idx]);
                var paths = [
                    function () { return (Array.isArray(inner[0]) && typeof inner[0][0] === 'string') ? inner[0][0] : ''; },
                    function () { return (inner[4] && inner[4][0] && inner[4][0][1] && inner[4][0][1][0]) || ''; },
                    function () { return (inner[4] && inner[4][0] && inner[4][0][1]) || ''; },
                    function () { return (Array.isArray(inner[1]) && typeof inner[1][0] === 'string') ? inner[1][0] : ''; },
                    function () { return (inner[0] && inner[0][1] && inner[0][1][0]) || ''; },
                    function () { return (inner[3] && inner[3][0] && inner[3][0][0]) || ''; },
                    function () { return (inner[3] && inner[3][1] && inner[3][1][0]) || '' }
                ];

                for (var pi = 0; pi < paths.length; pi++) {
                    try {
                        var candidate = paths[pi]();
                        if (typeof candidate === 'string' && candidate.length > 0 && candidate.length > replyText.length && !/^[rc]_[a-f0-9]{16,}$/.test(candidate) && !/^(https?:)?\/\/[^\s]+$/.test(candidate.trim())) {
                            replyText = candidate;
                        }
                    } catch (e) { }
                }

                if (!replyText) {
                    function findLongest(obj, depth) {
                        if (depth > 8) return '';
                        if (typeof obj === 'string') return obj;
                        var longest = '';
                        if (Array.isArray(obj)) {
                            for (var k = 0; k < obj.length; k++) {
                                var s = findLongest(obj[k], depth + 1);
                                if (typeof s === 'string' && s.length > longest.length) longest = s;
                            }
                        }
                        return longest;
                    }
                    var longest = findLongest(inner, 0);
                    if (longest.length > 0 && longest.length > replyText.length && !/^[rc]_[a-f0-9]{16,}$/.test(longest) && !/^(https?:)?\/\/[^\s]+$/.test(longest.trim())) replyText = longest;
                }
            } catch (e) { }
        }

        if (!replyText) {
            if (commitIds) {
                console.error('[AI-OS API] Parse error: ReplyText empty. Raw response: ' + rawText.substring(0, 500));
            }
            throw new Error('Could not extract reply from Gemini');
        }
        return replyText;
    }

    async function uploadFileToGoogle(fileBase64, filename, mimeType) {
        console.log('[AI-OS Gemini API] Initializing resumable upload for:', filename);

        var binaryString = atob(fileBase64);
        var uint8Array = new Uint8Array(binaryString.length);
        for (var i = 0; i < binaryString.length; i++) {
            uint8Array[i] = binaryString.charCodeAt(i);
        }
        var size = uint8Array.byteLength;

        var pushId = 'feeds/mcudyrk2a4khkz';

        var initHeaders = {
            'Push-ID': pushId,
            'X-Tenant-Id': 'bard-storage',
            'X-Goog-Upload-Header-Content-Length': size.toString(),
            'X-Goog-Upload-Protocol': 'resumable',
            'X-Goog-Upload-Command': 'start',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        };

        var initRes = await fetch('https://push.clients6.google.com/upload/', {
            method: 'POST',
            headers: initHeaders,
            body: 'File name: ' + filename
        });

        if (!initRes.ok) {
            var errText = await initRes.text();
            throw new Error('Scotty upload initialization failed (' + initRes.status + '): ' + errText);
        }

        var uploadUrl = initRes.headers.get('x-goog-upload-url');
        if (!uploadUrl) {
            throw new Error('Upload Session URL not returned in headers');
        }

        console.log('[AI-OS Gemini API] Resumable session created. Transferring binary bytes...');
        var uploadRes = await fetch(uploadUrl, {
            method: 'POST',
            headers: {
                'Content-Type': mimeType || 'application/octet-stream',
                'X-Goog-Upload-Command': 'upload, finalize',
                'X-Goog-Upload-Offset': '0'
            },
            body: uint8Array
        });

        if (!uploadRes.ok) {
            var uploadErr = await uploadRes.text();
            throw new Error('Scotty file binary transfer failed (' + uploadRes.status + '): ' + uploadErr.substring(0, 200));
        }

        var resJson = await uploadRes.json();
        var token = resJson.sessionStatus && resJson.sessionStatus.additionalInfo && resJson.sessionStatus.additionalInfo['uploader_service.GoogleWinCounter_token'];
        if (!token) {
            token = resJson.sessionStatus && resJson.sessionStatus.token;
        }
        if (!token) {
            throw new Error('Scotty file upload succeeded but token not found in response');
        }

        console.log('[AI-OS Gemini API] Upload successful! Token retrieved:', token);
        return {
            token: token,
            filename: filename,
            mime: mimeType
        };
    }

    function setupStreamReceiver() {
        window.__aiosGeminiStream = { response: '', status: 'streaming', updates: [] };
        window.addEventListener('message', function (e) {
            if (e.data && e.data.type === 'gemini_stream_chunk') {
                var chunk = e.data.chunk;
                var raw = chunk.raw || '';
                var parsed = chunk.parsed || '';
                var isEnd = chunk.isEnd || false;

                var updateText = window.__aiosGeminiStream.response || '';
                if (parsed) {
                    if (updateText && parsed.startsWith(updateText)) {
                        window.__aiosGeminiStream.response = parsed;
                    } else if (parsed.length > updateText.length) {
                        window.__aiosGeminiStream.response = parsed;
                    } else {
                        window.__aiosGeminiStream.response += parsed;
                    }
                }
                var _updates = window.__aiosGeminiStream.updates;
                _updates.push({
                    raw: raw,
                    parsed: parsed,
                    timestamp: Date.now()
                });

                if (isEnd) {
                    window.__aiosGeminiStream.status = 'done';
                }
            }
        });
    }

    async function send(prompt, engine, attachments, sessionId, isFirstMessage) {
        activateSession(sessionId);
        _detectWorkspaces();
        
        try {
            engine = engine || 'auto';

            if (isFirstMessage && prompt.length > 500) {
                console.log('[AI-OS API] New conversation with large prompt detected. Warming up conversation first...');
                try {
                    await sendRaw('hi', engine, null, null, null, null, false);
                    console.log('[AI-OS API] Conversation warmed up successfully. Sending actual prompt...');
                } catch (warmupErr) {
                    console.warn('[AI-OS API] Warmup failed, attempting direct send anyway...', warmupErr.message);
                }
            }

            var workspaceId = 'fbb127bbb056c959';
            if (engine.indexOf(':') !== -1) {
                workspaceId = engine.split(':')[1];
            } else if (engine === '3.5-flash') {
                workspaceId = _workspaces.fast[0] || '56fdd199312815e2';
            } else if (engine === '3.1-pro') {
                workspaceId = _workspaces.thinking[0] || '9d8ca3786ebdfbea';
            } else if (engine === '3.1-flash-lite') {
                workspaceId = (document.documentElement.innerHTML.indexOf('8c46e95b1a07cecc') !== -1) ? '8c46e95b1a07cecc' : (_workspaces.fast[0] || '8c46e95b1a07cecc');
            } else {
                workspaceId = _workspaces.fast[0] || 'fbb127bbb056c959';
            }

            var profiles = {
                '9d8ca3786ebdfbea': { modelId: 3, customIndex11: 1, inner79: 3 },
                'e6fa609c3fa255c0': { modelId: 3, customIndex11: 1, inner79: 3 },
                '56fdd199312815e2': { modelId: 1, customIndex11: 2, inner79: 1 },
                'fbb127bbb056c959': { modelId: 1, customIndex11: 2, inner79: 1 },
                '797f3d0293f288ad': { modelId: 1, customIndex11: 2, inner79: 1 },
                '8c46e95b1a07cecc': { modelId: 6, customIndex11: 2, inner79: 6 }
            };

            var profile = profiles[workspaceId] || { modelId: 1, customIndex11: 2, inner79: 1 };
            
            return await sendRaw(prompt, engine, attachments, workspaceId, profile.modelId, profile.inner79, false);
        } catch (err) {
            _contextToken = '';
            saveSession();
            throw err;
        }
    }

    async function sendRaw(prompt, engine, attachments, workspaceId, modelId, modelIdentifier, _isRetry) {
        var tokens = await _getTokens();
        var reqId = Math.floor(900000 * Math.random()) + 100000;

        var queryParams = new URLSearchParams({
            bl: tokens.bl,
            rt: 'c',
            _reqid: reqId.toString()
        });

        var attachmentsArray = null;
        if (attachments && attachments.token) {
            var typeCode = 1;
            var mime = attachments.mime || '';
            if (mime.startsWith('image/')) typeCode = 1;
            else if (mime.startsWith('video/')) typeCode = 2;
            else if (mime.startsWith('audio/')) typeCode = 3;
            else if (mime.includes('pdf') || mime.startsWith('text/')) typeCode = 4;

            console.log('[AI-OS API] Sending message with attachment - Code:', typeCode, 'Mime:', mime);
            attachmentsArray = [
                [
                    [
                        attachments.token,
                        typeCode,
                        null,
                        mime
                    ],
                    attachments.filename || 'file',
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    [0]
                ]
            ];
        }

        var innerReq = new Array(81).fill(null);
        innerReq[0] = [prompt, 0, null, attachmentsArray, null, null, 0];
        innerReq[1] = ["en-GB"];
        innerReq[2] = [_conversationId || "", _responseId || "", _choiceId || "", null, null, null, null, null, null, _contextToken || ""];
        innerReq[6] = [1];
        innerReq[7] = 1;
        innerReq[10] = 1;
        innerReq[11] = 0;
        innerReq[17] = _conversationId ? [[1]] : [[0]];
        innerReq[18] = 0;
        innerReq[27] = 1;
        innerReq[30] = [4];
        innerReq[41] = [1];
        innerReq[53] = 0;
        var requestUuid = generateUuid().toUpperCase();
        innerReq[59] = requestUuid;
        innerReq[68] = 2;
        innerReq[79] = modelIdentifier;
        innerReq[80] = 1;

        var body = new URLSearchParams({
            at: tokens.at,
            'f.req': JSON.stringify([null, JSON.stringify(innerReq)])
        });

        var headers = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'x-same-domain': '1',
            'x-goog-ext-73010989-jspb': '[0]',
            'x-goog-ext-73010990-jspb': '[0,0,0]',
            'x-goog-ext-525001261-jspb': JSON.stringify([1, null, null, null, workspaceId, null, null, 0, [4, 5, 6, 8], null, null, 2, null, null, modelId, 1, _sessionUuid]),
            'x-goog-ext-525005358-jspb': JSON.stringify([requestUuid, 1])
        };

        var url = '/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate?' + queryParams;
        var res = await fetch(url, { method: 'POST', credentials: 'include', headers: headers, body: body });

        if (!res.ok) {
            if (res.status === 400 && _conversationId) {
                console.log('[AI-OS API] Old conversation ID invalid on current account. Resetting session...');
                _conversationId = '';
                _responseId = '';
                _choiceId = '';
                _contextToken = '';
                saveSession();
                return await sendRaw(prompt, engine, attachments, workspaceId, modelId, null, _isRetry);
            }
            throw new Error('Gemini API error (' + res.status + ')');
        }

        var result = await _parseResponse(await res.text(), true);
        saveSession();
        return result;
    }

    function newConversation(sessionId) {
        if (sessionId) {
            activateSession(sessionId);
            _sessions[sessionId] = {
                conversationId: '',
                responseId: '',
                choiceId: '',
                contextToken: '',
                sessionUuid: generateUuid().toUpperCase()
            };
        }
        _conversationId = '';
        _responseId = '';
        _choiceId = '';
        _contextToken = '';
        _sessionUuid = generateUuid().toUpperCase();
        try {
            localStorage.setItem('aios_sessions', JSON.stringify(_sessions));
        } catch (e) { }
        try {
            if (window.history && window.history.replaceState) {
                window.history.replaceState(null, '', '/app');
            }
        } catch (historyErr) {
            console.warn('[AI-OS API] Failed to update history state:', historyErr.message);
        }
        console.log('[AI-OS API] Conversation reset:', sessionId || 'current');
    }

    window.__aiosGeminiUnified = { send: send, newConversation: newConversation };
    window.__aiosGemini = {
        send: function (msg, engine, attachments, sessionId) { return send(msg, engine || 'auto', attachments, sessionId, true); },
        newConversation: newConversation,
        uploadFileToGoogle: uploadFileToGoogle
    };

    console.log('[AI-OS] Upgraded Unified Multimodal Gemini Engine Loaded');
})();
