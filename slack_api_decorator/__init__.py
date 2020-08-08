from .event_subscription import EventSubscription
from .slash_command import SlashCommand

# comparable tuple
VERSION = (0, 1, 0)
# generate __version__ via VERSION tuple
__version__ = ".".join(map(str, VERSION))
