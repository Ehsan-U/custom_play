import asyncio
from proxybroker import Broker
from random import choice

class Myproxies():
    def __init__(self):
        self.proxie = list()
        self.proxies = asyncio.Queue()
        self.broker = Broker(self.proxies)
        
    def setupp(self):
        tasks = asyncio.gather(
        self.broker.find(types=['HTTPS'], limit=5),
        self.show(self.proxies))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)

    async def show(self,proxies):
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            else:
                await self.send(proxy)
    async def send(self,proxy):
        self.proxie.append(f"{proxy.host}:{proxy.port}")

p = Myproxies()
p.setupp()
for p in p.proxie:
    print(p)