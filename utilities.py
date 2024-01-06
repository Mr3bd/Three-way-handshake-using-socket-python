from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from secrets import choice, token_bytes
from string import ascii_letters, digits
from hashlib import pbkdf2_hmac
from cryptography.fernet import Fernet

def write(file,msg):
    fh = open(file,'a')
    fh.write(str(msg))
    fh.close()
    return

class Password:
    BASE = ascii_letters + digits
    MIN_SALT_SIZE = 16
    
    @staticmethod
    def generate(length,base=BASE):
        """
        ----------------------------------------------------
        Parameters:   length (int)
                      base (str)
        Return:       password(str)
        Description:  Generate a password
                      that contain length characters from base
                      Uses cryptographically secure PRNGs
        ---------------------------------------------------
        """
        assert type(length) == int and length > 0, 'invalid length'
        assert type(base) == str and len(base) > 0, 'invalid base'
        return ''.join(choice(base) for _ in range(length))
    
    @staticmethod
    def is_strong(password):
        """
        ----------------------------------------------------
        Parameters:   password (str)
        Return:       True/False
        Description:  Check if given password is strong which is if:
                        - contains at least 14 characters
                        - has at least one lower case character
                        - has at least one upper case character
                        - has at least one digit character
        ---------------------------------------------------
        """
        if len(password) < 14:
            return False
        if(any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)):
            return True
        return False

    @staticmethod
    def generate_strong(length):
        length = 14 if length < 14 else length
        while True:
            password = Password.generate(length)
            if Password.is_strong(password):
                break
        return password
    
    @staticmethod
    def generate_salt(length):
        s = Password.MIN_SALT_SIZE
        length = s if length < s else length
        return token_bytes(length)
    
    @staticmethod
    def hash_password(password,salt=None):
        if salt == None: 
            salt = Password.generate_salt(16)
        if type(password) == str:
            password = password.encode()
        h = pbkdf2_hmac('sha256',password,salt,100000)
        #size of h is always 32 bytes, and size of salt is 16 bytes
        return h,salt
    
class RSA:
    @staticmethod
    def generate_keys(private_key_file, public_key_file):
        """
        ----------------------------------------------------
        Parameters:   private_key_file (str)
                      public_key_file (str)
        Return:       -
        Description:  Generate RSA public and private keys
                      Store the keys in the given files. 
        ---------------------------------------------------
        """
        private = rsa.generate_private_key(65537,1024)
        private_bytes = private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption())
        
        private_fh = open(private_key_file,'wb')
        private_fh.write(private_bytes)
        private_fh.close()
        
        public = private.public_key()
        public_bytes = public.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo)
        public_fh = open(public_key_file,'wb')
        public_fh.write(public_bytes)
        public_fh.close()
        return

    @staticmethod
    def load_key(file_prefix,key_type):
        """
        ----------------------------------------------------
        Parameters:   file_prefix (str): 'server' or 'clientx'
                      key_type (str)
        Return:       RSA_key (RSAPrivateKey or RSAPublicKey)
        Description:  Load RSA public or private key from file
                      key_type is 'private' or 'public'
                      filename = file_prefix + _private/public + '.txt' 
        ---------------------------------------------------
        """
        if key_type == 'private':
            filename = file_prefix + '_private.txt'
        elif key_type == 'public':
            filename = file_prefix + '_public.txt'
        else:
            print('Error(laod_RSA_key): invalid key_type')
            return None, None
        try:
            fh = open(filename,'rb')
            if key_type == 'private':
                key = serialization.load_pem_private_key(fh.read(), password=None)
            else:
                key = serialization.load_pem_public_key(fh.read())
            fh.close()
        except Exception as e:
            print('Error(RSA.load_key): {}'.format(e))
            key = None
        return key

    @staticmethod
    def to_bytes(key,key_type):
        """
        ----------------------------------------------------
        Parameters:   key (RSAPrivateKey or RSAPublicKey)
                      key_type (str)
        Return:       key_bytes (bytes) 
        Description:  Returns the bytes representation of the given RSA Key 
        ---------------------------------------------------
        """
        try:
            if key_type != 'private' and key_type != 'public':
                raise ValueError
            if key_type == 'private':
                key_bytes = key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption())
            else: #public
                key_bytes = key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo)
        except ValueError:
            print('Error(RSA.to_bytes): invalid key_type')
            key_bytes = b''
        return key_bytes
    
    @staticmethod
    def encrypt(public_key,plaintext):
        """
        ----------------------------------------------------
        Parameters:   public_key (RSAPublicKey)
                      plaintext(str or bytes)
        Return:       ciphertext(bytes)
        Description:  Encrypts given plaintext using RSA algorithm
        ---------------------------------------------------
        """
        if type(plaintext) == str:
            plaintext = plaintext.encode()
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    @staticmethod
    def decrypt(private_key,ciphertext):
        """
        ----------------------------------------------------
        Parameters:   private_key (RSAPrivateKey)
                      ciphertext(str or bytes)
        Return:       plaintext(bytes)
        Description:  Decrypts given ciphertext using RSA algorithm
        ---------------------------------------------------
        """
        if type(ciphertext) == str:
            ciphertext = ciphertext.encode()
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext    

