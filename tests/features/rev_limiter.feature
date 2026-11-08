# 仕様: docs/specs/rev_limiter.md
Feature: レブリミッタ
  エンジン回転数が上限に達したら燃料をカットし、下限まで下がったら復帰する。
  上限 REV_LIMIT_RPM = 6500 rpm（以上でカット）、復帰 REV_RECOVER_RPM = 6300 rpm（以下で復帰）。

  Background:
    Given ECUが初期化されている
    And スロットル開度が "50 %" である

  @代表動作
  Scenario: 上限 6500 rpm でカットし、復帰 6300 rpm まで下がると復帰する
    Given エンジン回転数が "6000 rpm" である
    When "10 ms" 経過する
    Then 燃料カットが "OFF" である
    # 上限 6500 rpm に達した
    When エンジン回転数が "6500 rpm" である
    And "10 ms" 経過する
    Then 燃料カットが "ON" である
    # 上限と復帰の間では、カットを保つ
    When エンジン回転数が "6400 rpm" である
    And "10 ms" 経過する
    Then 燃料カットが "ON" である
    # 復帰 6300 rpm まで下がった
    When エンジン回転数が "6300 rpm" である
    And "10 ms" 経過する
    Then 燃料カットが "OFF" である

  Scenario Outline: カット開始は 6500 rpm 以上
    Given エンジン回転数が "<rpm> rpm" である
    When "10 ms" 経過する
    Then 燃料カットが "<state>" である

    Examples:
      | rpm  | state | 備考                    |
      | 6499 | OFF   | 上限 6500 の 1 rpm 手前 |
      | 6500 | ON    | 上限ちょうど（以上）    |

  Scenario Outline: カット中は 6300 rpm 以下になるまで継続する
    Given エンジン回転数が "7000 rpm" である
    When "10 ms" 経過する
    And エンジン回転数が "<rpm> rpm" である
    And "10 ms" 経過する
    Then 燃料カットが "<state>" である

    Examples:
      | rpm  | state | 備考                  |
      | 6301 | ON    | 復帰 6300 の 1 rpm 上 |
      | 6300 | OFF   | 復帰ちょうど（以下）  |
