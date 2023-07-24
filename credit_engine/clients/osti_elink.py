import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients.args import AuthenticatedClientArgs

NAME = "OSTI elink"
VALID_OUTPUT_FORMATS = {CE.OutputFormat.JSON, CE.OutputFormat.XML}
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.OSTI_ELINK}"
DEFAULT_FORMAT = CE.OutputFormat.JSON


class ClientArgs(AuthenticatedClientArgs):
    """Arguments for the OSTI elink client.

    :return: object with validated DOI client args
    :rtype: AuthenticatedClientArgs
    """
