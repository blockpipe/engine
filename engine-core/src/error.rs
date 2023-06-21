#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error(transparent)]
    IOError(#[from] std::io::Error),
    #[error(transparent)]
    MsgPackEncodeError(#[from] rmp_serde::encode::Error),
    #[error(transparent)]
    MsgPackDecodeError(#[from] rmp_serde::decode::Error),
}
