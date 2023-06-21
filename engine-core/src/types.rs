use ethers::types::{H160, H256};
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use serde_bytes::ByteBuf;

pub struct Address(pub H160);
pub struct Hash(pub H256);

impl From<H160> for Address {
    fn from(h: H160) -> Self {
        Address(h)
    }
}

impl From<H256> for Hash {
    fn from(h: H256) -> Self {
        Hash(h)
    }
}

impl Serialize for Address {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_bytes(self.0.as_bytes())
    }
}

impl Serialize for Hash {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_bytes(self.0.as_bytes())
    }
}

impl<'de> Deserialize<'de> for Address {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let s = ByteBuf::deserialize(deserializer)?;
        if s.len() != 20 {
            return Err(serde::de::Error::custom("invalid address length"));
        }
        Ok(Address(H160::from_slice(s.as_slice())))
    }
}

impl<'de> Deserialize<'de> for Hash {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let s = ByteBuf::deserialize(deserializer)?;
        if s.len() != 32 {
            return Err(serde::de::Error::custom("invalid hash length"));
        }
        Ok(Hash(H256::from_slice(s.as_slice())))
    }
}
