import json
from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio

active_connections = {}
request_active_connections = {}

class ShearePublicKey(AsyncWebsocketConsumer):
    async def connect(self):
        self.userId = self.scope["url_route"]["kwargs"]['userId']
        await self.accept()
    
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            jsonData = json.loads(text_data)
            if jsonData['publicKey'] and self.userId in request_active_connections:
                reciver = request_active_connections[self.userId]
                await reciver.send(text_data)
            
                
                

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
            if 'request' in jsonData:
                if jsonData['request'] == 'givePublicKey':
                    senderUserId = jsonData['userId']
                    request = json.dumps({
                        'request':'givePublicKey',
                        'userId' : senderUserId,
                        'reciverId' : self.userId,
                    })
                    if senderUserId in active_connections:
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