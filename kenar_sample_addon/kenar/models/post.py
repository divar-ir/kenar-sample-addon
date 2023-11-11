class Post:
    def __init__(self, post_dict):
        self.post_dict = post_dict

    @property
    def city(self) -> str:
        return self.post_dict.get("city")

    @property
    def token(self) -> str:
        return self.post_dict.get("token")

    @property
    def category(self) -> str:
        return self.post_dict.get("category")

    @property
    def data(self):
        return self.post_dict.get("data")
