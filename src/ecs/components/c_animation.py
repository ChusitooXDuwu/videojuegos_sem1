from typing import List

class CAnimation:
    def __init__(self, animation:dict) -> None:
        self.frames = animation["number_frames"]
        self.animations_list:List[AnimationData] = []
        for anim in animation["list"]:
            anim_data = AnimationData(anim["name"],anim["start"],
                                      anim["end"], anim["framerate"])
            self.animations_list.append(anim_data)
        self.current_animation = 0
        self.current_animation_time = 0
        self.curr_frame = self.animations_list[self.current_animation].start

class AnimationData:
    def __init__(self, name:str, start:int, end:int, framerate:float) -> None:
        self.name = name
        self.start = start
        self.end = end
        self.framerate = 1.0 / framerate