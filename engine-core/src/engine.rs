use std::pin::Pin;

use bytes::Bytes;
use futures::Stream;
use serde::Serialize;

use crate::error::Error;
use crate::types::{Address, Hash};

pub type StreamT<T> = Pin<Box<dyn Stream<Item = T> + Send>>;

#[derive(Serialize)]
pub struct Log {
    pub block_number: i64,
    pub block_hash: Hash,
    pub block_timestamp: i64,
    pub log_index: i64,
    pub tx_hash: Hash,
    pub tx_index: i64,
    pub address: Address,
    pub topics: Vec<Hash>,
    pub data: Bytes,
}

#[async_trait::async_trait]
pub trait Engine {
    async fn get_logs(
        &self,
        from_block: i64,
        to_block: i64,
        filters: Vec<(Address, Hash)>,
    ) -> Result<StreamT<Result<Log, Error>>, Error>;
}
