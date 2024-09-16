"""Get Credentials from data store."""


from app.cipher import Cipher
from app.configs.datastore import DATA_STORE_DIR, DATA_STORE_FILE
from app.constants.general import API_KEY, QRADAR_SECURITY_TOKEN, SHARED, PROXY_PASSWORD
from app.datastore import read_data_store


def get_credentials(to_decrypt=False, data_store_dir=DATA_STORE_DIR):
    """Get  encrypted credentials stored in datastore.

    :return: decrypted credentials
    :rtype: dict
    """
    config = read_data_store(data_store_dir, DATA_STORE_FILE)

    if config and to_decrypt:
        config[API_KEY] = Cipher(API_KEY, SHARED).decrypt()
        config[QRADAR_SECURITY_TOKEN] = Cipher(QRADAR_SECURITY_TOKEN, SHARED).decrypt()
        config[PROXY_PASSWORD] = Cipher(PROXY_PASSWORD, SHARED).decrypt()
    return config
