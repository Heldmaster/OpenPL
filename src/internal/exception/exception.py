
class ApplicationError(Exception):
    pass

class MavlinkConnectionError(ApplicationError):
    pass

class CameraError(ApplicationError):
    pass
