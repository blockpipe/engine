import logging
import time
import uvicorn
from fastapi import FastAPI, Request, Response

from .rw import Reader, Writer


logger = logging.getLogger(__name__)


class WebserverProcess:
    def __init__(self, name, port):
        self.name = name
        self.port = port

    def run_and_exit(self, recv_id, send_id):
        app = FastAPI()
        r = Reader(recv_id)
        w = Writer(send_id)

        @app.get(f'/{self.name}' + '/{path:path}')
        async def handle_request(request: Request, response: Response, path: str):
            query = f'?{request.url.query}' if request.url.query else ''
            fullpath = f'{path}{query}'
            w.write(fullpath)
            v = r.read()
            return v
            # TODO: Check v
            # logging.error(
            #     f'Unexpected response: {v}. Please report to Blockpipe team.')
            # raise HTTPException(500)

        @app.on_event('shutdown')
        def handle_shutdown():
            r.close()
            w.close()
            time.sleep(1)

        uvicorn.run(app, host='0.0.0.0', port=self.port,
                    log_level='error', access_log=False)
        exit(0)
