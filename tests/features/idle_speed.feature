# 仕様: docs/specs/idle_speed.md
Feature: アイドル回転数制御
  水温に応じて目標アイドル回転数を決める。
  20 ℃ 未満は 1200 rpm、20 ℃ 以上 60 ℃ 未満は 1000 rpm、60 ℃ 以上は 750 rpm。

  Background:
    Given ECUが初期化されている

  Scenario Outline: 水温から目標アイドル回転数が決まる
    Given 水温が "<temp> ℃" である
    When "10 ms" 経過する
    Then 目標アイドル回転数が "<idle> rpm" である

    Examples:
      | temp | idle | 備考                  |
      | -10  | 1200 | 冷間(20 ℃ 未満)       |
      | 19   | 1200 | 冷間の上限            |
      | 20   | 1000 | 20 ℃ ちょうどは中間   |
      | 59   | 1000 | 中間の上限            |
      | 60   | 750  | 60 ℃ ちょうどは暖機後 |
      | 90   | 750  | 暖機後                |
