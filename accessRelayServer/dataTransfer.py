import websockets
import asyncio
import json
import os
import bcrypt
# import ssl
from cryptography.hazmat.primitives import serialization
import threading
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
from database.dataBase import DataBase
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
import jwt
import datetime
from pathlib import Path
from cryptographyFiles.Cryptography import Cryptography
import time

class jwtAuth:
    def __init__(self,BASE_DIR):
        path = os.path.join(BASE_DIR,"account.json")
        with open(path,"r") as file:
            data = json.load(file)
        self.SECRET_KEY = data['SECRET_KEY']
    def createToken(self,boxId):

        # User data to include in the token
        payload = {
            "boxId": boxId,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  # Expiration time (optional but important)
        }

        return jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
    
    def decryptToken(self,token):
        try:
            decoded_payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
            return decoded_payload['boxId']
        except:
            return False
class JSONEncryptor:
    def __init__(self, password: str):
        self.password = password.encode()
        self.backend = default_backend()

    def _derive_key(self, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=self.backend
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password))

    def encrypt_json(self, data: dict) -> bytes:
        json_data = json.dumps(data).encode()
        salt = os.urandom(16)
        key = self._derive_key(salt)
        f = Fernet(key)
        encrypted = f.encrypt(json_data)
        return salt + encrypted  # prepend salt to use it during decryption

    def decrypt_json(self, encrypted_data: bytes) -> dict:
        salt = encrypted_data[:16]
        real_data = encrypted_data[16:]
        key = self._derive_key(salt)
        f = Fernet(key)
        decrypted = f.decrypt(real_data)
        return json.loads(decrypted.decode())

class subTask:
    def __init__(self,reciverId,BASE_DIR,IP):
        self.IP = IP
        self.BASE_DIR = BASE_DIR
        self.reciverId = reciverId
        self.relayConnection = None
        self.loop = asyncio.get_event_loop()
        self.connectRelay()
    async def connectToRelay(self):
        try:
            url = f"wss://{self.IP}/ws/relay/subTask/{self.reciverId}/"
            self.relayConnection = await websockets.connect(url)
        except:
            print('error') ## change after development
            
    def connectRelay(self):
        self.loop.create_task(self.connectToRelay())
        
    
    def getPublicKey(self):
        publicKeyObj = passwordEncryptAndDecrypt(self.BASE_DIR)
        return publicKeyObj.convetToText(publicKeyObj.getPublicKey())
    
    async def shearPublicKey(self):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        publicKey = self.getPublicKey()
        jsonData = json.dumps({'response':'sendingPublicKey','publicKey':publicKey})
        await self.relayConnection.send(jsonData)
        
    def publicKey(self):
        self.loop.create_task(self.shearPublicKey())
        
    async def authentication(self,info):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        db = DataBase()
        boxInfo = db.getDataOfBox(info['boxId'])
        status = 404
        encData = False
        if boxInfo:
            if boxInfo[3]:
                if bcrypt.checkpw(info['password'].encode(), boxInfo[2]):
                    status = 200
            else:
                if boxInfo[2] == info['password']:
                    status = 200
            if status == 200:
                jwtToken = jwtAuth(self.BASE_DIR)
                token = jwtToken.createToken(info['boxId'])
                boxInfo = db.listAllFileByBoxId(boxInfo[0])
                data = {
                    'fileInfo' : boxInfo,
                    'jwtToken' : token,
                }
                encObj = JSONEncryptor(password=info['password'])
                encData = encObj.encrypt_json(data=data)
                encData = base64.b64encode(encData).decode()
            await self.relayConnection.send(json.dumps({'response':'sharingFileInfo','status':status,'data':encData}))
        else:
            await self.relayConnection.send(json.dumps({'response':'sharingFileInfo','status':404,'data':encData}))
    
    def authenticationResponse(self,info):
        self.loop.create_task(self.authentication(info))
        
