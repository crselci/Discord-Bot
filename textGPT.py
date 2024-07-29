import openai

openai.api_key = #YOUR KEY HERE

DUNGEON = 0
MERCHANT = 1
WAITINGROOM = 2

def call_gpt(prompt, room):
    try:
        response = None
        if room == DUNGEON:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Describe a fantasy room and creature."},
                    {"role": "user", "content": "I enter the room."},
                    {"role": "assistant", "content": prompt}
                ]
            )
        elif room == MERCHANT:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Merchant message of the day."},
                    {"role": "user", "content": "Reading display board."},
                    {"role": "assistant", "content": prompt}
                ]
            )
        elif room == WAITINGROOM:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "A simple portal/fantasy room display board."},
                    {"role": "user", "content": "Maybe I should go in."},
                    {"role": "assistant", "content": prompt}
                ]
            )

        message_content = response['choices'][0]['message']['content']
        print(message_content)
        return message_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def dungeon_description(creature):
    prompt = f"Describe a hostile {creature} awaiting in the described room in less than 60 words."
    response = call_gpt(prompt, DUNGEON)
    if response:
        write_text(response)
    return response

def merchant_room(wares):
    prompt = f"Describe a room full of wares including only these {wares} in less than 50 words. You don't have to include all of the items listed, just be goofy and funny."
    response = call_gpt(prompt, MERCHANT)
    if response:
        write_text(response)
    return response

def waiting_room():
    prompt = "In your funniest way describe a waiting room used for directing people to dungeons in less than 50 words."
    response = call_gpt(prompt, WAITINGROOM)
    if response:
        write_text(response)
    return response

def write_text(text):
    filename = "gptFile.txt"
    try:
        with open(filename, "a") as file:
            file.write(text + "\n")
    except IOError as e:
        print(f"Failed to write to file: {e}")
