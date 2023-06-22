use std::{collections::HashSet, time::Duration};

use ethers::{
    providers::{Http, Middleware, Provider},
    types::Filter,
};
use futures::StreamExt;
use reqwest::{ClientBuilder, Url};

use crate::{
    engine::{Engine, Log, StreamT},
    error::Error,
    types::{Address, Hash},
};

pub struct JsonRpcEngine {
    client: Provider<Http>,
}

impl JsonRpcEngine {
    pub fn new(rpc_url: &str) -> Self {
        Self {
            client: Provider::new(Http::new_with_client(
                Url::parse(rpc_url).unwrap(),
                ClientBuilder::new().timeout(Duration::from_secs(5)).build().unwrap(),
            )),
        }
    }
}

#[async_trait::async_trait]
impl Engine for JsonRpcEngine {
    async fn get_block_number(&self) -> Result<i64, Error> {
        Ok(self.client.get_block_number().await.unwrap().as_u64() as i64)
    }

    async fn get_logs(
        &self,
        from_block: i64,
        to_block: i64,
        filters: Vec<(Address, Hash)>,
    ) -> Result<StreamT<Result<Log, Error>>, Error> {
        let client = self.client.clone();
        let rpc_filter_base = Filter::new()
            .from_block(from_block)
            .to_block(to_block)
            .address(
                filters
                    .iter()
                    .map(|(addr, _)| addr.0)
                    .collect::<HashSet<_>>()
                    .into_iter()
                    .collect::<Vec<_>>(),
            )
            .topic0(
                filters
                    .iter()
                    .map(|(_, hash)| hash.0)
                    .collect::<HashSet<_>>()
                    .into_iter()
                    .collect::<Vec<_>>(),
            );
        Ok(Box::pin(
            futures::stream::iter((from_block..to_block).step_by(2000))
                .map(move |start| {
                    let client = client.clone();
                    let end = start + 2000 - 1;
                    let filter = rpc_filter_base.clone().from_block(start).to_block(end);
                    async move {
                        let logs = client.get_logs(&filter).await.unwrap();
                        println!("{} logs from {} to {}", logs.len(), start, end);
                        futures::stream::iter(logs.into_iter())
                    }
                })
                .buffered(10)
                .flatten()
                .filter(move |log| {
                    futures::future::ready(
                        filters.iter().any(|(a, h)| a.0 == log.address && h.0 == log.topics[0]),
                    )
                })
                .map(|log| {
                    Ok(Log {
                        block_number: log.block_number.unwrap().as_u64() as i64,
                        block_hash: log.block_hash.unwrap().into(),
                        block_timestamp: 0,
                        log_index: log.log_index.unwrap().as_u64() as i64,
                        tx_hash: log.transaction_hash.unwrap().into(),
                        tx_index: log.transaction_index.unwrap().as_u64() as i64,
                        address: log.address.into(),
                        topics: log.topics.into_iter().map(|topic| topic.into()).collect(),
                        data: log.data.0,
                    })
                }),
        ))
    }
}
