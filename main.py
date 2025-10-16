import sys
import os
import multiprocessing

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from Communication.voice_input import VoiceInput
from Communication.voice_output import VoiceOutput
from Core.command_handler import CommandHandler
from Reminders.reminder_manager import ReminderManager 

def main():
    voice_output = VoiceOutput("Resources/voices")
    voice_input = VoiceInput(language="ru-RU")
    reminder_manager = ReminderManager(voice_output) 

    weather_api_key = ""
    folder_id = ""
    yandex_gpt_api_key = ""

    handler = CommandHandler(
        voice_output=voice_output,
        reminder_manager=reminder_manager, 
        weather_api_key=weather_api_key,
        folder_id=folder_id,
        yandex_gpt_api_key=yandex_gpt_api_key
    )

    greeting_text = "Привет! Я Мита, ваш верный помощник. Готова к работе!"
    print(greeting_text)
    voice_output.play("greeting.wav", text=greeting_text)

    print("Голосовой ассистент запущен. Говорите команду:")
    try:
        while True:
            command = voice_input.listen()
            if command:
                print(f"Распознанная команда: {command}")
                handler.run_command(command)
    except KeyboardInterrupt:
        print("\nЗавершение работы ассистента...")
    finally:
        reminder_manager.stop() 
        print("Поток напоминаний остановлен. До свидания!")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
