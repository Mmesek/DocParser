Examples of (preferable) output files

```json
"Log Structure": {
        "description": ["Structure Description"],
        "variables": [
            {
                "name": "webhooks",
                "is_list": true,
                "size": 0,
                "type": "Webhook",
                "description": "list of webhooks found in the audit log"
            },
            {
                "name": "user",
                "is_list": false,
                "size": 0,
                "type": "User",
                "description": "list of users found in the audit log"
            }
        ]
    },
"Log Events": {
        "description": ["Enum Description"],
        "variables": [
            {
                "name": "GUILD_UPDATE",
                "value": "1",
                "description":"some desc"
            },
            {
                "name": "CHANNEL_CREATE",
                "value": "10"
            },
            {
                "name": "CHANNEL_UPDATE",
                "value": "11"
            }
        ]
    },
"Endpoint Name": {
        "description": [
            "Description of an Endpoint"
        ],
        "method": "GET",
        "path": "/path/{param_id}/of/{endpoint_id}",
        "required_permission": ["SOME_PERMISSION"],
        "return": "Object",
        "return_list": false,
        "parameters": [
            "param_id",
            "endpoint_id"
        ],
        "query_params":[
            {
                "name": "query_param_name",
                "type": "string",
                "optional": false,
                "is_list": false,
                "size": 0,
                "description": "description of the parameter"
            }
        ],
        "json_params": [
            {
                "name": "param_name",
                "type": "type",
                "optional": true,
                "is_list": true,
                "size": 0,
                "description": "description of the json parameter"
            }
        ]
    }
```

```python
class Log(DiscordObject):
    """
    Structure Description
    Params:
        :webhooks: list of webhooks found in the audit log
        :user: list of users found in the audit log
    """
    webhooks: List[Webhook]
    user: List[User]
    def __init__(self, webhooks: List[Webhook], user: List[User]):
        self.webhooks = [Webhook(**i) for i in webhooks]
        self.users = [User(**i) for i in user]

class Log_Events(Enum):
    """
    Enum Description
    Params:
        :GUILD_UPDATE: some desc
    """
    GUILD_UPDATE = 1,
    CHANNEL_CREATE = 10,
    CHANNEL_UPDATE = 11

def Endpoint_Name(self, param_id, endpoint_id, query_param_name: str, param_name:type = []) -> Object:
    """
    Description of an Endpoint
    Params:
        :query_param_name: description of the parameter
        :param_name: description of the json parameter 
    """
    r = await self.api_call(
        path=f"/path/{param_id}/of/{endpoint_id}", 
        method="GET",
        params={"query_param_name":query_param_name}, 
        json={"param_name":param_name})
    return Object(r)
```