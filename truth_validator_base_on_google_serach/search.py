# -----------------------------------------------------------------------------
# I decided not to divide this module to smallest because from my point of view
# generally it has only one responsibility. Maybe we have here a fun to count
# substring but it have strong dependency to InputError so it will require new
# imports that badly effects this project.
# -----------------------------------------------------------------------------

import requests
from googleapiclient.discovery import build

# -----------------------------------------------------------------------------
# Constants require by google cse
my_api_key3 = 'AIzaSyAffjZ8HBUda3Zx0kAMHgBuijFcg1Y728Y'
my_api_key2 = 'AIzaSyAsIjxZpXf9ANNQbgJfI5mzAdF7zDr4keY'
my_api_key = 'AIzaSyDS-EySo1dfqUyN9CkigcZpbKVzxH1CEqM'
my_cse_id = "009762290705935037254:wqirt74az30"
common_words = ['a', 'the', 'an', 'is', 'are', 'I', 'and', 'or', 'he', 'you']


# -----------------------------------------------------------------------------
# Exception to handle connect errors and wrong inputs
class Error(Exception):
    pass


class ConnectError(Error):
    def __init__(self, message):
        self.message = message


class InputError(Error):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


# -----------------------------------------------------------------------------
# The most important class. It provides main functionality and structure to
# store important data needed to interpret the problem
class ParseSearchTerm:
    def __init__(self, search_term):
        if type(search_term) != str or len(search_term) == 0:
            raise InputError('ParseSearchTeram.__init__',
                             'search_term must be not empty string')
        if count_sub_strings(search_term, ' ') == len(search_term):
            raise InputError('ParseSearchTeram.__init__',
                             'search_term must be not only white chars')
        self.search_term = search_term
        self.split_search_term = dict()
        for elem in str.split(self.search_term, " "):
            # This functionality moved to validate_truth
            # if elem not in ['a', 'the', 'an']:
            self.split_search_term[elem] = 0
        self.strong_occurrences = 0
        self.truth_ratio = 0
        self.not_common_words = list()
        self.new_statement_that_can_be_true = ''
        self.snippet_list = list()

    def add_occurrence(self, key, value):
        if key not in self.split_search_term.keys() or value <= 0 or \
                        type(value) != int:
            raise InputError('ParseSearchTeram.add_occurrence',
                             'key must be in split_search_term dictionary '
                             'and value mast be positive integer')
        self.split_search_term[key] += value

    def gen_new_truth(self):
        i = 1
        for elem in self.split_search_term.items():
            if elem[0] not in self.not_common_words:
                if i < len(self.split_search_term.keys()) - \
                        len(self.not_common_words):
                    self.new_statement_that_can_be_true += elem[0] + ' '
                else:
                    self.new_statement_that_can_be_true += elem[0]
                i += 1

    def validate_truth(self):
        if self.strong_occurrences > 0:
            self.truth_ratio = 0.5
        sum_occ = 0
        for elem in self.split_search_term.items():
            if elem[0] not in common_words:
                sum_occ += elem[1]
        for elem in self.split_search_term.items():
            if elem[1] < sum_occ / 100:
                self.not_common_words.append(elem[0])
        for elem in self.split_search_term.items():
            if elem[1] > sum_occ / 50:
                self.truth_ratio += 0.5 / len(self.split_search_term.keys())


# -----------------------------------------------------------------------------
# Class made for join google search result and be able to visits links
# It finds occurrences of whole phrases and each word
class SearchResult:
    def __init__(self, parse_search_term, snippet, link):
        if type(parse_search_term) != ParseSearchTerm:
            raise InputError('SearchResult.__init__',
                             'argument parse_search_term must be object of '
                             'class ParseSearchTerm')
        self.parse_search_term = parse_search_term
        self.snippet = snippet
        self.link = link

    def visit_link_and_search(self):
        try:
            r = requests.get(self.link)
        except Exception as e:
            raise ConnectError("Couldn't connect to: " + self.link + " " +
                               str(e))
        if r.status_code != 200:
            raise ConnectError("Couldn't connect to: " + self.link +
                               "\nRequest status code: " + str(r.status_code))
        if r.text.find(self.parse_search_term.search_term) != -1:
            self.parse_search_term.strong_occurrences += 1
            self.parse_search_term.snippet_list.append(
                "Found this phrase at page: " + self.link + "\n" +
                "Short info from page: " + self.snippet)
        else:
            for elem in self.parse_search_term.split_search_term.keys():
                repeats = count_sub_strings(r.text, elem)
                if repeats != 0:
                    self.parse_search_term.split_search_term[elem] += repeats


