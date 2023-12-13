name = input("Type your name:")
print("Welcome", name, "to this adventure")

answer = input(
	"You are on a dirt road, it has come to an end and you can go left or right. Which way would you like to go?").lower()

if answer == "left":
	answer = input("You come to a river , you can walk around it or swim across?")

	if answer == "swim":
		print("You swim across and you are eaten by a crocodile")
	elif answer == "walk":
		print("You walked for many kilometres , ran out of water and you lost the gane")
	else:
		print("Not a valid option . You lose.")

elif answer == "right":
	answer = input("You come to a broken bridge, do you want to cross it or head back (cross/back)?")
	if answer == "back":
		print("You go back and lose the game")
	elif answer == "cross":
		answer = input("You cross the bridge carefully and meet a stranger. Do you talk to them (yes/no)?")

		if answer == "yes":
			print (" You talk to the stranger and he gifts you gold ")

		elif answer == "no":
			print("You ignore the stranger and you continue crossing the brodge and fall to the river and get eaten by crocodiles")

		else:
			print("not a valid option. You lose.")

	else:
		print("Not a valid option . You lose.")

else:
	print("not a valid option. You lose.")

print("Thank you for trying", name)