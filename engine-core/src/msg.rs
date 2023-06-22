use serde::{Deserialize, Serialize};

use crate::types::{Address, Hash};

#[derive(Deserialize)]
pub struct GetLogsArg {
    pub from_block: i64,
    pub to_block: i64,
    pub filters: Vec<(Address, Hash)>,
}

#[derive(Deserialize)]
pub enum ServerRequest {
    Ping,                // Check if the server is responsive
    Bye,                 // Close the connection gracefully
    GetLogs(GetLogsArg), // Get logs from the data source
}

#[derive(Serialize)]
pub enum ServerResponse<'a, T> {
    Row(&'a T),     // Data row to client
    End(u64),       // End frame with total row count
    Error(&'a str), // Frame Error with message string
    Fatal(&'a str), // Fatal error with message string
}
