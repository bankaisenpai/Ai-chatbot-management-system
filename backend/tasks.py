from fastapi import BackgroundTasks
import time

def fake_train_model(bot_id: int):
    # placeholder: call Rasa training or persist dataset to storage
    time.sleep(3)  # simulate
    print("Training complete for bot", bot_id)

def enqueue_training(background_tasks: BackgroundTasks, bot_id: int):
    background_tasks.add_task(fake_train_model, bot_id)
