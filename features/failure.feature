Feature: something


    @some.tag
    Scenario: Successful - Add <card_provider> card to an account consumer
        Given a http client

        When I access resource "/posts/"
        And I make POST request

        Then the status code should be "400"
