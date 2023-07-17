"""Get Credentials from data store."""


from app.cipher import Cipher
from app.configs.datastore import DATA_STORE_DIR, DATA_STORE_FILE
from app.constants.general import API_KEY, QRADAR_SECURITY_TOKEN, SHARED
from app.datastore import read_data_store


def get_credentials(to_decrypt=False):
    """Get  encrypted credentials stored in datastore.

    :return: decrypted credentials
    :rtype: dict
    """
    config = read_data_store(DATA_STORE_DIR, DATA_STORE_FILE)

    if config and to_decrypt:
        config[API_KEY] = Cipher(API_KEY, SHARED).decrypt()
        config[QRADAR_SECURITY_TOKEN] = Cipher(QRADAR_SECURITY_TOKEN, SHARED).decrypt()
    return config
