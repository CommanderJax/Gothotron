import abc
import re
import json
import math
import random
import os


# ffmpeg -i name.wav -vn -ar 22050 -ac 1 output.wav

class DataCurator(object):
    __metaclass__ = abc.ABCMeta
    ouinfo_data_path = ''  # TODO implement support for SVM audio files
    ouinfo_content = ''

    dialogue_dict = {}
    dialogue_character_mapping = {}

    validation_set_size = 0.05  # the percentage of audio files that will be used to form our validation set, 5% by default

    def __init__(self, ouinfo_path, validation_set_size=0.05):
        self.ouinfo_data_path = ouinfo_path
        self._load_ouinfo()
        self._process_ouinfo()
        self._load_dialogue_character_mapping()
        self.validation_set_size = validation_set_size
        self.output_path = ''

    @abc.abstractmethod
    def _load_dialogue_character_mapping(self):
        return

    def _load_ouinfo(self):
        with open(self.ouinfo_data_path) as ouinfo_file:
            self.ouinfo_content = ouinfo_file.readlines()

    @abc.abstractmethod
    def _process_ouinfo(self):
        """Override for each language localisation to ensure the file is processed properly"""
        return


class EnglishDataCurator(DataCurator):

    def __init__(self, *args, **kwargs):
        super(EnglishDataCurator, self).__init__(*args, **kwargs)
        self.output_path = 'output/english/'

    def _load_dialogue_character_mapping(self):
        dialouge_character_mapping_filepath = 'data/english/gothic1_character_dialogue_mapping.json'  # only supporting Gothic 1 for now
        assert dialouge_character_mapping_filepath != ''
        with open(dialouge_character_mapping_filepath) as dialouge_character_mapping_file:
            self.dialogue_character_mapping = json.load(dialouge_character_mapping_file)
        assert len(self.dialogue_character_mapping['Hero']) == 1936

        # lowering the case of the .wav suffix will make our lives way easier down the line
        for character, dialogues in self.dialogue_character_mapping.items():
            for i in range(0, len(dialogues)):
                self.dialogue_character_mapping[character][i] = dialogues[i].replace(".WAV", ".wav")

        # We need to do this extra step to cater for the fact that we don't support SVM audio files yet and we've
        # removed some broken/meaningless audio files already in the process_ouinfo function.
        for character, dialogues in self.dialogue_character_mapping.items():
            curated_dialogues = [dialogue for dialogue in dialogues if dialogue in self.dialogue_dict]
            self.dialogue_character_mapping[character] = curated_dialogues

            # Debugging
            # print("Character: {}, num dialogues: {}, num after curation: {}".format(character, len(dialogues), len(curated_dialogues)))
            # missing_dialogues = set(dialogues).symmetric_difference(set(curated_dialogues))
            # print_limit = 50
            # for index, dialogue in enumerate(missing_dialogues):
            #     print(dialogue)
            #     if index == print_limit:
            #         break
            # print("---")

    def _generate_test_and_validation_dataset(self, character="Hero"):
        total_dataset_size = len(self.dialogue_character_mapping[character])
        total_validation_dataset_size = math.ceil(self.validation_set_size * total_dataset_size)

        choices = list(range(total_dataset_size))
        random.shuffle(choices)

        validation_set_incides = []
        for i in range(0, total_validation_dataset_size):
            validation_set_incides.append(choices.pop())

        # Debugging, TODO, replace with proper logging & DEBUG flags
        # print(len(validation_set_incides))
        # print(validation_set_incides)

        # We're finally building our datasets and writing them to the relevant files on disk.
        validation_dir = self.output_path + character.lower() + '/'
        train_dir = validation_dir
        validation_path = validation_dir + 'validation_filelist.txt'
        train_path = validation_dir + 'train_filelist.txt'
        if not os.path.exists(train_dir):
            os.makedirs(train_dir)
        with open(validation_path, 'w') as validation, open(train_path, 'w') as train:
            counter = 0
            for audio_file, text in self.dialogue_dict.items():
                if audio_file in self.dialogue_character_mapping[character]:
                    formatted_input = "DUMMY/{}|{}\n".format(audio_file, text)
                    if counter in validation_set_incides:
                        validation.write(formatted_input)
                    else:
                        train.write(formatted_input)
                    counter += 1
        # Samples from resulting files:
        # DUMMY/GRD_200_THORUS_WANNABEMAGE_INFO_15_01.wav|I'm interested in the path of magic.
        # DUMMY/DIA_SCORPIO_REFUSETRAIN_15_00.wav|Can you teach me to fight?
        # DUMMY/GRD_205_SCORPIO_CROSSBOW2_OK_15_01.wav|Let's start now.
        # DUMMY/DIA_SCATTY_TRAIN_1H_15_00.wav|I want to improve my handling of one-handed weapons.
        # DUMMY/DIA_GRD_215_TORWACHE_FIRST_TROUBLE_15_00.wav|Sure, I plan to take on the whole Camp!

    def generate_test_and_validation_datasets(self):
        """
        Generates the filelists that will be read by tacotron2 or other speech synthesis model
        WARNING! The results will be different with each execution due to randomness
        TODO certain actors are supplying voices to multiple game NPCs, need to map voice actors to characters and support generating datasets by voice actor
        """
        for character, dialogues in self.dialogue_character_mapping.items():
            self._generate_test_and_validation_dataset(character)

    def _process_ouinfo(self):
        """
        English processor
        Processes raw data in ouinfo into a dictionary that maps filenames to dialogue text
        """

        ouinfo_lines = self.ouinfo_content

        for line in ouinfo_lines:
            regex = re.match(".*AI_Output.*\"(.*)\".*\/\/(.*)\}", line)

            if regex:
                # Found the words we're interested in...
                # Now, we need to map our file names to the text dialogue.
                # We also need to remove whitespaces from the beginning and end of each line and quotes("")
                # present throughout the sentence as they are sometimes repeated and meaningless.
                filename = regex.group(1).upper() + ".wav"

                self.dialogue_dict[filename] = regex.group(2).replace('"', '').strip()
                # As we require the data to be clean, some Gothic audio files contain unintelligible or inaudible sounds
                # For example, when the hero addresses the baals and they "sigh" in response.
                # Fe need to remove such occurrences in order to clean our data,
                # we also need to add punctuation if it's missing.
                try:
                    if not (self.dialogue_dict[filename][-1] in r"!?,.;:"):  # add punctuation if it's missing
                        self.dialogue_dict[filename] += "."
                        # print(f'filename: {filename}, text: {self.dialogue_dict[filename]}')  # if you need to debug...
                except IndexError:
                    # no text dialogue associated with this audio file, let's remove it from our dataset
                    # print(f'No text, filename: {filename}, text: {self.dialogue_dict[filename]}')  # if you need to debug...
                    del self.dialogue_dict[filename]

                # Some inaudible audio files will not be useful to our model and may affect its performance,
                # let's remove them
                if filename in self.dialogue_dict and self.dialogue_dict[filename] == "(sigh).":
                    del self.dialogue_dict[filename]

                # This audio file is broken, so let's remove it from our dataset as well
                if filename == "TPL_1436_TEMPLER_CRAWLER_INFO_13_02.wav":
                    del self.dialogue_dict[filename]

        assert len(self.dialogue_dict) == 5514
