use std::time::Duration;

use ethers::{
    providers::{Http, Middleware, Provider, StreamExt},
    types::Filter,
};
use reqwest::Url;

#[tokio::main]
async fn main() {
    dotenv::dotenv().ok();
    tracing_subscriber::fmt::init();

    let uri = "https://eth.llamarpc.com";
    // let uri = "https://ethereum.publicnode.com";

    let url = Url::parse(uri).unwrap();
    let x = Http::new_with_client(
        url,
        reqwest::ClientBuilder::new().timeout(Duration::from_secs(2)).build().unwrap(),
    );

    // let client = Provider::<Http>::try_from(uri).unwrap();
    let client = Provider::<Http>::new(x);
    // use ethers::providers::Ws;
    // let client = Provider::<Ws>::connect(uri).await.unwrap();

    let filter = Filter::new().address(vec![
        "0xba11d00c5f74255f56a5e366f4f77f5a186d7f55".parse().unwrap(),
        "0xa1faa113cbe53436df28ff0aee54275c13b40975".parse().unwrap(),
    ]);

    let vals = futures::stream::unfold(10000000, move |start| {
        let mut filter = filter.clone();
        let client = client.clone();
        async move {
            if start > 10100000 {
                return None;
            }
            let end = (start + 1999).min(10100000);
            filter = filter.from_block(start).to_block(end);
            let logs = client.get_logs(&filter).await.unwrap();
            println!("{} {} {}", start, end, logs.len());
            Some((logs, end + 1))
        }
    })
    .flat_map(|vec| futures::stream::iter(vec.into_iter()));

    vals.for_each(|x| async move {
        println!("eiei {:?}", x.block_number);
    })
    .await;

    // println!("{:?}", vals.len());
}
