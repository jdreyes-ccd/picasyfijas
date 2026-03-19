Feature: Number validation API
    Scenario Outline: Validate number format rules
        Given I have a number <number>
        When I validate the number
        Then the result should be <result>

        Examples:
            | number | result |
            | 1234   | true   |
            | 5678   | true   |
            | 9012   | true   |
            | 1123   | false  |
            | 12a4   | false  |
            | 123    | false  |
            | 12345  | false  |
          
