try {
    var chrome = Application('Google Chrome Canary');
    if (chrome.windows.length === 0) {
        JSON.stringify({error: "No windows open"});
    } else {
        var tab = chrome.windows[0].activeTab();
        var url = tab.url();
        var title = tab.title();
        
        var js = `
            (function() {
                var text = document.body ? document.body.innerText : "";
                if (text.length > 20000) {
                    text = text.substring(0, 20000) + "... [truncated]";
                }
                return text;
            })();
        `;
        
        var inner_text = tab.execute({javascript: js}) || "";
        
        JSON.stringify({
            url: url || "",
            title: title || "",
            inner_text: inner_text
        });
    }
} catch (e) {
    JSON.stringify({error: e.toString()});
}
