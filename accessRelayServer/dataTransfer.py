import websockets
import asyncio
import json
import ssl
from cryptography.hazmat.primitives import serialization
import threading
    
    
    
class SendPublicKey:
    def __init__(self,reciverId):
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
        with open('public_key.pem', "rb") as pub_file:
            public_key = serialization.load_pem_public_key(pub_file.read())
        pem_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)

        return pem_bytes.decode('utf-8')
    
    async def shearPublicKey(self):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        publicKey = self.getPublicKey()
        jsonData = json.dumps({'publicKey':publicKey})
        await self.relayConnection.send(jsonData)
        
    def publicKey(self):
        self.loop.create_task(self.shearPublicKey())

class RequestHandling:
    def __init__(self,userId):
        self.userId = userId
        self.relayConnection = None
        self.loop = asyncio.get_event_loop()
        self.recv_lock = asyncio.Lock()
        self.connectRelay()
        self.scanRequest()
    async def requestHandler(self):
        while self.relayConnection is None:
            await asyncio.sleep(0.1)
        while True:
            async with self.recv_lock:
                request = await self.relayConnection.recv()
            if request:
                data = json.loads(request)
                if data['request'] == 'givePublicKey':
                    reviverId = data['reciverId']
                    sendPublicKey = SendPublicKey(reviverId)
                    thread = threading.Thread(target=sendPublicKey.publicKey)
                    thread.start()
                    
                    
    def scanRequest(self):
        self.loop.create_task(self.requestHandler())
                    
    async def connectToRelay(self):
        try:
            url = f"ws://127.0.0.1:8000/ws/relay/{self.userId}/"
            self.relayConnection = await websockets.connect(url)
        except:
            print('error') ## change after development
            
    def connectRelay(self):
        self.loop.create_task(self.connectToRelay())
        
class Request:
    def __init__(self,userId):
        self.userId = userId
        self.relayConnection = None
        self.loop = asyncio.get_event_loop()
        self.connectRelay()
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
        publicKey = await self.relayConnection.recv()
        if publicKey:
            key = json.loads(publicKey)
            if 'publicKey' in key:
                print(key['publicKey'])
                
    def publicKeyRequest(self,userId):
        self.loop.create_task(self.requestForPublicKey(userId))
        
ch = input()
if ch == '1':
    obj = RequestHandling('User001')
    obj.scanRequest()
else:
    obj = Request('User002')
    obj.publicKeyRequest('User001')
    


try:
    obj.loop.run_forever()
except KeyboardInterrupt:
    print("Shutting down...")