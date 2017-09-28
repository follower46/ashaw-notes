#!/usr/bin/python3

""" Local File Note Connector module
"""
import re
import os
import shutil
import ashaw_notes.utils.search
import ashaw_notes.utils.configuration
from ashaw_notes.utils.search import datestring_to_timestamp


class LocalNotes:

    config_section = 'local_notes'
    __line_regex__ = re.compile(r'\[([^\]]+)\] (.*)')

    def is_enabled(self):
        """Checks if connector is enabled"""
        backends = ashaw_notes.utils\
            .configuration\
            .load_config()\
            .get('base_config', 'data_backends')
        return self.config_section in backends

    def save_note(self, timestamp, note):
        """Saves note to timestamp"""
        self.add_local_note(timestamp, note)

    def delete_note(self, timestamp):
        """Removes note at supplied timestamp"""
        self.delete_local_note(timestamp)

    def update_note(self, original_timestamp, new_timestamp, new_note):
        """Updates note at supplied timestamp"""
        self.delete_note(original_timestamp)
        self.save_note(new_timestamp, new_note)

    def find_notes(self, search_terms):
        """Returns all notes corresponding to supplied search object"""
        request = ashaw_notes.utils.search.get_search_request(search_terms)
        return self.find_local_notes(request)

    @staticmethod
    def get_common_words():
        """Finds all common words in note file"""
        # not yet implemented
        return set()

    def add_local_note(self, timestamp, note):
        """Inserts note into local file"""
        self.backup_notes()
        if os.path.isfile(self.get_notes_file_location()):
            reading_file = open(self.get_notes_file_location(), "r+", encoding="utf8")
        else:
            reading_file = None
        writing_file = open(self.get_notes_file_location(), "a+", encoding="utf8")
        if not self.is_header_found(reading_file, timestamp):
            self.write_header(writing_file, self.get_date_header(timestamp))
        self.write_line(writing_file, self.build_note_line(timestamp, note))
        if reading_file:
            reading_file.close()
        writing_file.close()

    def delete_local_note(self, timestamp):
        """Removes note at timestamp from file"""
        self.backup_notes()
        log = open(self.get_notes_file_location(), "r+", encoding="utf8").readlines()
        writing_file = open(self.get_notes_file_location(), "w", encoding="utf8")
        for line in log:
            if line.find(self.build_note_line(timestamp, '')) != 0:
                writing_file.write(line)
        writing_file.close()

    def find_local_notes(self, search_request):
        """Searches notes file for given request"""
        results = []

        reading_file = open(self.get_notes_file_location(), "r+", encoding="utf8")
        for line in reading_file:
            matching_line = True

            for term in search_request.inclusion_terms:
                if not re.search(r'\b(%s)\b' % term, line):
                    matching_line = False
                    break

            if not matching_line:
                continue

            for term in search_request.exclusion_terms:
                if re.search(r'\b(%s)\b' % term, line):
                    matching_line = False
                    break

            if not matching_line:
                continue

            timestamp, note = self.parse_note_line(line)

            if search_request.date:
                pattern = re.compile(
                    search_request.date.strftime("%a %b %d [^ ]+ %Y"))
                if not pattern.match(timestamp):
                    continue

            if note:
                epoch = datestring_to_timestamp(timestamp)
                results.append((epoch, note))
        return results

    def get_notes_file_location(self):
        """Returns the note file location from the config"""
        config = ashaw_notes.utils.configuration.load_config()
        return config.get(self.config_section, 'location')

    def use_backup(self):
        """Checks if local backups are enabled"""
        config = ashaw_notes.utils.configuration.load_config()
        return config.get(self.config_section, 'create_backup')

    def backup_notes(self):
        """Creates a local backup of the notes file"""
        if not self.use_backup():
            return
        if os.path.isfile(self.get_notes_file_location()):
            shutil.copyfile(self.get_notes_file_location(), "%s.bak" % self.get_notes_file_location())

    def restore_from_backup(self):
        """Restores previous note file"""
        if not self.use_backup():
            return
        shutil.copyfile("%s.bak" % self.get_notes_file_location(), self.get_notes_file_location())

    def is_header_found(self, file, timestamp):
        """Checks for header in file"""
        if not file:
            return False

        header = self.get_date_header(timestamp)
        for line in file:
            if "%s\n" % header == line:
                return True
        return False

    @staticmethod
    def get_date_header(timestamp):
        """Builds header"""
        return ashaw_notes.utils.search.timestamp_to_datestring(timestamp, False)

    def write_header(self, file, note):
        """Writes header to file"""
        self.write_line(file, "==========")
        self.write_line(file, note)

    @staticmethod
    def build_note_line(timestamp, note):
        """Generates a note line for insertion"""
        return "[%s] %s" % (
            ashaw_notes.utils.search.timestamp_to_datestring(timestamp), note)

    def parse_note_line(self, notes_line):
        """Rips apart note line into its timestamp and note"""
        line = self.__line_regex__.findall(notes_line)
        if line:
            return line[0][0], line[0][1]
        return None, None

    @staticmethod
    def write_line(file, line):
        """Writes line to file"""
        file.write("%s\n" % line)
