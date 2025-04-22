import websockets
import asyncio
import json
import os
import bcrypt
import ssl
from cryptography.hazmat.primitives import serialization
import threading
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
from database.dataBase import DataBase
    
class subTask:
    def __init__(self,reciverId,BASE_DIR):
        self.BASE_DIR = BASE_DIR
        self.reciverId = reciverId
        self.relayConnection = None
        self.loop = asyncio.get_event_loop()
        self.connectRelay()
    async def connectToRelay(self):
        try:
            url = f"ws://127.0.0.1:8000/ws/relay/publicKey/{self.reciverId}/"
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
        
    async def authentication(self,info,publicKey):
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
                boxInfo = db.listAllFileByBoxId(boxInfo[0])
                data = {
                    'fileInfo' : boxInfo,
                }
                encObj = passwordEncryptAndDecrypt(self.BASE_DIR)
                publicKeyData = serialization.load_pem_public_key(publicKey.encode('utf-8'))
                encData = encObj.encrypt_json(data_dict=data,public_key=publicKeyData)
            await self.relayConnection.send(json.dumps({'response':'sharingFileInfo','status':status,'data':encData}))
    
    def authenticationResponse(self,info,publicKey):
        self.loop.create_task(self.authentication(info,publicKey))

class RequestHandling:
    def __init__(self,userId,url,BASE_DIR):
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
                    sendPublicKey = subTask(reviverId,self.BASE_DIR)
                    thread = threading.Thread(target=sendPublicKey.publicKey)
                    thread.start()
                elif data['request'] == 'authentication':
                    reviverId = data['reciverId']
                    publicKey = data['userPublicKey']
                    encObj = passwordEncryptAndDecrypt(self.BASE_DIR)
                    info = encObj.decrypt_text(data['data'])
                    auth = subTask(reviverId,self.BASE_DIR)
                    thread = threading.Thread(target=auth.authenticationResponse,args=(info,publicKey))
                    thread.start()
        self.loop.call_soon_threadsafe(self.loop.stop)
                    
                    
    def scanRequest(self):
        self.loop.create_task(self.requestHandler())
                    
    async def connectToRelay(self):
        try:
            self.relayConnection = await websockets.connect(self.url)
        except:
            pass ## change after development
            
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
    def __init__(self,userId,BASE_DIR,Queue):
        self.Queue = Queue
        self.BASE_DIR = BASE_DIR
        self.userId = userId
        self.relayConnection = None
        self.loop = asyncio.new_event_loop()
        self.publicKeyData = None
    async def connectToRelay(self):
        try:
            url = f"ws://127.0.0.1:8000/ws/relay/request/{self.userId}/"
            self.relayConnection = await websockets.connect(url)
        except:
            print('error') ## change after development
            
    def connectRelay(self):
        self.loop.create_task(self.connectToRelay())
        
    async def requestForPublicKey(self,userId):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        data = {
            'request' : 'givePublicKey',
            'userId' : userId,
        }
        jsonData = json.dumps(data)
        await self.relayConnection.send(jsonData)
        publicKey = await asyncio.wait_for(self.relayConnection.recv(),timeout=3)
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
            userPublicKey = encObj.convetToText(encObj.getPublicKey())
            request = {
                'request' : 'authentication',
                'userId' : userId,
                'data' : encrypt_data,
                'userPublicKey' : userPublicKey,
            }
            jsonRequest = json.dumps(request)
            await self.relayConnection.send(jsonRequest)
            replay = await asyncio.wait_for(self.relayConnection.recv(),timeout=3)
            if replay:
                jsonData = json.loads(replay)
                self.Queue.put(jsonData)
            else:
                data = {'status':404}
                self.Queue.put(data)
                # if jsonData['status'] == 200:
                #     info = encObj.decrypt_text(jsonData['data'])
                #     print(info)
        else:
            print('not fount')
            #declare the alert logic
        
        
    def authenticationRequest(self,userId,boxId,password):
        self.loop.create_task(self.authentication(userId,boxId,password))
        
    def loginRequest(self,userId,boxId,password):
        asyncio.set_event_loop(self.loop)
        self.connectRelay()
        self.authenticationRequest(userId,boxId,password)
        self.loop.run_forever()
    def loginRequestThread(self,userId,boxId,password):
        threading.Thread(target=self.loginRequest, daemon=True,args=(userId,boxId,password)).start()
        
        
        
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