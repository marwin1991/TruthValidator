import pytest

from truth_validator_base_on_google_serach.search import ConnectError
from truth_validator_base_on_google_serach.search import InputError
from truth_validator_base_on_google_serach.search import ParseSearchTerm
from truth_validator_base_on_google_serach.search import SearchResult
from truth_validator_base_on_google_serach.search import \
    SearchResultInterpreter
from truth_validator_base_on_google_serach.search import count_sub_strings
from truth_validator_base_on_google_serach.search import google_search
from truth_validator_base_on_google_serach.search import \
    prepare_search_and_return


# -----------------------------------------------------------------------------
# Test for count_sub_string function
def test_count_sub_strings_good_values():
    assert 3 == count_sub_strings('aaa', 'a')
    assert 0 == count_sub_strings('aaa', 'aaaaa')


def test_count_sub_strings_wrong_first_value():
    with pytest.raises(InputError):
        count_sub_strings(1, 'a')


def test_count_sub_strings_wrong_second_value():
    pytest.raises(InputError, count_sub_strings, 'abc', 0.4)


def test_count_sub_strings_wrong_both_values():
    pytest.raises(InputError, count_sub_strings, 5, 0.4)


# -----------------------------------------------------------------------------
# Test for google_search function
def test_google_search_wrong_arg():
    with pytest.raises(InputError):
        google_search("aaaaa")


# -----------------------------------------------------------------------------
# Test class ParseSearchTerm
# init
def test_parse_search_term_class_init_good_value():
    assert type(ParseSearchTerm('search_term')) == ParseSearchTerm


def test_parse_search_term_class_init_wrong_value():
    with pytest.raises(InputError):
        ParseSearchTerm(1)


def test_parse_search_term_class_init_empty_value():
    with pytest.raises(InputError):
        ParseSearchTerm('')


def test_parse_search_term_class_init_spaces_value():
    with pytest.raises(InputError):
        ParseSearchTerm('   ')


# add_occurrence
def test_parse_search_term_class_add_occurrence_good_value():
    p = ParseSearchTerm('a b')
    p.add_occurrence('a', 1)
    assert p.split_search_term['a'] == 1


def test_parse_search_term_class_add_occurrence_minus_value():
    p = ParseSearchTerm('a b')
    with pytest.raises(InputError):
        p.add_occurrence('a', -1)


def test_parse_search_term_class_add_occurrence_float_value():
    p = ParseSearchTerm('a b')
    with pytest.raises(InputError):
        p.add_occurrence('a', 4.2)


def test_parse_search_term_class_add_occurrence_wrong_key():
    p = ParseSearchTerm('a b')
    with pytest.raises(InputError):
        p.add_occurrence('c', 2)


# gen_new_truth
def test_parse_search_term_class_gen_new_truth_good_value_beginning():
    p = ParseSearchTerm('a b c')
    p.not_common_words.append('a')
    p.gen_new_truth()
    assert p.new_statement_that_can_be_true == 'b c'


def test_parse_search_term_class_gen_new_truth_good_value_middle():
    p = ParseSearchTerm('a b c')
    p.not_common_words.append('b')
    p.gen_new_truth()
    assert p.new_statement_that_can_be_true == 'a c'


def test_parse_search_term_class_gen_new_truth_good_value_end():
    p = ParseSearchTerm('a b c')
    p.not_common_words.append('c')
    p.gen_new_truth()
    assert p.new_statement_that_can_be_true == 'a b'


# validate_truth
def test_parse_search_term_class_validate_truth_good_values():
    p = ParseSearchTerm('abc')
    p.not_common_words.append('abc')
    p.strong_occurrences += 1
    p.add_occurrence('abc', 1)
    p.validate_truth()
    assert p.truth_ratio == 1


def test_parse_search_term_class_validate_truth_good_values2():
    p = ParseSearchTerm('abc')
    p.not_common_words.append('abc')
    p.add_occurrence('abc', 1)
    p.validate_truth()
    assert p.truth_ratio == 0.5


# -----------------------------------------------------------------------------
# Test class SearchResult
# init
def test_search_result_class_init_good_vales():
    p = ParseSearchTerm('abc')
    s = SearchResult(p, 'abc', 'abc')
    assert type(s) == SearchResult


def test_search_result_class_init_wrong_vales():
    with pytest.raises(InputError):
        SearchResult('abc', 'abc', 'abc')


# visit_link_and_search
def test_search_result_class_visit_link_and_search_wrong_link():
    p = ParseSearchTerm('abc')
    s = SearchResult(p, 'abc', 'abc')
    with pytest.raises(ConnectError):
        s.visit_link_and_search()


# -----------------------------------------------------------------------------
# Test class SearchResultInterpreter
# init
def test_search_result_interpreter_class_init_good_vales():
    p = ParseSearchTerm('abc')
    s = SearchResultInterpreter(p)
    assert type(s) == SearchResultInterpreter


def test_search_result_interpreter_class_init_wrong_vales():
    with pytest.raises(InputError):
        SearchResultInterpreter('a')


# -----------------------------------------------------------------------------
# Test function prepare_search_and_return
def test_prepare_search_and_return_wrong_statement():
    with pytest.raises(InputError):
        prepare_search_and_return(1)


if __name__ == '__main__':
    pytest.main()
