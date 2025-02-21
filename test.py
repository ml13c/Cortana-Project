#THIS IS THE RECOVERED VERSION OF THE CODE AFTER LOST LAPTOP
"""
This is the main script for the Cortana-like assistant. The script works to how I imagine an alexa works. Once it is powered on it is always on
unlees turned off by the main power source. It is always listening for the keyword "cortana" and once it hears it it will start the animation
and wait for a command. If it hears the keyword "exit" it will stop the animation and go back to listening for the keyword. Ideally 
this is connected to the internet so that APIS all work correctly. G4F is used for the AI responses and is the main communication with the user if
not doing commands.
"""
'''
TODO:
    -weather optimization
    -make the animations work correctly with the commands(do animation and return to idle)
    -add weather os to environmental variables***
    -add more commands
        -youtube video player
        -maps
    -add more animations
    -weather visualization
'''
import threading
import time
import subprocess
import os
from datetime import datetime
import geocoder
import requests
import socket
from g4f.client import Client

client = Client()
testaction = "still"
keyword_detected = False
voices_process = None

"""
This uses an api key in the os. I have removed it for security reasons. You can add it back in by adding it to the os environment variables on your
system or if you want you can just add it to the code for simplicity. IF RASPBERRY PI OS(linux distrobution) IS DIFFERENT it would be best to 
add to code for simplicity. It uses the openweathermap api to get the weather data via city name or current location.
"""
def get_weather_data(city_text):
    user_api = os.environ['current_weather_data']#add environmemtal variable(current_weather_data) by clicking new and pasating the actual key value
    complete_api_link = "https://api.openweathermap.org/data/2.5/weather?q=" + city_text + "&appid=" + user_api
    api_link = requests.get(complete_api_link)
    api_data = api_link.json()

    try:
        
        #Extract weather information. There is more to get but these are just what I think is important for now.
        temp_city = (1.8 * (api_data['main']['temp'] - 273.15) + 32)
        weather_desc = api_data['weather'][0]['description']
        hmdt = api_data['main']['humidity']
        wind_spd = api_data['wind']['speed']
        #maybe add uv index later
        date_time = datetime.now().strftime("%d %b %Y | %I:%M:%S %p")

        # Format weather information as a string
        # maybe format it into different strings to make it easier to modify in pyghame/seperate window
        weather_info = f"{city_text.upper()}  || {date_time}\n"
        weather_info += "{:.2f} F\n".format(temp_city)
        weather_info += f"{weather_desc}\n"
        weather_info += f"Humidity  : {hmdt}%\n"
        weather_info += f"Wind Speed : {wind_spd} kmph"
        
        return weather_info
    except KeyError as e:
        print(f"Error occurred while fetching weather data: {e}")
        return "Failed to fetch weather data for " + city_text
'''
I could probably make this a function that just get the lan and lon and then pass that to the weather api for get weather data
so I will add that to the todo list. Other than finding the current location to determine the city it works the same as the other function.
So I think I can pass it as a parameter to the get weather data function.**MUST DO BY 2/22***
This would bea good idea to do just change it to use latlon to find city and
pass to get weather data.
'''
def get_latlonweather_data():
    user_api = os.environ['current_weather_data']
    g = geocoder.ip('me')
    lat, lon = g.latlng
    lat_str = str(lat)
    lon_str = str(lon)
    print(g.latlng)
    print(lat, lon)
    complete_latlon_link ="https://api.openweathermap.org/data/2.5/weather?lat="+lat_str+"&lon="+lon_str+"&appid="+user_api
    latlon_link = requests.get(complete_latlon_link)
    latlon_data = latlon_link.json()
    try:
        #variables for latlon data
        date_time = datetime.now().strftime("%d %b %Y | %I:%M:%S %p")
        temp_latlon = (1.8*((latlon_data['main']['temp']) - 273.15)+32)
        tempmin_latlon = (1.8*((latlon_data['main']['temp_min']) - 273.15)+32)
        tempmax_latlon = (1.8*((latlon_data['main']['temp_max']) - 273.15)+32)
        weather_latlon = latlon_data['weather'][0]['description']
        hmdt_latlon = latlon_data['main']['humidity']
        windspd_latlon = latlon_data['wind']['speed']
        latlon_location = latlon_data['name']
        #format
        weather_info = f"{latlon_location.upper()}  || {date_time}\n"
        weather_info += "{:.2f} F\n".format(temp_latlon)
        weather_info += "Max: {:.2f} F\n".format(tempmax_latlon)
        weather_info += "Min: {:.2f} F\n".format(tempmin_latlon)
        weather_info += f"{weather_latlon}\n"
        weather_info += f"Humidity  : {hmdt_latlon}%\n"
        weather_info += f"Wind Speed : {windspd_latlon} kmph"
        
        return weather_info
    except KeyError as e:
        print(f"Error occurred while fetching weather data: {e}")
        return "Failed to fetch weather data for " + latlon_location
