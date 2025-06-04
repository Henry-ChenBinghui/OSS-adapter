from llm.factory import get_provider_pool
from llm.balancer.load_balancer import RoundRobinBalancer

class MultiCloudRouter:
    def __init__(self):
        self.providers = get_provider_pool()
        self.cloud_balancer = RoundRobinBalancer()
        self.inner_balancers = {
            cloud: RoundRobinBalancer()
            for cloud in self.providers
        }

    async def route(self, method: str, **kwargs):
        cloud_name = self.cloud_balancer.select("cloud", list(self.providers.keys()))
        instance = self.inner_balancers[cloud_name].select("provider", self.providers[cloud_name])
        func = getattr(instance, method)
        return await func(**kwargs)
