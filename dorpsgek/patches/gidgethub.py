import logging

from gidgethub import routing

log = logging.getLogger(__name__)


# The dispatch function of gidgethub does almost exactly what you would like.
# The only issue is that when there is an exception in the callback, no other
# callbacks are called. This is not wanted behaviour, as all callbacks are
# independent of each other.
async def dispatch(self, event, *args, **kwargs):
    """Dispatch an event to all registered function(s)."""

    found_callbacks = []
    try:
        found_callbacks.extend(self._shallow_routes[event.event])
    except KeyError:
        pass
    try:
        details = self._deep_routes[event.event]
    except KeyError:
        pass
    else:
        for data_key, data_values in details.items():
            if data_key in event.data:
                event_value = event.data[data_key]
                if event_value in data_values:
                    found_callbacks.extend(data_values[event_value])
    for callback in found_callbacks:
        try:
            await callback(event, *args, **kwargs)
        except Exception:
            log.exception("GitHub callback failed")


routing.Router.dispatch = dispatch  # noqa
