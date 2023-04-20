import csv
import re
import subprocess

from sortedcontainers import SortedSet

# Todo : clean and better organize save functions

COMMAND_GET_PACKAGE = ['/usr/bin/pamac', 'list']
COMMAND_GET_EXPLICIT_PACKAGE = ['/usr/bin/pamac', 'list', '-e']

PACKAGE_RE = re.compile(
    r'^(?P<name>[a-z0-9@._+\-]+)\s+'
    r'(?P<ver>[\d.a-z+:-]+)\s+'
    r'(?P<repo>[a-z]+)?\s*'
    r'(?P<size>[\d,]+\s(?:bytes?|[kmtg]B))?$',
    re.I | re.M
)


class Package:

    def __init__(self, name: str, ver: str, repo: str, size: str) -> None:
        self.name = name
        self.ver = ver
        self.repo = repo
        self.size = size

    @classmethod
    def from_match(cls, match: re.Match):
        return cls(
            name=match.group('name'),
            ver=match.group('ver'),
            repo=match.group('repo'),
            size=match.group('size')
        )

    def __repr__(self) -> str:
        return f'<Package: {self.name} | {self.ver} | {self.repo} | {self.size} >'

    def attrs(self):
        return self.name, self.ver, self.repo, self.size

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Package) and o.attrs() == self.attrs()

    def __hash__(self):
        return hash(self.attrs())


def get_packages(explicit: bool = False) -> SortedSet[Package]:
    # todo : add safety : check if pamac exist
    raw_package_list = subprocess.run(
        COMMAND_GET_EXPLICIT_PACKAGE if explicit else COMMAND_GET_PACKAGE,
        capture_output=True,
        text=True
    ).stdout.strip()

    # return {Package.from_match(m) for m in PACKAGE_RE.finditer(raw_package_list)}
    # We use map as a form of lambda iterator, same as above but sorted
    return SortedSet(
        map(Package.from_match, PACKAGE_RE.finditer(raw_package_list)),
        key=lambda package: package.name
    )


def save():
    print('Querying package list')
    packages = get_packages()
    explicit_packages = get_packages(explicit=True)

    print('Generating CSV output')
    csv_output = [
        ('name', 'version', 'repo', 'size', 'explicit'),
    ]

    package: Package
    for package in packages:
        csv_output.append((
            *package.attrs(),
            True if package in explicit_packages else False
        ))

    print('Writing CSV output')
    # todo : change file name based on current date
    # maybe add argparse for optional file renaming
    with open('out/result.csv', 'w') as csvfile:
        # todo : check if "out" folder exist, if not create, warning if not possible
        # maybe at start of script ? a precheck function ?
        csv.writer(csvfile).writerows(csv_output)

    print('Finished')


if __name__ == '__main__':
    save()
