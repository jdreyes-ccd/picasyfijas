Feature: Multiplayer game service API
    Scenario: Create multiplayer game in waiting state
        Given player "Alice" creates a multiplayer game
        Then the multiplayer game should be in waiting status

    Scenario: Join multiplayer game
        Given player "Alice" has a waiting multiplayer game
        When player "Bob" joins that multiplayer game
        Then the multiplayer game should be in progress

    Scenario: Reject guess out of turn in multiplayer
        Given players "Alice" and "Bob" are in a multiplayer game
        When player 2 submits guess "1234" in multiplayer game
        Then the response status should be 400
        And the response detail should contain "No es tu turno"
