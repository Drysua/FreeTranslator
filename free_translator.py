import time
import os
import logging
import re
from deepl_scrapper import DeepLScrapper
from deep_translator import GoogleTranslator

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} executed in {time.time() - start:.2f}s")
        return result
    return wrapper

class FreeTranslator:
    CHUNK_SEPARATORS = ["-+ +-", "+ ;", "+;", "+;+", "+; ;+", "---", "+-=-", "; ;"]
    DEEPL_MAX_SIZE = 1500
    GOOGLE_MAX_SIZE = 5000
    MAX_RETRIES = 5
    RATE_LIMIT_DELAY = 10

    def __init__(self, source, target, translator_service='deepl'):
        self.source = source
        self.target = target
        self.current_translator = translator_service
        self._initialize_translators()

        self.CURRENT_CHUNK_SEPARATOR_INDEX = 0
        self.CHUNK_SEP = self.CHUNK_SEPARATORS[self.CURRENT_CHUNK_SEPARATOR_INDEX]
    
    def _initialize_translators(self):
        self.translator_deepl= DeepLScrapper(source=self.source, target=self.target)
        self.translator_google = GoogleTranslator(source=self.source, target=self.target)
    
    def _switch_separator(self):
        self.CURRENT_CHUNK_SEPARATOR_INDEX = (self.CURRENT_CHUNK_SEPARATOR_INDEX + 1) % len(self.CHUNK_SEPARATORS)
        self.CHUNK_SEP = self.CHUNK_SEPARATORS[self.CURRENT_CHUNK_SEPARATOR_INDEX]
        logging.info('CURRENT SEPARATOR: ', self.CHUNK_SEP)

    def _translate(self, text):
        if (self.current_translator == 'deepl'):
            return self.translator_deepl.translate(text)
        else:
            retries = 0
            while retries < self.MAX_RETRIES:
                try:
                    return self.translator_google.translate(text)
                except Exception as e:
                    logging.error(f"Translation failed for text: '{text}' with error: {e}")
                    retries += 1
                    time.sleep(self.RATE_LIMIT_DELAY)
            else:
                raise Exception("Failed to translate text after maximum retries with Google. Wait some time a start again")

    def _get_last_line(self, file_path):
        if not os.path.exists(file_path):
            return 0
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for _ in file)
    
    def _get_max_input_size(self):
        return self.DEEPL_MAX_SIZE if self.current_translator == 'deepl' else self.GOOGLE_MAX_SIZE

    def _change_separator(self, text, old_separator, new_separator):
        old_separator_escaped = re.escape(old_separator)
        return re.sub(old_separator_escaped, new_separator, text)

    def _translate_chunk(self, buffer, current_chunk, output_file):
        try:
            translated_chunk = self._translate(current_chunk).split(self.CHUNK_SEP)
        except Exception as e:
            logging.error(f"Translation error: {e}")
            self.current_translator = 'google'
            logging.info("Switching to Google Translator...")
            translated_chunk = self._translate(current_chunk).split(self.CHUNK_SEP)
        # print(current_chunk)
        # print(translated_chunk)
        # print(buffer)
        # print(len(buffer), len(translated_chunk))
        retries = 0
        max_retries = len(self.CHUNK_SEPARATORS)
        prime_buffer = buffer.copy()
        while retries < max_retries:
            try:
                for j, _ in enumerate(buffer):
                    # print(buffer[j][1], translated_chunk[j])
                    buffer[j][2] = translated_chunk[j].replace('_S_', '/')
                    buffer[j][1] = buffer[j][1].replace('_S_', '/')
                    buffer[j] = '|'.join(buffer[j])

                with open(output_file, 'a', encoding='utf-8') as outfile:
                    outfile.write(''.join(buffer))
                    outfile.flush()
                return

            except Exception as e:
                retries += 1
                prev_separator = self.CHUNK_SEP
                self._switch_separator()
                #change separator in current sting]
                current_chunk = self._change_separator(current_chunk, prev_separator, self.CHUNK_SEP)
                translated_chunk = self._translate(current_chunk).split(self.CHUNK_SEP)
                buffer = prime_buffer.copy()
                # print(len(buffer), len(translated_chunk))
        else:
            raise Exception("All separators failed")

 
    @timing_decorator
    def translate_file(self, file_path, output_file, progress_callback=None):
        start_line = self._get_last_line(output_file)
        logging.info(f"Resuming from line {start_line}...")
        if progress_callback:
            progress_callback(0)

        with open(file_path, 'r', encoding='utf-8') as infile:
            buffer = []
            current_chunk = ""
            total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))

            for _ in range(start_line):
                infile.readline()

            for i, line in enumerate(infile, start=start_line):
                raw_line = line.split('|')
                raw_line[1] = raw_line[1].replace('/', '_S_')
                max_input = self._get_max_input_size()
                if len(current_chunk) + len(raw_line[1]) + len(self.CHUNK_SEP) < max_input:
                    current_chunk = current_chunk + raw_line[1] + self.CHUNK_SEP
                    # current_chunk = ''.join([current_chunk, raw_line[1], self.CHUNK_SEP])
                    buffer.append(raw_line)
                else:
                    self._translate_chunk(buffer, current_chunk, output_file)
                    self.CURRENT_CHUNK_SEPARATOR_INDEX = 0
                    self.CHUNK_SEP = self.CHUNK_SEPARATORS[self.CURRENT_CHUNK_SEPARATOR_INDEX]
                    raw_line = line.split('|')
                    raw_line[1] = raw_line[1].replace('/', '_S_')
                    current_chunk = raw_line[1] + self.CHUNK_SEP
                    buffer = [raw_line]
                    if progress_callback:
                        progress_callback((i + 1) / total_lines * 100)
                    logging.info(f"Checkpoint reached: {i + 1} lines translated.")

            if buffer:
                self._translate_chunk(buffer, current_chunk, output_file)
                if progress_callback:
                    progress_callback(100)
                logging.info('Translation complete')
    

if __name__ == '__main__':
    input_file = 'input.txt'
    output_file = 'output.txt'
    free_tranlator = FreeTranslator(source='en', target='ru')
    free_tranlator.translate_file(input_file, output_file)