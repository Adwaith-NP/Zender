import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

active_connections = {}
request_active_connections = {}
filePass_active_connection = {} # reciverId : {fileId1 : self,fileId2 : self}
activateTransactions = []

class filePass(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver = None
        self.userId = self.scope["url_route"]["kwargs"]['userId']
        self.transactionId = self.scope["url_route"]["kwargs"]['transactionId']
        if self.userId and self.transactionId:
            await self.accept()
            if self.userId in filePass_active_connection:
                transactions = filePass_active_connection[self.userId]
                if self.transactionId in transactions:
                    await self.send(json.dumps({'status' : 200}))
                    self.receiver = transactions[self.transactionId]
                else:
                    await self.send(json.dumps({'status' : 404}))
            else:
                await self.send(json.dumps({'status' : 405}))
                
    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data and self.receiver and self.transactionId in activateTransactions:
            await self.receiver.send(bytes_data = bytes_data)
            await asyncio.sleep(0)
        if text_data:
            data = json.loads(text_data)
            if 'message' in data:
                if data['message'] == 'completed':
                    await self.receiver.send("END")
                    activateTransactions.remove(self.transactionId)
                elif data['message'] == 'enc':
                    await self.receiver.send(text_data)
    async def disconnect(self, close_code):
        if self.receiver:
            await self.receiver.send(json.dumps({'message' : 'closed'}))
            if self.transactionId in activateTransactions:
                activateTransactions.remove(self.transactionId)
                
            

class subTask(AsyncWebsocketConsumer):
    async def connect(self):
        self.userId = self.scope["url_route"]["kwargs"]['userId']
        await self.accept()
    
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            jsonData = json.loads(text_data)
            if 'response' in jsonData and self.userId in request_active_connections:
                reciver = request_active_connections[self.userId]
                if jsonData['response'] == 'sendingPublicKey':
                    await reciver.send(text_data)
                elif jsonData['response'] == 'sharingFileInfo':
                    await reciver.send(text_data)
            else:
                await self.send(json.dumps({'status':404}))
    
                
                
                

class RelayConsumerConnections(AsyncWebsocketConsumer):
    async def connect(self):
        self.userId = self.scope["url_route"]["kwargs"]['userId']
        await self.accept()
        active_connections[self.userId] = self
    async def receive(self, text_data=None, bytes_data=None):
        pass
    
    async def disconnect(self, close_code):
        if self.userId in active_connections:
            del active_connections[self.userId]
            
class OneTimeRequest(AsyncWebsocketConsumer):
    def createTransactionId(self):
        if not activateTransactions:
            number = '10000001'
            activateTransactions.append(number)
        else:
            number = str((int(activateTransactions[-1]))+1)
        return number
    
    async def connect(self):
        self.userId = self.scope["url_route"]["kwargs"]['userId']
        await self.accept()
        
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            jsonData = json.loads(text_data)
            request = None
            if 'request' in jsonData:
                if jsonData['request'] == 'givePublicKey':
                    senderUserId = jsonData['userId']
                    request = json.dumps({
                        'request':'givePublicKey',
                        'reciverId' : self.userId,
                    })
                elif jsonData['request'] == 'authentication':
                    senderUserId = jsonData['userId']
                    request = json.dumps({
                        'request':'authentication',
                        'data' : jsonData['data'],
                        'reciverId' : self.userId,
                    })
                if senderUserId in active_connections and request:
                        request_active_connections[self.userId] = self
                        await active_connections[senderUserId].send(request)
                else:
                    message = json.dumps({'status':404})
                    await self.send(message)
            elif 'fileRequest' in jsonData:
                if jsonData['fileRequest'] == 'giveFile':
                    fileSenderId = jsonData['fileSenderId']
                    clientInfo = jsonData['clientInfo']
                    transactionId = self.createTransactionId()
                    
                    jsonRequest = json.dumps(
                        {
                            'request' : 'giveFile',
                            'clientInfo' : clientInfo,
                            'transactionId' : transactionId,
                            'reciverId' : self.userId,
                        }
                    )
                    if fileSenderId in active_connections:
                        activateTransactions.append(transactionId)
                        if self.userId not in filePass_active_connection:
                            filePass_active_connection[self.userId] = {}
                        filePass_active_connection[self.userId][transactionId] = self
                        
                        await active_connections[fileSenderId].send(jsonRequest)
                        message = json.dumps({'status':200})
                        await self.send(message)
                    else:
                        message = json.dumps({'status':404})
                        await self.send(message)
                    
    
    async def disconnect(self, close_code):
        if self.userId in request_active_connections:
            del request_active_connections[self.userId]