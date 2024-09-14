### 2024 Fall Miniproject DOCUMENTATION

After setting up our environments and the Pico itself, we completed the three
exercises as requested.

## DESIGN

For the cloud portion of our miniproject, we decided to use the exercise_game
button press game as our main program that will send and receive data from the
cloud. We chose to utilize the Firebase REST API based on recommendation from
instructors. This allowed us to use Firebase's realtime database which we use to send
and receive data from.

The referenced data that is being transferred is the .json file of the player's
score from the button press game. We used the 'network' python module to
establish a WLAN connection so the Pico can access the internet. We use the
'requests' HTTP module to make POST requests to the Firebase realtime database.

When a player completes a game,