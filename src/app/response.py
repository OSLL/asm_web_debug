from datetime import datetime


class Response(dict):
  
  def __init__(self, **kwargs):
    super().__init__(**kwargs,
                        timestamp=datetime.utcnow().timestamp())
