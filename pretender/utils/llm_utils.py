def tidy_llm_list_string(llm_list_string, strip_nums=True):
    if type(llm_list_string) is str:
        llm_list = llm_list_string.split('\n')
        if len(llm_list) == 1 and len(llm_list_string.split(',')) > 1:
            print('WARNING: splitting on commas')  # TODO balloch: make this a real warning
            llm_list = llm_list_string.split(',')
    else:
        llm_list = llm_list_string
    if strip_nums:
        return [s.lstrip('0123456789 .').rstrip(' .').strip() for s in llm_list]
    return [s.strip() for s in llm_list]

