use std::fs;

fn main() {
    let content = fs::read_to_string("/Users/matthewmurphy/.gemini/antigravity-cli/brain/bd2a7f09-d821-48f0-8848-54c101de9457/.system_generated/logs/transcript.jsonl").unwrap();
    if let Some(start_idx) = content.find("<THREAD_NAME>") {
        println!("FOUND START TAG at {}", start_idx);
        if let Some(end_idx) = content[start_idx..].find("</THREAD_NAME>") {
            println!("FOUND END TAG at offset {}", end_idx);
            let title = content[start_idx + 13..start_idx + end_idx].trim().to_string();
            println!("TITLE:\n{}", title);
        } else {
            println!("END TAG NOT FOUND");
        }
    } else {
        println!("START TAG NOT FOUND");
    }
}
