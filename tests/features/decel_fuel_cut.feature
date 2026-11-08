# 仕様: docs/specs/decel_fuel_cut.md
Feature: 減速時燃料カット
  スロットル全閉で高回転のときに燃料をカットし、回転数が下がるか
  アクセルを踏むと復帰する。
  全閉 DECEL_THROTTLE_CLOSED_PCT = 2 %（以下）、カット開始 DECEL_CUT_ABOVE_RPM = 1500 rpm（超え）、
  復帰 DECEL_RECOVER_RPM = 1100 rpm（以下）。

  Background:
    Given ECUが初期化されている

  @代表動作
  Scenario: 減速で燃料カットし、回転数が下がると復帰する
    Given スロットル開度が "0 %" である
    And エンジン回転数が "3000 rpm" である
    When "10 ms" 経過する
    # 全閉かつ 1500 rpm 超えなのでカット
    Then 燃料カットが "ON" である
    # 1500 と 1100 の間では、カットを保つ
    When エンジン回転数が "1200 rpm" である
    And "10 ms" 経過する
    Then 燃料カットが "ON" である
    # 復帰 1100 rpm まで下がった
    When エンジン回転数が "1100 rpm" である
    And "10 ms" 経過する
    Then 燃料カットが "OFF" である

  Scenario Outline: カット開始条件（全閉 2 % 以下かつ 1500 rpm 超え）
    Given スロットル開度が "<throttle> %" である
    And エンジン回転数が "<rpm> rpm" である
    When "10 ms" 経過する
    Then 燃料カットが "<state>" である

    Examples:
      | throttle | rpm  | state | 備考                        |
      | 0        | 1500 | OFF   | 1500 ちょうどは超えていない |
      | 0        | 1501 | ON    | 1500 を超えた               |
      | 2        | 3000 | ON    | 全閉の上限 2 %              |
      | 3        | 3000 | OFF   | 2 % を超えると全閉でない    |

  Scenario Outline: カット中は 1100 rpm 以下になるまで継続する
    Given スロットル開度が "0 %" である
    And エンジン回転数が "3000 rpm" である
    When "10 ms" 経過する
    # カット中であることを先に確かめる
    Then 燃料カットが "ON" である
    When エンジン回転数が "<rpm> rpm" である
    And "10 ms" 経過する
    Then 燃料カットが "<state>" である

    Examples:
      | rpm  | state | 備考                  |
      | 1101 | ON    | 復帰 1100 の 1 rpm 上 |
      | 1100 | OFF   | 復帰ちょうど（以下）  |

  Scenario: スロットルが全閉(2 %)でなくなると復帰する
    Given スロットル開度が "0 %" である
    And エンジン回転数が "3000 rpm" である
    When "10 ms" 経過する
    # カット中であることを先に確かめる
    Then 燃料カットが "ON" である
    # 全閉 2 % を超えた
    When スロットル開度が "10 %" である
    And "10 ms" 経過する
    Then 燃料カットが "OFF" である

  Scenario Outline: カット中のスロットル全閉の境界（2 % 以下ならカットを保つ）
    Given スロットル開度が "0 %" である
    And エンジン回転数が "3000 rpm" である
    When "10 ms" 経過する
    # カット中であることを先に確かめる
    Then 燃料カットが "ON" である
    When スロットル開度が "<throttle> %" である
    And "10 ms" 経過する
    Then 燃料カットが "<state>" である

    Examples:
      | throttle | state | 備考                                |
      | 1        | ON    | 全閉のまま                          |
      | 2        | ON    | 全閉の上限 2 % ちょうどは復帰しない |
      | 3        | OFF   | 2 % を超えたので全閉でなく復帰      |
      | 4        | OFF   | 2 % を超えている                    |
