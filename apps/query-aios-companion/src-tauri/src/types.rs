#[derive(serde::Deserialize)]
pub struct CommitPayload {
    pub thread_uuid: String,
    pub target_filename: String,
    pub content: String,
}

#[derive(Clone, serde::Serialize)]
pub struct RevisionEvent {
    pub thread_uuid: String,
    pub target_filename: String,
    pub commit_hash: String,
}

#[derive(serde::Deserialize)]
pub struct ContextSyncPayload {
    pub thread_id: String,
    pub content: String,
}

#[derive(serde::Deserialize)]
pub struct GeminiSyncPayload {
    pub url: String,
    pub body: String,
}
