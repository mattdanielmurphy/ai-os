let liveAgyStream = "Thinking...\n⠋ Some thought";
let data = "\r⠙ Some thought\nNext line";
let stripped = data.replace(/\x1B\[[0-?]*[ -/]*[@-~]/g, '');
for (let i = 0; i < stripped.length; i++) {
    if (stripped[i] === '\r') {
        const lastNewline = liveAgyStream.lastIndexOf('\n');
        liveAgyStream = liveAgyStream.substring(0, lastNewline + 1);
    } else if (stripped[i] === '\b') {
        liveAgyStream = liveAgyStream.slice(0, -1);
    } else {
        liveAgyStream += stripped[i];
    }
}
console.log(JSON.stringify(liveAgyStream));
