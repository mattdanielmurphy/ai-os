const ws = new WebSocket("ws://127.0.0.1:9119/api/ws");

ws.onopen = () => {
  console.log("Connected!");
  const req = {
    jsonrpc: "2.0",
    id: 1,
    method: "session.create",
    params: { cols: 80, source: "test" }
  };
  ws.send(JSON.stringify(req));
};

ws.onmessage = (event) => {
  console.log("Response:", event.data);
  ws.close();
  process.exit(0);
};

ws.onerror = (err) => {
  console.error("Error:", err);
  process.exit(1);
};

setTimeout(() => {
  console.log("Timeout waiting for response");
  process.exit(1);
}, 5000);
