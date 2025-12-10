"""
Starter script for a NexusDojo kata.
"""


import random

def check_guess(secret: int, guess: int) -> str:
      if guess < secret:
          return "low"
      if guess > secret:
          return "high"
      return "correct"

def main() -> None:
      secret = random.randint(1, 100)
      attempts = 0
      print("Guess a number between 1 and 100. Type 'q' to quit.")
      while True:
          raw = input("Your guess: ").strip()
          if raw.lower() == "q":
              print(f"Bye! The number was {secret}.")
              return
          try:
              guess = int(raw)
          except ValueError:
              print("Please enter a whole number.")
              continue
          if not 1 <= guess <= 100:
              print("Keep it between 1 and 100.")
              continue
          attempts += 1
          result = check_guess(secret, guess)
          if result == "low":
              print("Higher.")
          elif result == "high":
              print("Lower.")
          else:
              print(f"Correct! {secret} in {attempts} tries.")
              return

if __name__ == "__main__":
      main()