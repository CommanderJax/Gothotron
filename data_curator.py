import abc
import re

class DataCurator(object):

    __metaclass__ = abc.ABCMeta
    audio_data_path = ''
    ouinfo_data_path = ''
    ouinfo_content = ''
    dialogue_dict = {}

    def __init__(self, ouinfo_path, data_path):
        self.ouinfo_data_path = ouinfo_path
        self.data_path = data_path

    def _load_ouinfo(self):
        with open(self.ouinfo_data_path) as ouinfo_file:
            self.ouinfo_content = ouinfo_file.readlines()

    @abc.abstractmethod
    def process_ouinfo(self):
        """Override for each language localisation to ensure the file is processed properly"""
        return


class EnglishDataCurator(DataCurator):

    def process_ouinfo(self):
        """
        English processor
        Processes raw data in ouinfo into a dictionary that maps filenames to dialogue text
        """

        self._load_ouinfo()
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
                if filename == "TPL_1436_TEMPLER_CRAWLER_INFO_13_02.WAV":
                    del self.dialogue_dict[filename]

        # if len(self.dialogue_dict) != 5515:
        #     print("Warning, the resulting dataset size is incorrect!")

