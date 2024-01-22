def f_prompt(prompt_in=None, **kwargs):
    if prompt_in in known_f_prompts:
        prompt_in = known_f_prompts[prompt_in]
    formatted_prompt = prompt_in.format(**kwargs)
    return formatted_prompt


known_f_prompts = dict(
    obj_in_sentence="List the physical objects referenced in the sentence. \n [Example] \n Sentence: 'Do research and find evidence or maps that lead to the treasures whereabouts' \n Objects: 1. evidence \n 2. map \n 2. treasure. \n [Query] \n Sentence: '{point}' \n Objects: ",
    tf_obj_possession="True or False: In the sentence '{point}',  {the_characters} need to possessed or acquired {obj} to use it.",
    tf_change_loc="True or False: it is possible the {the_characters} can successfully '{point}' while staying at {loc}.",
    tf_deepening="True or False: it is possible for {the_characters} to successfully '{point}' by only {str_of_subtasks}. [Context] \n story: \n {story}.",
)

