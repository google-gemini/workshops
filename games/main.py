#!/usr/bin/env python
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl import app
from pettingzoo.classic import rps_v2
from play import make_ares, make_athena, play_game, plot_scores


def main(argv):
    env = rps_v2.env(render_mode="human", num_actions=3, max_cycles=25)
    players = {"player_0": make_ares(), "player_1": make_athena()}

    for game in range(1):
        play_game(game, env, players)

    plot_scores(players)


if __name__ == "__main__":
    app.run(main)
