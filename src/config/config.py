from service.config import Config
from settings import BLOCK_CHAIN


def load_configs():
    """ load list of configs """
    data = [{
                "name": f"SERVICE_CHARGE_{BLOCK_CHAIN}",
                "value": "5"
            },
            {
                "name": "SERVICE_CHARGE_ALLEY",
                "value": "2.5"
            },
            {
                "name": "MAX_ROYALTY",
                "value": "30"
            },
            {
                "name": "DEFAULT_ROYALTY",
                "value": "1"
            }
        ]
    for config in data:
        Config().create_one(config)
