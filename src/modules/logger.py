import logging
import sys

from fastapi.logger import logger as fastapi_logger
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        frame, depth = logging.currentframe(), 2
        while frame and depth:
            frame = frame.f_back
            depth -= 1

        level = record.levelname
        if level not in logger._core.levels:
            level = "INFO"

        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logger():
    # Remove qualquer configuração anterior
    for log_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging.getLogger(log_name).handlers = []
    logger.remove()

    # Adiciona saída para console
    logger.add(sys.stdout, level="INFO")
    logger.add('logs/app.log', rotation='10 MB', retention='10 days', level='INFO')

    # Redireciona logs padrão do FastAPI para o Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

    for log_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging.getLogger(log_name).handlers = [InterceptHandler()]

    fastapi_logger.handlers = [InterceptHandler()]
    fastapi_logger.setLevel(logging.INFO)
