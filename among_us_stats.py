#!/usr/bin/env python3
import argparse
import logging
import pathlib
import struct
from dataclasses import asdict, astuple, dataclass, field, fields

log = logging.getLogger(__name__)


@dataclass
class Stats:
    verbosity: int = field(repr=False)
    bodies_reported: int
    emergencies_called: int
    tasks_completed: int
    all_tasks_completed: int
    sabotages_fixed: int
    impostor_kills: int
    times_murdered: int
    times_ejected: int
    crewmate_streak: int
    times_impostor: int
    times_crewmate: int
    games_started: int
    games_finished: int
    crewmate_vote_wins: int
    crewmate_task_wins: int
    impostor_vote_wins: int
    impostor_kill_wins: int
    impostor_sabotage_wins: int
    win_array: bytes = field(repr=False)
    lose_array: bytes = field(repr=False)
    tie_array: bytes = field(repr=False)
    ban_points: float = field(repr=False)
    last_game: bytes = field(repr=False)


@dataclass
class FancyStats(Stats):
    impostor_ratio: float = field(init=False)
    tasks_per_game: float = field(init=False)
    impostor_win_ratio: float = field(init=False)
    crewmate_win_ratio: float = field(init=False)
    sabotages_fixed_per_game: float = field(init=False)
    task_completion_ratio: float = field(init=False)
    kills_per_game: float = field(init=False)
    murdered_per_game: float = field(init=False)
    kill_death_ratio: float = field(init=False)
    impostor_lost: float = field(init=False, repr=False)
    impostor_bias: float = field(init=False)
    crewmate_vote_win_ratio: float = field(init=False, repr=False)
    untrustworthiness_ratio: float = field(init=False, repr=False)
    untrustworthiness_index: float = field(init=False)

    def __post_init__(self):
        self.impostor_ratio = self.times_impostor / self.games_started
        self.tasks_per_game = self.tasks_completed / self.times_crewmate
        self.impostor_win_ratio = (
            self.impostor_vote_wins + self.impostor_kill_wins +
            self.impostor_sabotage_wins
        ) / self.times_impostor
        self.crewmate_win_ratio = (
            self.crewmate_vote_wins + self.crewmate_task_wins
        ) / self.times_crewmate
        # yes, impostors can also fix - but if you do that, it should count extra towards your crewmate bonuses
        self.sabotages_fixed_per_game = self.sabotages_fixed / self.times_crewmate
        self.task_completion_ratio = self.all_tasks_completed / self.times_crewmate
        self.kills_per_game = self.impostor_kills / self.times_impostor
        self.murdered_per_game = self.times_murdered / self.times_crewmate
        self.kill_death_ratio = self.impostor_kills / (
            self.times_murdered + self.times_ejected
        )
        self.impostor_lost = (
            self.times_impostor -
            (self.impostor_vote_wins + self.impostor_kill_wins)
        )
        self.impostor_bias = self.impostor_ratio - (((1 / 7) + (2 / 10)) / 2)
        self.crewmate_vote_win_ratio = self.crewmate_vote_wins / (
            self.crewmate_task_wins + self.crewmate_vote_wins
        )
        self.untrustworthiness_ratio = (
            self.times_ejected -
            (self.impostor_lost * self.crewmate_vote_win_ratio)
        ) / self.times_crewmate
        self.untrustworthiness_index = self.untrustworthiness_ratio + max(
            self.impostor_bias, 0
        )


def load_stats(filename: str) -> Stats:
    format = '<B18I8s28s28sf8s'
    with open(filename, 'rb') as fd:
        unpacked_data = struct.unpack(format, fd.read())
    return Stats(*unpacked_data)


def print_stats(stats: Stats, print_hidden=False) -> None:
    hidden_fields = [f.name for f in fields(stats) if not f.repr]
    for name, value in asdict(stats).items():
        if name in hidden_fields and not print_hidden:
            continue
        if type(value) == float:
            print('{}: {:.2f}'.format(name, value))
        else:
            print('{}: {}'.format(name, value))


def try_finding_statsfile() -> str:
    appdata_path = 'AppData/LocalLow/Innersloth/Among Us/playerStats2'
    possible_paths = (
        pathlib.Path.home() / appdata_path,
        pathlib.Path(
            '~/.local/share/Steam/steamapps/compatdata/945360/pfx/drive_c/users/steamuser'
        ) / appdata_path,
    )
    for path in possible_paths:
        expanded_path = path.expanduser()
        log.debug('Trying {}'.format(expanded_path))
        if expanded_path.exists():
            return str(expanded_path)
    raise ValueError('Cannot find the playerStats2 file')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    parser.add_argument(
        'statsfile', nargs='?', help='Filename of the playerStats2 file'
    )
    parser.add_argument('--fancy', action='store_true', help='Fancy stats')
    parser.add_argument(
        '--hidden', action='store_true', help='Print hidden fields'
    )
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)
    if args.statsfile is None:
        statsfile = try_finding_statsfile()
    else:
        statsfile = args.statsfile
    stats = load_stats(statsfile)
    if not args.fancy:
        print_stats(stats, args.hidden)
    else:
        fancy_stats = FancyStats(*astuple(stats))
        print_stats(fancy_stats, args.hidden)


if __name__ == '__main__':
    main()
