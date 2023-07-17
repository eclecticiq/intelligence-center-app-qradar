"""Used for encrypting and decrypting data."""
from qpylib.encdec import Encryption

from app.constants.general import NAME, USER


class Cipher:
    """Encrypts or Decrypts the data ."""

    def __init__(self, name, user) -> None:
        self._name = name
        self._user = user

    @property
    def name(self):
        """Get value for name.

        :return: Name
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def user(self):
        """Get value for user.

        :return: User
        :rtype: str
        """
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    def _get_secret_store(self):
        return Encryption({NAME: self.name, USER: self.user})

    def encrypt(self, clear_text):
        """Encrypt the data.

        :param clear_text: Secret key to encrypt data
        :type filename: str
        :return: Encrypted data
        :rtype: str
        """
        store = self._get_secret_store()
        return store.encrypt(clear_text)

    def decrypt(self):
        """Decrypt the data.

        :return: Decrypted data
        :rtype: str
        """
        store = self._get_secret_store()
        return store.decrypt()
