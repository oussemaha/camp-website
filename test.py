from datetime import datetime

def calculate_age(birthdate):
    # Parse the birthdate string into a datetime object
    birthdate = datetime.strptime(birthdate, "%Y-%m-%d")

    # Get the current date
    current_date = datetime.now()
    
    # Calculate the difference between the current date and the birthdate
    age = current_date.year - birthdate.year
    
    # Check if the birthdate has already occurred this year
    if current_date.month < birthdate.month or (current_date.month == birthdate.month and current_date.day < birthdate.day):
        age -= 1  # Subtract 1 from the age
    
    return age

# Example usage
birthdate_str = "1990-05-15"  # Replace with the birthdate string in "yyyy-mm-dd" format
age = calculate_age(birthdate_str)
print("Age:", age)
