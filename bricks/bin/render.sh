#!/usr/bin/env bash
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

./lib/l2cu/l2cu -d $PWD/var/rendered -r 7 -f mpd
for png in var/rendered/renders/*.png; do
  base="$(basename "${png}")"
  mv -v "${png}" "var/rendered/${base/-07.png/.png}"
done
