use serde::{Deserialize, Serialize};
use strum::{AsRefStr, EnumIter, EnumString};

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
