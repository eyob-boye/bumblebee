import re

def clean_c_cc_comments(istr):
    """
    Given an input string that represents a c
    code, the function strips the
      c /* */ comments
      cpp // comments
      trailing white spaces
      blank lines
    It returns the cleaned string.
    """
    c_comments = r'/\*(?:.|[\r\n])*?.*\*/'
    cpp_comments = r'//.*$'
    special_cpp_comments = r'//.*/\*.*$'
    # Get rid of cpp like comments that contain c comment openers...
    # Comments such as  // bla bla /* bla bla
    clean_str = re.compile(special_cpp_comments,re.MULTILINE).sub('',istr)
    # Then clean up the c comments, if there are nested cpp comments
    # they will be clean up.
    clean_str = re.compile(c_comments,re.MULTILINE).sub('',clean_str)
    # Finally cleaup all the cpp comments
    clean_str = re.compile(cpp_comments,re.MULTILINE).sub('',clean_str)
    # Clean up the trailing white spaces
    clean_str = re.compile(r'\s+$',re.MULTILINE).sub('',clean_str)
    # Clean up blank lines
    clean_str = re.compile(r'^\n',re.MULTILINE).sub('',clean_str)
    return clean_str