import pddlpy


DOMAIN_PDDL_PATH = "/home/suyash/eilab/playingpretend/alfworld_server/interfacer/data/domain.pddl"
# DOMAIN_PDDL_PATH = "/home/suyash/eilab/playingpretend/alfworld_server/alfworld/test.pddl"
STATE_PDDL_PATH = "/home/suyash/eilab/playingpretend/alfworld_server/alfworld/ALFWORLD_DATA/json_2.1.1/train/look_at_obj_in_light-AlarmClock-None-DeskLamp-301/trial_T20190907_174127_043461/initial_state.pddl"

domprob = pddlpy.DomainProblem(DOMAIN_PDDL_PATH, STATE_PDDL_PATH)

print(domprob.operators())

