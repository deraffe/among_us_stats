#!/usr/bin/env python3
import argparse
import dataclasses
import logging
import struct

log = logging.getLogger(__name__)


@dataclasses.dataclass
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


def load_file(filename: str) -> bytes:
    with open(filename, 'rb') as fd:
        return fd.read()


def parse_stats(data: bytes) -> Stats:
    format = '<x18I76x'
    unpacked_data = struct.unpack(format, data)
    result = Stats(*unpacked_data)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    parser.add_argument('statsfile', help='Filename of the playerStats2 file')
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)
    data = load_file(args.statsfile)
    stats = parse_stats(data)
    print(stats)


if __name__ == '__main__':
    main()
