use std::{net::TcpListener, sync::Arc};

use clap::Parser;
use engine_core::{
    conn::TcpConnection, engine::Engine, error::Error, json_rpc_engine::JsonRpcEngine,
    msg::ServerRequest,
};
use futures::StreamExt;
use once_cell::sync::Lazy;
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

static RUNTIME: Lazy<Runtime> = Lazy::new(|| Runtime::new().unwrap());

fn handle_connection(engine: &JsonRpcEngine, conn: &mut TcpConnection) -> Result<(), Error> {
    loop {
        let (input, mut writer) = conn.read::<ServerRequest>()?;
        match input {
            ServerRequest::Ping => writer.write_row(&vec!["Pong"]).unwrap(),
            ServerRequest::Bye => break,
            ServerRequest::GetLogs(qs) => {
                RUNTIME.block_on(async {
                    let mut res =
                        engine.get_logs(qs.from_block, qs.to_block, qs.filters).await.unwrap();
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
