import boto3
import json
import csv
from datetime import datetime

# Initialize the Cognito client
client = boto3.client('cognito-idp', region_name='Add-your-region')

# Replace with your User Pool ID
user_pool_id = 'Add-yours'

def list_all_users_with_states(user_pool_id):
    users = []
    pagination_token = None
    call_count = 0  # To track the number of API calls

    while True:
        try:
            call_count += 1  # Increment call count
            if pagination_token:
                response = client.list_users(
                    UserPoolId=user_pool_id,
                    Limit=60,
                    PaginationToken=pagination_token
                )
            else:
                response = client.list_users(
                    UserPoolId=user_pool_id,
                    Limit=60
                )

            users.extend(response['Users'])

            # Log the number of users fetched in this call
            print(f"Fetched {len(response['Users'])} users in call {call_count}.")
            
            # Check for pagination token
            pagination_token = response.get('PaginationToken')
            if not pagination_token:
                break
        except client.exceptions.InvalidParameterException as e:
            print(f"Error occurred: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    # Count users by state
    user_states = {}
    for user in users:
        status = user['UserStatus']
        user_states[status] = user_states.get(status, 0) + 1

    return users, user_states

def convert_datetime_to_string(user):
    """Convert datetime objects in the user dictionary to ISO formatted strings."""
    if 'UserCreateDate' in user:
        user['UserCreateDate'] = user['UserCreateDate'].isoformat()
    if 'UserLastModifiedDate' in user:
        user['UserLastModifiedDate'] = user['UserLastModifiedDate'].isoformat()
    return user

def save_to_json(users):
    # Save to JSON file
    with open('cognito_users.json', 'w') as f:
        json.dump(users, f, indent=4)

def save_to_csv(users):
    # Save to CSV file
    with open('cognito_users.csv', 'w', newline='') as csvfile:
        fieldnames = users[0].keys()  # Get the headers from the first user's keys
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # Write the header
        for user in users:
            writer.writerow(user)  # Write user data

# Call the function to get all users and their states
all_users, user_states = list_all_users_with_states(user_pool_id)

# Convert datetime objects to strings for each user
all_users = [convert_datetime_to_string(user) for user in all_users]

# Save to JSON and CSV files
save_to_json(all_users)
save_to_csv(all_users)

# Print results
print(f"Total users fetched: {len(all_users)}")
print("User states count:", user_states)
