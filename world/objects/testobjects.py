#### Imports ####
from random import choice

from evennia.utils.utils import wrap

from world.typeclasses.objects import Object


#### WiseStone Test Object ####
class WiseStone(Object):
    """
    An object speaking when someone looks at it. We
    assume it looks like a stone in this example.
    """

    class_perm = {"create": "Beginner Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        new_obj_lockstring = super().get_default_lockstring(account, caller, **kwargs)
        return new_obj_lockstring

    def after_spawn(self, account=None, caller=None, **kwargs):
        super().after_spawn(caller=caller)

    def at_object_creation(self):
        "Called when object is first created"
        super().at_object_creation()

        self.db.wise_texts = [
            "Stones have feelings too.",
            "To live like a stone is to not have lived at all.",
            "The world is like a rock of chocolate.",
            "I'm sooo wise... Gosh, am I wise!",
            "Whereever you go, take your stone with you.",
            "What was life, if we didn't had the guts to be a stone.",
            "To be a stone or not to be a stone. There's no question.",
        ]

    def return_appearance(self, looker):
        """
        Called by the  look command. We want to return
        a wisdom when we get looked at.
        """
        desc = f"{self.db.desc}"
        desc += f"|/It grumbles and says: '|Y{choice(self.db.wise_texts)}|n'"
        return self.set_appearance(looker, desc=desc)


#### Flower Test Object ####
class Flower(Object):
    """
    This creates a simple flower object
    """

    class_perm = {"create": "Beginner Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        new_obj_lockstring = super().get_default_lockstring(account, caller, **kwargs)
        return new_obj_lockstring

    def after_spawn(self, account=None, caller=None, **kwargs):
        super().after_spawn(caller=caller)

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = "You see a beautiful and colorful flower."

    def return_appearance(self, looker):
        desc = f"{self.db.desc}"
        desc += f"|/This is a freshly picked |Y{self.key}|n."
        return self.set_appearance(looker, desc=desc)
