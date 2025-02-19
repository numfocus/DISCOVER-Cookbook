import logging

import click


class ClickLogHandler(logging.Handler):
    _use_stderr = True

    def emit(self, record):
        try:
            msg = self.format(record)
            click.echo(msg, err=self._use_stderr)
        except Exception:
            self.handleError(record)


def setup_logger(logger: logging.Logger) -> None:
    """Add handler to log to click."""
    try:
        import click_log
    except ImportError:
        logger.addHandler(ClickLogHandler())
    else:
        click_log.basic_config(logger)
