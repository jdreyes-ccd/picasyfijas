Feature: Solo game service API
    Scenario: Create a solo game
        Given I am a player named "Ana"
        When I start a solo game
        Then the solo game should be created with 10 attempts

    Scenario: Reject invalid guess in solo game
        Given I started a solo game for "Ana"
        When I submit guess "123" in that solo game
        Then the response status should be 400

    Scenario: Get solo game status
        Given I started a solo game for "Ana"
        When I request the current game status
        Then the game status response should include the same game id
