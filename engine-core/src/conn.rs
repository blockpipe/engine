use std::{
    io::{BufReader, BufWriter, Read, Write},
    net::TcpStream,
};

use byteorder::{BigEndian, ReadBytesExt, WriteBytesExt};
use serde::{de::DeserializeOwned, Serialize};

use crate::{error::Error, msg::ServerResponse};

pub struct TcpWriter<'a> {
    conn: &'a mut TcpConnection,
    count: u64,
    has_error: bool,
}

impl<'a> TcpWriter<'a> {
    pub fn new(conn: &'a mut TcpConnection) -> Self {
        Self {
            conn,
            count: 0,
            has_error: false,
        }
    }

    pub fn write_row<T: Serialize>(&mut self, v: &T) -> Result<(), Error> {
        self.count += 1;
        self.conn.write_row(v)
    }

    pub fn write_end(&mut self) -> Result<(), Error> {
        self.conn.write_end(self.count)
    }

    pub fn write_error(&mut self, v: &str) -> Result<(), Error> {
        self.has_error = true;
        self.conn.write_error(v)
    }
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

    pub fn read<T: DeserializeOwned>(&mut self) -> Result<(T, TcpWriter), Error> {
        let size = self.reader.read_u32::<BigEndian>()?;
        let mut data = vec![0; size as usize];
        self.reader.read_exact(&mut data)?;
        let v = rmp_serde::from_slice(&data)?;
        Ok((v, TcpWriter::new(self)))
    }

    pub fn write_fatal(&mut self, v: &str) -> Result<(), Error> {
        let data = rmp_serde::to_vec(&ServerResponse::<()>::Fatal(v))?;
        self.write_bytes(&data)
    }

    fn write_row<T: Serialize>(&mut self, v: &T) -> Result<(), Error> {
        let data = rmp_serde::to_vec(&ServerResponse::Row(v))?;
        self.write_bytes(&data)
    }

    fn write_end(&mut self, v: u64) -> Result<(), Error> {
        let data = rmp_serde::to_vec(&ServerResponse::<()>::End(v))?;
        self.write_bytes(&data)?;
        Ok(self.writer.flush()?)
    }

    fn write_error(&mut self, v: &str) -> Result<(), Error> {
        let data = rmp_serde::to_vec(&ServerResponse::<()>::Error(v))?;
        self.write_bytes(&data)
    }

    fn write_bytes(&mut self, data: &[u8]) -> Result<(), Error> {
        self.writer.write_u32::<BigEndian>(data.len() as u32)?;
        self.writer.write_all(data)?;
        Ok(())
    }
}
