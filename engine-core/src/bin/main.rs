use std::{
    io::{BufReader, BufWriter, Read, Write},
    net::{TcpListener, TcpStream},
    sync::Arc,
};

use clap::Parser;
use engine_core::{
    conn::TcpConnection,
    engine::Engine,
    error::Error,
    json_rpc_engine::JsonRpcEngine,
    types::{Address, Hash},
};
use futures::StreamExt;
use once_cell::sync::Lazy;
use serde::{Deserialize, Serialize};
use strum::{AsRefStr, EnumIter, EnumString};
use tokio::runtime::Runtime;

#[derive(Parser)]
struct Args {
    #[clap(default_value = "0.0.0.0")]
    host: String,
    #[clap(default_value_t = 9167)]
    port: u16,
    #[clap(default_value = "https://eth.llamarpc.com")]
    rpc_url: String,
}

#[derive(Debug, Clone, Copy, AsRefStr, EnumIter, EnumString, PartialEq, Serialize, Deserialize)]
#[strum(serialize_all = "snake_case")]
#[serde(rename_all = "snake_case")]
pub enum Network {
    EthereumMainnet,
    EthereumGoerli,
    EthereumSepolia,
    ArbitrumOne,
    ArbitrumGoerli,
    OptimismMainnet,
}

#[derive(Deserialize)]
pub enum ServerRequest {
    Ping,                          // Check if the server is responsive
    Bye,                           // Close the connection gracefully
    GetLogs(Vec<(Address, Hash)>), // Get logs from the data source
}

#[derive(Deserialize)]
pub struct ServerArg {
    pub columns: Vec<String>,
    pub network: Option<Network>,
    pub from_block: i64,
    pub to_block: i64,
    pub limit: Option<i64>,
}

#[derive(Serialize, Deserialize)]
pub enum ServerResponse<'a, T> {
    Row(T),         // Data row to client
    End(u64),       // End with total row count
    Error(&'a str), // Frame Error with message string
    Fatal(&'a str), // Fatal error with message string
}

static RUNTIME: Lazy<Runtime> = Lazy::new(|| Runtime::new().unwrap());

fn handle_connection(engine: &JsonRpcEngine, conn: &mut TcpConnection) -> Result<(), Error> {
    loop {
        let (input, mut writer) = conn.read::<ServerRequest>()?;
        match input {
            ServerRequest::Ping => writer.write_row(&vec!["Pong"]).unwrap(),
            ServerRequest::Bye => break,
            ServerRequest::GetLogs(qs) => {
                RUNTIME.block_on(async {
                    let mut res = engine.get_logs(10000000, 10200000, qs).await.unwrap();
                    while let Some(log) = res.next().await {
                        let log = log.unwrap();
                        writer.write_row(&log).unwrap();
                    }
                });
            }
        }
        writer.write_end().unwrap();
    }
    Ok(())
}

fn main() -> std::io::Result<()> {
    tracing_subscriber::fmt::init();
    let args = Arc::new(Args::parse());
    let engine = Arc::new(JsonRpcEngine::new(&args.rpc_url));
    let listener = TcpListener::bind(&format!("{}:{}", &args.host, &args.port))?;
    for stream in listener.incoming() {
        let mut conn = TcpConnection::new(stream?);
        let engine = engine.clone();
        std::thread::spawn(move || match handle_connection(&engine, &mut conn) {
            Ok(_) => {}
            Err(e) => {
                println!("Fatal error: {:?}", e);
                conn.write_fatal(&e.to_string()).unwrap();
            }
        });
    }
    Ok(())
}
