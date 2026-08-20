"""Minimal Praat TextGrid reader and writer (interval tiers only).

Handles both the long and short TextGrid formats, and both UTF-8 and UTF-16
files, since Praat picks the encoding depending on what characters the labels
contain and these labels are IPA.
"""


class Interval:
    __slots__ = ("xmin", "xmax", "text")

    def __init__(self, xmin, xmax, text):
        self.xmin = xmin
        self.xmax = xmax
        self.text = text

    @property
    def duration(self):
        return self.xmax - self.xmin

    @property
    def midpoint(self):
        return 0.5 * (self.xmin + self.xmax)

    def __repr__(self):
        return f"Interval({self.xmin:.4f}, {self.xmax:.4f}, {self.text!r})"


class Tier:
    def __init__(self, name, xmin, xmax, intervals=None):
        self.name = name
        self.xmin = xmin
        self.xmax = xmax
        self.intervals = intervals if intervals is not None else []

    def labelled(self, skip=("", "sil", "sp")):
        return [iv for iv in self.intervals if iv.text.strip() not in skip]

    def __len__(self):
        return len(self.intervals)

    def __iter__(self):
        return iter(self.intervals)


class TextGrid:
    def __init__(self, xmin=0.0, xmax=0.0, tiers=None):
        self.xmin = xmin
        self.xmax = xmax
        self.tiers = tiers if tiers is not None else []

    def __getitem__(self, name):
        for t in self.tiers:
            if t.name == name:
                return t
        raise KeyError(f"no tier named {name!r}; have {[t.name for t in self.tiers]}")

    def names(self):
        return [t.name for t in self.tiers]


def _decode(path):
    raw = open(path, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig")


def _tokens(text):
    """Values in document order: quoted strings as str, bare numbers as float."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "=" in line:
            line = line.split("=", 1)[1].strip()
        if line.startswith('"'):
            # labels may contain doubled quotes as Praat's escape
            out.append(line[1:line.rindex('"')].replace('""', '"'))
            continue
        try:
            out.append(float(line))
        except ValueError:
            pass  # structural lines such as 'item [1]:' or '<exists>'
    return out


def read_textgrid(path):
    tok = _tokens(_decode(path))
    i = 0
    if isinstance(tok[i], str):  # "ooTextFile"
        i += 1
    if isinstance(tok[i], str):  # "TextGrid"
        i += 1
    xmin, xmax, n_tiers = tok[i], tok[i + 1], int(tok[i + 2])
    i += 3

    grid = TextGrid(xmin, xmax)
    for _ in range(n_tiers):
        cls, name, t_min, t_max = tok[i], tok[i + 1], tok[i + 2], tok[i + 3]
        n = int(tok[i + 4])
        i += 5
        if cls != "IntervalTier":
            raise ValueError(f"tier {name!r} is a {cls}, only IntervalTier is supported")
        tier = Tier(name, t_min, t_max)
        for _ in range(n):
            tier.intervals.append(Interval(tok[i], tok[i + 1], tok[i + 2]))
            i += 3
        grid.tiers.append(tier)
    return grid


def _esc(s):
    return s.replace('"', '""')


def write_textgrid(grid, path):
    lines = [
        'File type = "ooTextFile"',
        'Object class = "TextGrid"',
        "",
        f"xmin = {grid.xmin} ",
        f"xmax = {grid.xmax} ",
        "tiers? <exists> ",
        f"size = {len(grid.tiers)} ",
        "item []: ",
    ]
    for ti, tier in enumerate(grid.tiers, start=1):
        lines += [
            f"    item [{ti}]:",
            '        class = "IntervalTier" ',
            f'        name = "{_esc(tier.name)}" ',
            f"        xmin = {tier.xmin} ",
            f"        xmax = {tier.xmax} ",
            f"        intervals: size = {len(tier.intervals)} ",
        ]
        for ii, iv in enumerate(tier.intervals, start=1):
            lines += [
                f"        intervals [{ii}]:",
                f"            xmin = {iv.xmin} ",
                f"            xmax = {iv.xmax} ",
                f'            text = "{_esc(iv.text)}" ',
            ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def evenly_spaced(name, labels, xmin, xmax):
    """A tier with the labels in order and boundaries at equal spacing."""
    n = len(labels)
    step = (xmax - xmin) / n
    tier = Tier(name, xmin, xmax)
    for k, lab in enumerate(labels):
        a = xmin + k * step
        b = xmax if k == n - 1 else xmin + (k + 1) * step
        tier.intervals.append(Interval(a, b, lab))
    return tier
