# it is a multiplayer game of rolling dice 1 - 6

import random

def roll(): #defined my function
    min_value = 1
    max_value = 6
    roll = random.randint(min_value, max_value)

    return roll

while True: #takes the number of players going to play
    players = input("Enter the number of players (1-4): ")
    if players.isdigit():
        players =int(players)
        if 2 <= players <=4:
            break
        else:
            print("Must be between 2 -4 players")
    else:
        print("Invalid try again")

max_score = 50
player_scores = [0 for _ in range(players)] #This is a list comprehension(it puts a zero for every single player we have )


while max(player_scores) < max_score:#This simulates the terms

    for player_index in range(players): #looping over all of our different players
        print("\nPlayer number", player_index + 1 , "turn has just started\n")
        current_score = 0

        while True: #simulating the role
            should_roll = input("Would you like to roll (y/n)? ")
            if should_roll.lower() != "y":
                break

            value = roll()
            if value == 1:
                print("You rolled a 1! Turn done")
                current_score = 0
            else:
                current_score += value
                print("You rolled a: ", value)

            print("Your score is: ", current_score)

        player_scores[player_index] += current_score
        print("Your total score is: ",player_scores[player_index])


