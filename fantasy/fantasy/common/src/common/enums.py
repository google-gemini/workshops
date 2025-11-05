"""Enums for fantasy sports.

This file contains enumerations for fantasy sports, such as player positions and
team names.
"""

import enum

Enum = enum.Enum


class Positions(str, Enum):
  QB = "QB"
  RB = "RB"
  WR = "WR"
  TE = "TE"
  K = "K"


class Teams(str, Enum):
  """Enum for NFL team abbreviations.

  Must match the abbreviations in the Sleeper API.
  """

  ARI = "ARI"
  ATL = "ATL"
  BAL = "BAL"
  BUF = "BUF"
  CAR = "CAR"
  CHI = "CHI"
  CIN = "CIN"
  CLE = "CLE"
  DAL = "DAL"
  DEN = "DEN"
  DET = "DET"
  GB = "GB"
  HOU = "HOU"
  IND = "IND"
  JAX = "JAX"
  KC = "KC"
  LV = "LV"
  LAC = "LAC"
  LAR = "LAR"
  MIA = "MIA"
  MIN = "MIN"
  NE = "NE"
  NO = "NO"
  NYG = "NYG"
  NYJ = "NYJ"
  PHI = "PHI"
  PIT = "PIT"
  SF = "SF"
  SEA = "SEA"
  TB = "TB"
  TEN = "TEN"
  WAS = "WAS"


class SoundEffects(str, Enum):
  """Enum for sound effects used in fantasy football."""

  INTRO = "intro"
  APPLAUSE = "applause"
  BOO = "boo"
  GASP = "gasp"
  CHIME = "chime"
