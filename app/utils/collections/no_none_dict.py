class NoNoneDict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._wipe_none()

    def _wipe_none(self):
        keys = {k for k, v in self.items() if v is not None}
        for key in keys:
            self.pop(key)

    def __setitem__(self, k, v) -> None:
        if v is None:
            return
        return super().__setitem__(k, v)