class sendFile:
    def __init__(self,reciverId,transactionId,BASE_DIR,IP):
        self.IP = IP
        self.transactionId = transactionId
        self.reciverId = reciverId
        self.BASE_DIR = BASE_DIR
        self.relayConnection = None
        self.loop = asyncio.get_event_loop()
        self.connectRelay()
    async def connectToRelay(self):
        try:
            url = f"wss://{self.IP}/ws/relay/sendFile/{self.transactionId}/{self.reciverId}/"
            self.relayConnection = await websockets.connect(url)
        except:
            print('error') ## change after development
            
    def connectRelay(self):
        self.loop.create_task(self.connectToRelay())
        
    async def sendFile(self,info):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        result = self.verifyUser(info)
        try:
            response = await asyncio.wait_for(self.relayConnection.recv(),timeout=2)
        except:
            response = None
        if result:
            filePath = result[0]
            enc = result[1]
            if response:
                result = json.loads(response)
                if result['status'] == 200:
                    
                    message = json.dumps({'message' : 'enc','enc':enc})
                    await self.relayConnection.send(message)
                    chunk_size = 512 * 1024 
                    with open(filePath, 'rb') as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            try:
                                await asyncio.wait_for(self.relayConnection.send(chunk),timeout=2)
                            except:
                                return
                    message = json.dumps({'message' : 'completed'})
                    await self.relayConnection.send(message)
            await self.relayConnection.close()
        else:
            message = json.dumps({'message' : 'invalid_data'})
            await self.relayConnection.send(message)
        
    def verifyUser(self,info):
        token = info['token']
        fileId = info['fileId']
        auth = jwtAuth(self.BASE_DIR)
        boxId = auth.decryptToken(token)
        if boxId:
            db = DataBase()
            fileData = db.getFileInfo(fileId)
            boxData = db.getDataOfBox(boxId)
            if boxData and fileData:
                if boxData[0] == fileData[-1]:
                    if boxData[3]:
                        path = os.path.join(self.BASE_DIR,f"files/encrypted/{fileData[1]}")
                    else:
                        path = os.path.join(self.BASE_DIR,f"files/non_encrypted/{fileData[1]}")
                    if os.path.exists(path):
                        return (path,boxData[3])
                        
            
        
    def passFile(self,info):
        self.loop.create_task(self.sendFile(info))
        
    
        

class RequestHandling:
    def __init__(self,userId,url,BASE_DIR,IP):
        self.IP = IP
        self.BASE_DIR = BASE_DIR
        self.url = url
        self.userId = userId
        self.relayConnection = None
        self.loop = asyncio.new_event_loop()
        self.recv_lock = asyncio.Lock()
        
    async def requestHandler(self):
        #while self.relayConnection is None:
        await asyncio.sleep(3)
        while self.relayConnection is not None:
            try:
                async with self.recv_lock:
                    request = await self.relayConnection.recv()
            except:
                self.relayConnection = None
                break
            if request:
                data = json.loads(request)
                if data['request'] == 'givePublicKey':
                    reviverId = data['reciverId']
                    sendPublicKey = subTask(reviverId,self.BASE_DIR,self.IP)
                    thread = threading.Thread(target=sendPublicKey.publicKey)
                    thread.start()
                elif data['request'] == 'authentication':
                    reviverId = data['reciverId']
                    encObj = passwordEncryptAndDecrypt(self.BASE_DIR)
                    info = encObj.decrypt_text(data['data'])
                    auth = subTask(reviverId,self.BASE_DIR,self.IP)
                    thread = threading.Thread(target=auth.authenticationResponse,args=(info,))
                    thread.start()
                elif data['request'] == 'giveFile':
                    reviverId = data['reciverId']
                    transactionId = data['transactionId']
                    clientInfo = data['clientInfo']
                    encObj = passwordEncryptAndDecrypt(self.BASE_DIR)
                    info = encObj.decrypt_text(clientInfo)
                    response = sendFile(transactionId=transactionId,reciverId=reviverId,BASE_DIR = self.BASE_DIR,IP = self.IP)
                    thread = threading.Thread(target=response.passFile,args=(info,),daemon=True).start()
                    
        self.loop.call_soon_threadsafe(self.loop.stop)
                    
                    
    def scanRequest(self):
        self.loop.create_task(self.requestHandler())
                    
    async def connectToRelay(self):
        try:
            self.relayConnection = await websockets.connect(self.url)
        except:
            print('error')
            ## change after development
            
    def connectRelay(self):
        self.loop.create_task(self.connectToRelay())
        
    def startScaning(self):
        asyncio.set_event_loop(self.loop)
        self.connectRelay()
        self.scanRequest()
        self.loop.run_forever()
    def startScaningThread(self):
        threading.Thread(target=self.startScaning, daemon=True).start()
        
