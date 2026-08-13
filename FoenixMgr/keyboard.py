"""Encode host keys as K2 optical-keyboard matrix snapshots."""

OPTICAL_SNAPSHOT_SIZE = 16

# These are the first 64 entries of the K2 microkernel key table. Each
# group of eight is a firmware state row. Hardware delivers the rows in reverse
# order and reverses the column bit numbering.
_OPTICAL_ASCII_INDEX = {
    "q": 1, " ": 3, "2": 4, "1": 7, "/": 8, "\t": 9, "'": 13,
    "]": 14, "=": 15, ",": 16, "[": 17, ";": 18, ".": 19, "l": 21,
    "p": 22, "-": 23, "n": 24, "o": 25, "k": 26, "m": 27, "0": 28,
    "j": 29, "i": 30, "9": 31, "v": 32, "u": 33, "h": 34, "b": 35,
    "8": 36, "g": 37, "y": 38, "7": 39, "x": 40, "t": 41, "f": 42,
    "c": 43, "6": 44, "d": 45, "r": 46, "5": 47, "e": 49, "s": 50,
    "z": 51, "4": 52, "a": 53, "w": 54, "3": 55, "\n": 62,
    "\r": 62,
}

_OPTICAL_NAMED_INDEX = {
    "run-stop": 0,
    "runstop": 0,
    "pause": 0,
    "break": 0,
    "backspace": 6,
    "tab": 9,
    "space": 3,
    "home": 12,
    "up": 56,
    "left": 61,
    "enter": 62,
}

_SHIFTED = {
    "!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6",
    "&": "7", "*": "8", "(": "9", ")": "0", "_": "-", "+": "=",
    "{": "[", "}": "]", ":": ";", '"': "'", "<": ",", ">": ".",
    "?": "/",
}

_OPTICAL_LEFT_SHIFT_INDEX = 48


def _empty_optical_snapshot():
    snapshot = bytearray(OPTICAL_SNAPSHOT_SIZE)
    for row in range(8):
        snapshot[row * 2] = row << 4
    return snapshot


def _set_optical_key(snapshot, table_index):
    state_row = table_index // 8
    column = 7 - (table_index % 8)
    hardware_row = 7 - state_row
    snapshot[hardware_row * 2] = hardware_row << 4
    snapshot[hardware_row * 2 + 1] |= 1 << column


def _optical_stroke(table_index, shift=False):
    if shift:
        shift_only = _empty_optical_snapshot()
        _set_optical_key(shift_only, _OPTICAL_LEFT_SHIFT_INDEX)

        pressed = bytearray(shift_only)
        _set_optical_key(pressed, table_index)

        # Shift shares a matrix row with E, S, Z, A, and W. The K2 firmware
        # scans those key bits before the Shift bit when both change in one
        # snapshot. Send the modifier transition separately, as a physical
        # keyboard would, so every shifted key sees Shift already held.
        return [
            bytes(shift_only),
            bytes(pressed),
            bytes(shift_only),
            bytes(_empty_optical_snapshot()),
        ]

    pressed = _empty_optical_snapshot()
    _set_optical_key(pressed, table_index)
    return [bytes(pressed), bytes(_empty_optical_snapshot())]


def encode_optical_character(character):
    """Return press and release snapshots for one printable character."""
    if len(character) != 1:
        raise ValueError("expected one character")

    shift = False
    if "A" <= character <= "Z":
        character = character.lower()
        shift = True
    elif character in _SHIFTED:
        character = _SHIFTED[character]
        shift = True

    try:
        table_index = _OPTICAL_ASCII_INDEX[character]
    except KeyError as error:
        raise ValueError(
            "character {!r} has no K2 optical-keyboard mapping".format(character)
        ) from error
    return _optical_stroke(table_index, shift)


def encode_optical_text(text):
    """Return optical press/release snapshots for every character in text."""
    snapshots = []
    for character in text:
        snapshots.extend(encode_optical_character(character))
    return snapshots


def encode_optical_key(name):
    """Return press and release snapshots for a named key or character."""
    table_index = _OPTICAL_NAMED_INDEX.get(name.lower())
    if table_index is not None:
        return _optical_stroke(table_index)
    if len(name) != 1:
        raise ValueError("unknown key {!r}".format(name))
    return encode_optical_character(name)
