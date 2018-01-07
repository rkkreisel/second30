""" Generic Functions Used Across Modules """


def waitForProp(objectReference, propName):
    """ Pause Thread / Function Until Object Property is Populated """
    while True:
        try:
            while getattr(objectReference, propName) is None:
                pass
            return
        except AttributeError:
            pass
