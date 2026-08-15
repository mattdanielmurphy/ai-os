var chrome = Application('Google Chrome Canary');
if (chrome.windows.length === 0) {
    console.log(JSON.stringify({error: "No windows open"}));
} else {
    var tab = chrome.windows[0].activeTab();
    var url = tab.url();
    var title = tab.title();
    
    console.log(JSON.stringify({
        url: url,
        title: title
    }));
}
