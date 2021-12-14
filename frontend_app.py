import json

import kivy
import time
import random
from sound import Sound

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

kivy.require('1.11.1')


class LoginScreen(GridLayout):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='User Name'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)


class TestButtons(GridLayout):
    def __init__(self, **kwargs):
        super(TestButtons, self).__init__(**kwargs)

        self.cols = 1
        self.label = Label(text='Press the Start test button to start the test \n'
                                'This test consist in identifying from which direction (left or right) the sound comes. \n \n'
                                'Required use of headphones or speakers.')
        self.add_widget(self.label)

        self.test_btn = Button(text="Start test")
        self.test_btn.bind(on_press=self.pressed_test_btn)
        self.add_widget(self.test_btn)

        self.running_test_event = None
        self.cancelled_test = False

        self.sound = Sound()

    def delayed_work(self, func, items, delay=0):
        '''
        Apply the func() on each item contained in items
        From: https://github.com/kivy/kivy/wiki/Delayed-Work-using-Clock
        '''

        if not items:
            return

        def _delayed_work(*l):
            item = items.pop()
            if func(item) is False or not len(items):
                return False
            self.running_test_event = Clock.schedule_once(_delayed_work, delay)

        self.running_test_event = Clock.schedule_once(_delayed_work, delay)

        return delay*len(items)

    def pressed_test_btn(self, instance):
        print("Pressed test btn")

        if self.test_btn.text == "Start test":
            self.cancelled_test = False

            # Add the buttons for the test
            self.desk = GridLayout()
            self.desk.cols = 2
            self.add_widget(self.desk)

            def change_label_text(text):
                self.label.text = text
            text_list = ["Test in progress", "1", "2", "3", "Starting test in"]
            delay = self.delayed_work(change_label_text, text_list, 1)

            self.left_btn = Button(text="Left ear")
            self.left_btn.bind(on_press=self.left_ear)
            self.desk.add_widget(self.left_btn)

            self.right_btn = Button(text="Right ear")
            self.right_btn.bind(on_press=self.right_ear)
            self.desk.add_widget(self.right_btn)

            self.test_btn.text = "End test"

            if not self.cancelled_test:
                Clock.schedule_once(self.start_ear_test, delay+1)

        else:
            # Stop test if running
            if self.running_test_event:
                Clock.unschedule(self.running_test_event)
                self.cancelled_test = True
            if self.test_sound_event:
                Clock.unschedule(self.test_sound_event)
                self.cancelled_test = True
            # Remove buttons of the test
            self.test_btn.text = "Start test"
            self.label.text = "Test ended"

            self.remove_widget(self.desk)
            self.remove_widget(self.right_btn)
            self.remove_widget(self.left_btn)

            # Save results in a txt file
            results = {"left": self.dict_left_ear, "right": self.dict_right_ear}
            with open("results.json", "w") as json_file:
                json.dump(results, json_file)
                print("Saved json")

    def initialize_sound_dict(self):
        sounds = {"250": 0, "500": 0, "1000": 0, "2000": 0, "4000": 0, "8000": 0}

        db = {str(t): 0 for t in range(0, 110, 10)}
        for s in sounds:
            sounds[s] = db
        return sounds

    def test_sound(self, t):
        self.sound.frequency = self.freq
        self.sound.volume = self.decibels
        self.sound.location = self.location_of_sound
        self.sound.time = 0.3

        self.sound.play()

        Clock.schedule_once(self.check_answer, 3)


    def get_next_freq(self):
        if self.freq == 0:
            self.freq = 250
        else:
            d = {"250": 500, "500": 1000, "1000": 2000, "2000": 4000, "4000": 8000, "8000": -1}
            self.freq = d[str(self.freq)]

    def check_answer(self, t):
        if self.location_of_sound == "left":
            if self.user_location_answer == "left":
                self.dict_left_ear[str(self.freq)][str(int(self.decibels*100))] = 1
                self.get_next_freq()
                self.decibels = 0.1
            elif self.user_location_answer == "right":
                self.dict_left_ear[str(self.freq)][str(int(self.decibels*100))] = -1
                self.decibels += 0.1
            else:
                self.decibels += 0.1
        elif self.location_of_sound == "right":
            if self.user_location_answer == "left":
                self.dict_right_ear[str(self.freq)][str(int(self.decibels*100))] = -1
                self.decibels += 0.1
            elif self.user_location_answer == "right":
                self.dict_right_ear[str(self.freq)][str(int(self.decibels*100))] = 1
                self.get_next_freq()
                self.decibels = 0.1
            else:
                self.decibels += 0.1

        if self.decibels > 1:
            if self.user_location_answer == "left":
                self.dict_left_ear[str(self.freq)]["100"] = 1
            # Assign the lowest puntuation
            self.get_next_freq()
            self.decibels = 0.1

        self.user_location_answer = None

        if self.freq != -1 and not self.cancelled_test:
            self.test_sound_event = Clock.schedule_once(self.test_sound, 1)
        elif self.freq == -1 and self.location_of_sound == "left":
            self.location_of_sound = "right"  # Next update, the location could be randomly changing
            self.freq = 0
            self.get_next_freq()
            self.decibels = 0.1
            self.test_sound_event = Clock.schedule_once(self.test_sound, 1)
        else:
            # Remove buttons of the test
            self.test_btn.text = "Start test"
            self.label.text = "Test ended \n \nResults saved"

            self.remove_widget(self.desk)
            self.remove_widget(self.right_btn)
            self.remove_widget(self.left_btn)

            # Save results in a txt file
            results = {"left": self.dict_left_ear, "right": self.dict_right_ear}
            with open("results.json", "w") as json_file:
                json.dump(results, json_file)
                #print("Saved json")
            return



    def round(self, t):
        #self.location_of_sound = random.choice(["left", "right"])
        self.location_of_sound = "left"

        self.get_next_freq()

        self.decibels = 0.1

        Clock.schedule_once(self.test_sound, 1)

    def start_ear_test(self, *l):
        self.location_of_sound = None

        self.freq = 0
        self.dict_left_ear = self.initialize_sound_dict()
        self.dict_right_ear = self.initialize_sound_dict()

        self.user_location_answer = None

        if self.cancelled_test:
            return

        Clock.schedule_once(self.round, 0.1)


    def right_ear(self, instance):
        print("Heard sound in the right ear")
        self.user_location_answer = "right"

    def left_ear(self, instance):
        print("Heard sound in the left ear")
        self.user_location_answer = "left"


class Menu(GridLayout):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)

        self.cols = 1
        self.title = Label(text='Welcome to the Hearing Test App !')
        self.add_widget(self.title)

        self.left_right_test = Button(text="Left / Right ear test")
        self.add_widget(self.left_right_test)

        self.range_test = Button(text="Range test")
        self.add_widget(self.range_test)


class HearingTestApp(App):

    def build(self):
        #return Menu()
        return TestButtons()


if __name__ == '__main__':
    HearingTestApp().run()