# -----------------------------------------------------------------------------
# The purpose of this class was to interpret the result stored in
# ParsedSearchTerm. Joining it together it breaks SRP
class SearchResultInterpreter:
    def __init__(self, parse_search_term):
        if type(parse_search_term) != ParseSearchTerm:
            raise InputError('SearchResultInterpreter.__init__',
                             'argument parse_search_term must be object of '
                             'class ParseSearchTerm')
        self.parse_search_term = parse_search_term

    def interpret(self):
        print("Report for statement: " + self.parse_search_term.search_term)
        number_of_chars = len(
            "Report for statement: " + self.parse_search_term.search_term)
        delimiter = ''
        for i in range(0, number_of_chars):
            delimiter += '-'
        print(delimiter)
        self.parse_search_term.validate_truth()
        self.parse_search_term.gen_new_truth()
        if self.parse_search_term.search_term != \
                self.parse_search_term.new_statement_that_can_be_true:
            print(
                "Statement that can be more real: " +
                self.parse_search_term.new_statement_that_can_be_true)
        print(
            "The truth ratio for: " + self.parse_search_term.search_term +
            " is: " + str(
                self.parse_search_term.truth_ratio))
        result_as_string = ''
        if 0 <= self.parse_search_term.truth_ratio < 0.15:
            result_as_string = 'highly unlikely to be true.'
        elif 0.3 > self.parse_search_term.truth_ratio >= 0.15:
            result_as_string = 'probably false.'
        elif 0.45 > self.parse_search_term.truth_ratio >= 0.3:
            result_as_string = 'probably false but really not sure.'
        elif 0.49 > self.parse_search_term.truth_ratio >= 0.45:
            result_as_string = 'probably false but really really not sure.'
        elif 0.49 <= self.parse_search_term.truth_ratio <= 0.51:
            result_as_string = 'not false and not true, cannot say.'
        elif 0.55 >= self.parse_search_term.truth_ratio > 0.51:
            result_as_string = 'probably true but really really not sure.'
        elif 0.55 >= self.parse_search_term.truth_ratio > 0.5:
            result_as_string = 'probably true but really really not sure.'
        elif 0.70 > self.parse_search_term.truth_ratio > 0.55:
            result_as_string = 'probably true really not sure.'
        elif 0.85 > self.parse_search_term.truth_ratio > 0.70:
            result_as_string = 'probably true.'
        elif 1 >= self.parse_search_term.truth_ratio >= 0.75:
            result_as_string = 'higly likely to be true. '
        print("This means that this statement is: " + result_as_string)
        for elem in self.parse_search_term.snippet_list:
            print(elem)


# -----------------------------------------------------------------------------
# Counting substring in a main string
def count_sub_strings(main_str, sub_str):
    if type(main_str) != str or type(sub_str) != str:
        raise InputError('count_sub_strings',
                         "a_str and sub should be strings")
    start = 0
    i = 0
    while True:
        start = main_str.find(sub_str, start)
        if start == -1:
            return i
        i += 1
        start += len(sub_str)


# -----------------------------------------------------------------------------
# This function returns the list of SearchResults find by googleapiclient
def google_search(search_term):
    if type(search_term) != ParseSearchTerm:
        raise InputError('google_search',
                         'search_term must be type of ParseSearchTerm')
    try:
        service = build("customsearch", "v1", developerKey=my_api_key)
        res = service.cse().list(q=search_term.search_term, cx=my_cse_id,
                                 num=10).execute()
    except Exception as ex:
        # Exception provides __str__ so it can be convert to string.
        # I provides new class of exception to be able to segregate them.
        raise ConnectError("Couldn't connect to google api! " + str(ex))

    result = res['items']
    search_return = []
    for elem in result:
        search_return.append(
            SearchResult(search_term, elem.get('snippet'), elem.get('link')))
    return search_return


# -----------------------------------------------------------------------------
# Joins whole functionality and provides simple API that require state as
# a string and return the truth ratio. Maybe I should think about options that
# will disable the printing information.
def prepare_search_and_return(statement):
    # It return truth ratio <0,1> where 1 is total true.
    # Possible exception:
    # ConnectError - passed from googleapiclient.discovery
    # ConnectError - passed from this module function visit_link_and_search
    # InputError - raised by this function due to wrong parameter
    if type(statement) != str:
        raise InputError('prepare_search_and_return',
                         "Search statement should be string!")
    if statement[len(statement) - 1] == '.':
        statement = statement[:-1]

    parsed_statement = ParseSearchTerm(statement)
    try:
        search_results = google_search(parsed_statement)
    except ConnectError:
        raise
    for e in search_results:
        try:
            e.visit_link_and_search()
        except ConnectError as ce:
            # I have to catch exception and handle here to be able to visit
            # sites even tho one of them will rise ConnectError
            print(ce.message)
    interpreted_results = SearchResultInterpreter(parsed_statement)
    interpreted_results.interpret()
    return parsed_statement.truth_ratio


# -----------------------------------------------------------------------------
# module can be run
def main():
    try:
        phrase = input("Enter the phrase to be validate: ")
        prepare_search_and_return(phrase)
    except ConnectError as ce:
        print(ce.message)
    except InputError as ie:
        print(ie.message + " at function " + ie.expression)


if __name__ == "__main__":
    main()
