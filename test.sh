#!/usr/bin/env bash
diff <(./among_us_stats.py testdata/playerStats2 | sort) <(cat testdata/playerStats2.txt | sort)