'''
This sends the standard 'testaction' to the animation handler. This is how the model knows what to do based on commands I give or infer.
The plan is to have a set of idle animations rather than just one so I will probably make it into a seperate array and have it run randomly through
one of those animations when idle.
'''
def send_testaction(action):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(action.encode(), ('localhost', 9999))
'''
This sends the weather data to the animation handler. This is how the model knows what to display based on the weather data I give it.
This data is then formatted and displayed. I can probably break this down so I can display other things that arent weather but I will see.
'''
def send_weather(weather):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(weather.encode(), ('localhost', 9998))
'''
This is where the main stuff starts to happen

This is where the animations start to occur. This is where the animated model knows what to do based on the test action set to a type of command.
It can detect weather based on how the input is formatted. If it is formatted as "weather in city" it will use the city name to get the weather data.
Right now I need to figure out a way to exit and return back to listen for keyword but that should be easy enough. 
'''
def listen_for_command():
    global testaction
    global keyword_detected
    global voices_process
    while keyword_detected:
        try:
            cortana_input = input("Listen for command - Input: ")
            print("Cortana reads:", cortana_input)
            if "weather in" in cortana_input:
                testaction = "weather"
                send_testaction(testaction)
                city_text = cortana_input.split("weather in", 1)[1].strip()
                print(f"Fetching weather for {city_text}")
                #weather based on city
                weather_info = get_weather_data(city_text)
                send_weather(weather_info)
                print(weather_info)
                print("Command - testaction sent as", testaction)
            elif "weather" in cortana_input:
                testaction = "weather"
                send_testaction(testaction)
                print("weather data being shown")
                #weather current location
                weather_info = get_latlonweather_data()
                send_weather(weather_info)
                print(weather_info)
                print("Command - testaction sent as", testaction)
            elif "exit" in cortana_input:
                testaction = "dismiss"
                send_testaction(testaction)
                print("Going back to sleep")
                print("Command - testaction sent as", testaction)
                keyword_detected = False
                if voices_process:
                    time.sleep(5)
                    voices_process.terminate()
                    voices_process = None
                break  # Exit the loop when "exit" is detected
            else:
                testaction = "cross"
                send_testaction(testaction)
                # Pass user input to GPT-3.5 for further processing
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": cortana_input}],
                )
                # Output GPT 4 mini Response
                print("GPT 4 mini Response:", response.choices[0].message.content)
        except Exception as e:
            print(f"Exception in listen for command found error: {e}")
'''
Pretty much its just a while loop that keeps rununing listening for the keyword. Once it is detected it will start the actual program.
I can proably shorten it but I wanted to format it to read commands before the keyword was actually detected. Even then there is probably a way to do so 
but due to how long it might take to debug i first want to fully implement and perfect other functionalities
'''
def listen_for_keyword():
    global testaction
    global keyword_detected
    while not keyword_detected:
        try:
            user_input = input("Listen keyword - Enter input:")
            if "cortana" in user_input:
                keyword_detected = True
                parts = user_input.split("cortana")
                if len(parts) > 1:
                    after_cortana = parts[1].strip()
                    if "weather in" in after_cortana:
                        testaction = "weather"
                        send_testaction(testaction)
                        city_text = after_cortana.split("weather in", 1)[1].strip()
                        print(f"Fetching weather for {city_text}")
                        #weather based on city
                        weather_info = get_weather_data(city_text)
                        send_weather(weather_info)
                        print(weather_info)                       
                    elif "weather" in after_cortana:
                        print("Listen for keyword - Does weather stuff")
                        testaction = "weather"
                        send_testaction(testaction)
                        print("weather data being shown")
                        #weather current location
                        weather_info = get_latlonweather_data()
                        send_weather(weather_info)
                        print(weather_info)
                        print("k-testaction sent as", testaction)
                    else:
                        print("This was inputted in listen keyword:", after_cortana)
                        testaction = "idle"
                        send_testaction(testaction)
                        print("k-testaction sent as", testaction)
                        # Pass user input to GPT-3.5 for further processing
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": after_cortana}],
                        )
                        # Output GPT 4 mini Response
                        print("GPT 4 mini Response:", response.choices[0].message.content)
                else:
                    after_cortana = ""
        except Exception as e:
            print(f"Exception done correctly found error: {e}")
'''
this is the animation function that starts the animation process. It is a seperate process so that it can run in the background while the main
script is still running. This is how the model knows what to do based on the test action set to a type of command.
'''
def animation():
    global voices_process
    voices_process = subprocess.Popen(["python", "voices.py"])
'''
This is the main loop that runs the program. It starts the animation process and then listens for commands. Once the keyword is detected it will
start the main loop. Based off of certain keywords
'''
def main_loop():
    global keyword_detected
    while True:
        listen_for_keyword()  # Wait for the keyword to be detected
        animation_thread = threading.Thread(target=animation, daemon=True)
        animation_thread.start()
        listen_for_command()  # Wait for commands after the keyword is detected
        keyword_detected = False

# Start the main loop
main_thread = threading.Thread(target=main_loop)
main_thread.start()
main_thread.join()