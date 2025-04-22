import json
from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio

active_connections = {}
request_active_connections = {}

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
                        'userPublicKey' : jsonData['userPublicKey'],
                        'reciverId' : self.userId,
                    })
                if senderUserId in active_connections and request:
                        request_active_connections[self.userId] = self
                        await active_connections[senderUserId].send(request)
                else:
                    message = json.dumps({'status':404})
                    await self.send(message)
                    
            else:
                message = json.dumps({'status':404})
                await self.send(message)
    
    async def disconnect(self, close_code):
        if self.userId in request_active_connections:
            del request_active_connections[self.userId]