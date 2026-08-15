fn main() {
    let s = serde_json::to_string(&"</THREAD_NAME>").unwrap();
    println!("Serialized: {}", s);
}
