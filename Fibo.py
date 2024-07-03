# Define a function to find the nth Fibonacci number
def fibonacci(n):
  # Base cases: 0 and 1
  if n == 0:
    return 0
  elif n == 1:
    return 1
  # Recursive case: use the formula F(n) = F(n-1) + F(n-2)
  else:
    return fibonacci(n-1) + fibonacci(n-2)

# Ask the user for a positive integer
n = int(input("Enter a positive integer: "))

# Print the Fibonacci sequence up to the nth term
print("The Fibonacci sequence up to the", n, "th term is: \n")
for i in range(n):
  print(fibonacci(i), end=" ")