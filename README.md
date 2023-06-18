# Blockpipe Engine

> ⚠️ This is a work-in-progress. For inqueries please contact swit [at] blockpipe [dot] io

## Getting started
To run a blockpipe engine instance to power your blockpipe program, there are two steps that you
need to do.

1. Run the blockpipe engine core. This program will subscribe to relevant data source and serve
TCP endpoint at a specified port (default: 9167). This program should be kept running as the
blockpipe program will subcribe and get data from this endpoint.

2. Run a blockpipe program. This program is constructed by merging a engine program templates with
user logic. The program exposes itself as a HTTP server a specified port (default: 9168). Upon spun
up, it will communicate with the engine core to get relevant blockchain data and continue to fetch
data from the engine core.

We are still working to get things in place. Updates will be pushed as soon as available.

## License
_Blockpipe Engine_ is relased under version 1 of the [Server Side Public License (SSPL)](LICENSE).