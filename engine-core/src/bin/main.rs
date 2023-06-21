use std::{
    io::{BufReader, BufWriter, Read, Write},
    net::{TcpListener, TcpStream},
    sync::Arc,
};

use byteorder::{BigEndian, ReadBytesExt, WriteBytesExt};
use clap::Parser;
use engine_core::{
    engine::Engine,
    json_rpc_engine::JsonRpcEngine,
    types::{Address, Hash},
};
use futures::StreamExt;
use once_cell::sync::Lazy;
use serde::{de::DeserializeOwned, Deserialize, Serialize};
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

#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error(transparent)]
    IOError(#[from] std::io::Error),
    #[error(transparent)]
    MsgPackEncodeError(#[from] rmp_serde::encode::Error),
    #[error(transparent)]
    MsgPackDecodeError(#[from] rmp_serde::decode::Error),
}

pub struct TcpConnection {
    reader: BufReader<TcpStream>,
    writer: BufWriter<TcpStream>,
}

impl TcpConnection {
    pub fn new(stream: TcpStream) -> Self {
        Self {
            reader: BufReader::new(stream.try_clone().unwrap()),
            writer: BufWriter::new(stream.try_clone().unwrap()),
        }
    }

    pub fn read<T: DeserializeOwned>(&mut self) -> Result<T, Error> {
        let size = self.reader.read_u32::<BigEndian>()?;
        let mut data = vec![0; size as usize];
        self.reader.read_exact(&mut data)?;
        Ok(rmp_serde::from_slice(&data)?)
    }

    pub fn write_row<T: Serialize>(&mut self, v: &T) -> Result<(), Error> {
        let data = rmp_serde::to_vec(&ServerResponse::Row(v))?;
        self.write_bytes(&data)
    }

    pub fn write_end(&mut self, v: u64) -> Result<(), Error> {
        let data = rmp_serde::to_vec(&ServerResponse::<()>::End(v))?;
        self.write_bytes(&data)?;
        Ok(self.writer.flush()?)
    }

    pub fn write_error(&mut self, v: &str) -> Result<(), Error> {
        let data = rmp_serde::to_vec(&ServerResponse::<()>::Error(v))?;
        self.write_bytes(&data)
    }

    pub fn write_fatal(&mut self, v: &str) -> Result<(), Error> {
        let data = rmp_serde::to_vec(&ServerResponse::<()>::Fatal(v))?;
        self.write_bytes(&data)
    }

    pub fn write_bytes(&mut self, data: &[u8]) -> Result<(), Error> {
        self.writer.write_u32::<BigEndian>(data.len() as u32)?;
        self.writer.write_all(data)?;
        Ok(())
    }
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
        match conn.read::<ServerRequest>()? {
            ServerRequest::Ping => conn.write_row(&vec!["Pong"]).unwrap(),
            ServerRequest::Bye => break,
            ServerRequest::GetLogs(qs) => {
                RUNTIME.block_on(async {
                    let mut res = engine.get_logs(10000000, 15000000, qs).await.unwrap();
                    while let Some(log) = res.next().await {
                        let log = log.unwrap();
                        conn.write_row(&log).unwrap();
                    }
                    conn.write_end(0).unwrap();
                });
            }
        }
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
