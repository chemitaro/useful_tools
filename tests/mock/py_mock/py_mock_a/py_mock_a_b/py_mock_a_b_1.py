py_mock_a_b_1 = 'py_mock_a_b_1'

# Define variables
variable1 = "This"
variable2 = "is"
variable3 = "a"
variable4 = "dummy"
variable5 = "code"

# Combine variables
combined_text = " ".join([variable1, variable2, variable3, variable4, variable5])

# Print the combined text
print(combined_text)

# Reverse the combined text
reversed_text = combined_text[::-1]

# Print the reversed text
print(reversed_text)

# Loop through each character in the combined text
for character in combined_text:
    print(character)

# Convert the combined text to uppercase and print it
print(combined_text.upper())

# Check if "code" is in the combined text
is_code = "code" in combined_text

# Print the result
print(f"Is 'code' in the text: {is_code}")

# Define lists
list1 = ["This", "is", "a", "dummy", "code"]
list2 = [1, 2, 3, 4, 5]

# Combine the lists
combined_list = list1 + list2

# Print the combined list
print(combined_list)

# Loop through the combined list and print its elements
for element in combined_list:
    print(element)

# Sort the combined list and print it
sorted_list = sorted(combined_list)
print(sorted_list)

# Reverse the sorted list and print it
reversed_list = sorted_list[::-1]
print(reversed_list)

# Define strings
string1 = "This is a dummy string."
string2 = "This is another dummy string."

# Concatenate the strings
combined_string = string1 + " " + string2

# Print the combined string
print(combined_string)

# Split the combined string into words and print them
words = combined_string.split()
print(words)

# Count the number of words in the combined string
word_count = len(words)

# Print the word count
print(f"Number of words: {word_count}")

# Check if "dummy" is in the combined string
is_dummy = "dummy" in combined_string

# Print the result
print(f"Is 'dummy' in the string: {is_dummy}")

# Check if the two strings are equal
strings_equal = string1 == string2

# Print the result
print(f"Are the strings equal: {strings_equal}")
