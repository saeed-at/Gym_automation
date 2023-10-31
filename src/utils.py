import json
from cryptography.fernet import Fernet
import os

def encrypt_credentials(username, password):
    """
    Encrypts the given username and password, then writes them to a file.

    Args:
    - username (str): The username to be encrypted.
    - password (str): The password to be encrypted.

    Writes the encrypted username and password to a file named 'credentials.txt'.
    """
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    encrypted_username = cipher_suite.encrypt(username.encode())
    encrypted_password = cipher_suite.encrypt(password.encode())

    with open("data/credentials.txt", "wb") as file:
        file.write(key + b'\n')
        file.write(encrypted_username + b'\n')
        file.write(encrypted_password)


def decrypt_credentials():
    """
    Reads and decrypts the stored credentials from the 'credentials.txt' file.

    Returns:
    - str: Decrypted username.
    - str: Decrypted password.
    """
    with open("data/credentials.txt", "rb") as file:
        key = file.readline().rstrip()
        cipher_suite = Fernet(key)
        encrypted_username = file.readline().rstrip()
        encrypted_password = file.readline()

        username = cipher_suite.decrypt(encrypted_username).decode()
        password = cipher_suite.decrypt(encrypted_password).decode()

        return username, password


def store_preferred_sessions(preferred_session):
    """
    Stores the preferred sessions in a JSON file.

    Args:
    - preferred_session (dict): A dictionary containing preferred session data.

    Writes the preferred sessions to a file named 'preferred_sessions.json'.
    """
    file_path = "data/preferred_sessions.json"
    with open(file_path, "w") as file:
        json.dump(preferred_session, file)


def read_preferred_sessions():
    """
    Reads the stored preferred sessions from the 'preferred_sessions.json' file.

    Returns:
    - dict: The preferred session data if the file exists, otherwise None.
    """
    file_path = 'data/preferred_sessions.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    else:
        return


def remove_json_file(file_name):
    """
    Removes the specified JSON file.

    Args:
    - file_name (str): The name of the file to be removed.
    """
    os.remove(file_name)
