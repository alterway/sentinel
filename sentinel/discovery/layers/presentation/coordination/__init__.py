from .discovery import Discovery


def _mangle_commands(*command_classes):
    out = {}
    for command_cls in command_classes:
        out[command_cls.name] = command_cls()
    return out


registry = _mangle_commands(Discovery)
