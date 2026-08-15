use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use crate::types::ProjectSession;

pub type SessionMap = Arc<Mutex<HashMap<String, ProjectSession>>>;

pub fn create_session_map() -> SessionMap {
    Arc::new(Mutex::new(HashMap::new()))
}
