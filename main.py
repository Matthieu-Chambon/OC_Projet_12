from app.cli import core
from app.cli.core import prepare_sentry_scope
from app.config import SENTRY_DSN
import sentry_sdk


sentry_sdk.init(
    dsn=SENTRY_DSN,
)

if __name__ == "__main__":
    try:
        core.cli()
    except Exception as e:
        print(f"[ERREUR FATALE] : {e}")
        prepare_sentry_scope()
        sentry_sdk.capture_exception(e)
