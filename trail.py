from accessRelayServer import dataTransfer as acc
from pathlib import Path
acc.BASE_DIR = Path(__file__).resolve().parent
ch = input()
if ch == '1':
    obj = acc.RequestHandling('User001')
    obj.scanRequest()
else:
    obj = acc.Request('User002')
    obj.authenticationRequest('User001','photos','Appu@1232')
    


try:
    obj.loop.run_forever()
except KeyboardInterrupt:
    print("Shutting down...")