class passwordEncryptAndDecrypt:
    def __init__(self,BASE_DIR):
        self.BASE_DIR = BASE_DIR
    def getPublicKey(self):
        public_key_path = os.path.join(self.BASE_DIR,'accessRelayServer/public_key.pem')
        with open(public_key_path, "rb") as pub_file:
            public_key = serialization.load_pem_public_key(pub_file.read())
        return public_key
    def getPrivateKey(self):
        private_key_path = os.path.join(self.BASE_DIR,'accessRelayServer/private_key.pem')
        with open(private_key_path, "rb") as priv_file:
            private_key = serialization.load_pem_private_key(
                priv_file.read(),
                password=None
            )
        return private_key
    def convetToText(self,public_key):
        pem_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return pem_bytes.decode('utf-8')
    
    def encrypt_json(self,data_dict, public_key):
        json_str = json.dumps(data_dict)  
        ciphertext = public_key.encrypt(
            json_str.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(ciphertext).decode('utf-8')
    
    def decrypt_text(self,ciphertext_base64):
        private_key = self.getPrivateKey()
        ciphertext = base64.b64decode(ciphertext_base64)
        try:
            decrypted_bytes = private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            json_str = decrypted_bytes.decode('utf-8')
            return json.loads(json_str)
        except:
            return False
        
        
        
class Request:
    def __init__(self,userId,BASE_DIR,Queue,IP):
        self.IP = IP
        self.Queue = Queue
        self.BASE_DIR = BASE_DIR
        self.userId = userId
        self.relayConnection = None
        self.loop = asyncio.new_event_loop()
        self.publicKeyData = None
    async def connectToRelay(self):
        try:
            url = f"wss://{self.IP}/ws/relay/request/{self.userId}/"
            self.relayConnection = await websockets.connect(url)
        except:
            self.relayConnection = 404
            print('error')
            
    def connectRelay(self):
        self.loop.create_task(self.connectToRelay())
        
    async def requestForPublicKey(self,userId):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        if self.relayConnection == 404:
            data = {'status':500}
            self.Queue.put(data)
            return
        data = {
            'request' : 'givePublicKey',
            'userId' : userId,
        }
        jsonData = json.dumps(data)
        await self.relayConnection.send(jsonData)
        try:
            publicKey = await asyncio.wait_for(self.relayConnection.recv(),timeout=2)
        except:
            publicKey = None
        if publicKey:
            key = json.loads(publicKey)
            if 'publicKey' in key:
                publicKeyData = key['publicKey']
                publicKeyData = serialization.load_pem_public_key(publicKeyData.encode('utf-8'))
                self.publicKeyData = publicKeyData
            else:
                self.publicKeyData = 404
        else:
            self.publicKeyData = 404
                
    # def publicKeyRequest(self,userId):
    #     self.loop.create_task(self.requestForPublicKey(userId))
        
    async def authentication(self,userId,boxId,password):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        if self.relayConnection == 404:
            data = {'status':500}
            self.Queue.put(data)
            return
        self.loop.create_task(self.requestForPublicKey(userId))
        while self.publicKeyData is None:
            await asyncio.sleep(0.1)
        if self.publicKeyData != 404:
            publicKey = self.publicKeyData
            data = {
                'boxId':boxId,
                'password':password,
            }
            encObj = passwordEncryptAndDecrypt(self.BASE_DIR)
            encrypt_data = encObj.encrypt_json(data_dict=data,public_key=publicKey)
            # userPublicKey = encObj.convetToText(encObj.getPublicKey())
            request = {
                'request' : 'authentication',
                'userId' : userId,
                'data' : encrypt_data,
            }
            jsonRequest = json.dumps(request)
            await self.relayConnection.send(jsonRequest)
            try:
                replay = await asyncio.wait_for(self.relayConnection.recv(),timeout=2)
            except:
                replay = None
            if replay:
                jsonData = json.loads(replay)
                if jsonData['status'] == 200:
                    data = jsonData['data']
                    data = base64.b64decode(data)
                    jsonDecrypt = JSONEncryptor(password=password)
                    jsonDecryptedData = jsonDecrypt.decrypt_json(data)
                    returnData = jsonDecryptedData['fileInfo']
                    token = jsonDecryptedData['jwtToken']
                    data = {'status':200,'replay':returnData,'publicKey':publicKey,'token':token}
                    self.Queue.put(data)
                else:
                    data = {'status':404}
                    self.Queue.put(data)
            else:
                data = {'status':404}
                self.Queue.put(data)
                # if jsonData['status'] == 200:
                #     info = encObj.decrypt_text(jsonData['data'])
                #     print(info)
        else:
            data = {'status':404}
            self.Queue.put(data)
            
        
        
    def authenticationRequest(self,userId,boxId,password):
        self.loop.create_task(self.authentication(userId,boxId,password))
        
    def loginRequest(self,userId,boxId,password):
        asyncio.set_event_loop(self.loop)
        self.connectRelay()
        self.authenticationRequest(userId,boxId,password)
        self.loop.run_forever()
        
    def loginRequestThread(self,userId,boxId,password):
        threading.Thread(target=self.loginRequest, daemon=True,args=(userId,boxId,password)).start()
        
        
    ## file request
        
    async def sendFileRequest(self,userId,token,fileId,fileName,password,downloadQ):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        if self.relayConnection == 404:
            data = {'status':500}
            self.Queue.put(data)
            return
        self.loop.create_task(self.requestForPublicKey(userId))
        while self.publicKeyData is None:
            await asyncio.sleep(0.1)
        if self.publicKeyData != 404:
            data = {
                'token' : token,
                'fileId' : fileId,
            }
            encObj = passwordEncryptAndDecrypt(self.BASE_DIR)
            encrypt_data = encObj.encrypt_json(data_dict=data,public_key=self.publicKeyData)
            request = {
                'fileRequest' : 'giveFile',
                'fileSenderId' : userId,
                'clientInfo' : encrypt_data,
            }
            jsonRequest = json.dumps(request)
            await self.relayConnection.send(jsonRequest)
            try:
                response = await asyncio.wait_for(self.relayConnection.recv(),timeout=2)
            except:
                response = None
            if response:
                jsonData = json.loads(response)
                if jsonData['status'] == 200:
                    data = {'status':200}
                    self.Queue.put(data)
                    try:
                        encMessage = await asyncio.wait_for(self.relayConnection.recv(),timeout=2)
                    except:
                        encMessage = None
                    if encMessage:
                        message = json.loads(encMessage)
                        complite = False
                        if 'enc' in message:
                            ## start reciving
                            enc = message['enc']
                            if enc:
                                path = os.path.join(self.BASE_DIR,f"files/temp/{fileName}")
                            else:
                                home_dir = Path.home()
                                downloads_dir = home_dir / 'Downloads'
                                path = os.path.join(downloads_dir,fileName)
                            total_bytes = 0
                            with open(path,'wb') as file:
                                time_elapsed = 0
                                while downloadQ.startDownloading:
                                    try:
                                        start_time = time.time()
                                        data = await asyncio.wait_for(self.relayConnection.recv(),timeout=5)
                                        end_time = time.time()
                                    except:
                                        break
                                    if isinstance(data, str):
                                        if data == "END":
                                            complite = True
                                            downloadQ.completed = True
                                            break
                                        elif json.loads(data)['message'] == 'closed':
                                            print('sender connection lost')
                                            return
                                            
                                    file.write(data)
                                    total_bytes += len(data)
                                    downloaded_mb = total_bytes / (1024 * 1024)
                                    time_elapsed += end_time - start_time
                                    download_speed = downloaded_mb / time_elapsed 
                                    downloadQ.speed = download_speed
                                    downloadQ.totalDownlaod = downloaded_mb
                                    # print(f"Downloaded: {downloaded_mb:.2f} MB", end='\r')
                                    # print(f"Download speed: {download_speed:.2f} MB/sec" , end='\r')
                            if complite and enc:
                                decrypt = Cryptography()
                                decrypt.decrypt_file(path,fileName,password)
                                os.remove(fileName)
                        else:
                            data = {'status':404}
                            self.Queue.put(data)
                            

            else:
                data = {'status':404}
                self.Queue.put(data)
                                    
                            
                    
                    
                    
            
    def sendFileRequestAwaited(self,userId,token,fileId,fileName,password,downloadQ):
        self.loop.create_task(self.sendFileRequest(userId,token,fileId,fileName,password,downloadQ))
        
    def fileRequest(self,userId,token,fileId,fileName,password,downloadQ):
        asyncio.set_event_loop(self.loop)
        self.connectRelay()
        self.sendFileRequestAwaited(userId,token,fileId,fileName,password,downloadQ)
        self.loop.run_forever()
        
    def fileRequestThread(self,userId,token,fileId,fileName,password,downloadQ):
        threading.Thread(target=self.fileRequest, daemon=True,args=(userId,token,fileId,fileName,password,downloadQ)).start()
        
        
        
        
# ch = input()
# if ch == '1':
#     obj = RequestHandling('User001')
#     obj.scanRequest()
# else:
#     obj = Request('User002')
#     obj.authenticationRequest('User001','music','Appu@1232')
    


# try:
#     obj.loop.run_forever()
# except KeyboardInterrupt:
#     print("Shutting down...")