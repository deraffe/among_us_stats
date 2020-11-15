#!/usr/bin/env python3
import argparse
import logging
import struct
from dataclasses import asdict, astuple, dataclass, field

log = logging.getLogger(__name__)


@dataclass
class Stats:
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


@dataclass
class FancyStats(Stats):
    impostor_ratio: float = field(init=False)
    tasks_per_game: float = field(init=False)
    impostor_win_ratio: float = field(init=False)
    crewmate_win_ratio: float = field(init=False)
    task_completion_ratio: float = field(init=False)
    kills_per_game: float = field(init=False)
    murdered_per_game: float = field(init=False)
    impostor_lost: float = field(init=False)
    impostor_bias: float = field(init=False)
    crewmate_vote_win_ratio: float = field(init=False)
    untrustworthiness_ratio: float = field(init=False)
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
        self.task_completion_ratio = self.all_tasks_completed / self.times_crewmate
        self.kills_per_game = self.impostor_kills / self.times_impostor
        self.murdered_per_game = self.times_murdered / self.times_crewmate
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


def load_file(filename: str) -> bytes:
    with open(filename, 'rb') as fd:
        return fd.read()


def parse_stats(data: bytes) -> Stats:
    format = '<x18I76x'
    unpacked_data = struct.unpack(format, data)
    result = Stats(*unpacked_data)
    return result


def print_stats(stats: Stats) -> None:
    for name, value in asdict(stats).items():
        if type(value) == float:
            print('{}: {:.2f}'.format(name, value))
        else:
            print('{}: {}'.format(name, value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    parser.add_argument('statsfile', help='Filename of the playerStats2 file')
    parser.add_argument('--fancy', action='store_true', help='Fancy stats')
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)
    data = load_file(args.statsfile)
    stats = parse_stats(data)
    if not args.fancy:
        print_stats(stats)
    else:
        fancy_stats = FancyStats(*astuple(stats))
        print_stats(fancy_stats)


if __name__ == '__main__':
    main()
