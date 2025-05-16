class DataStoringObject:
    """Base class providing a flexible key-value storage mechanism."""

    def __init__(self):
        """Initializes the internal data dictionary."""
        self.data = {}

    def set_data(self, *ident):
        """Sets multiple key-value pairs into the internal data dictionary.

        Args:
            *ident: Alternating sequence of keys and values.
        """
        for i in range(0, len(ident), 2):
            self.data[ident[i]] = ident[i + 1]

    def get_data(self, ident):
        """Retrieves the value associated with a given key.

        Args:
            ident (str): The key to look up.

        Returns:
            Any: The value associated with the key if it exists, else None.
        """
        if ident in self.data:
            return self.data[ident]

    def oper_data(self, ident, oper):
        """Applies an operation to a value associated with a given key.

        Args:
            ident (str): The key to operate on.
            oper (Callable): A function to apply to the current value.
        """
        self.data[ident] = oper(self.data[ident])


class SceneManager(DataStoringObject):
    """Manages scenes and timed events in the animation framework."""

    def __init__(self, scenes, events):
        """Initializes the SceneManager.

        Args:
            scenes (Iterable[Scene]): A list of scenes to manage.
            events (Iterable[Event]): A list of timed events to schedule.
        """
        super().__init__()

        self.scenes = {scene.name: scene for scene in scenes}
        self.events = {
            event.beat: [ev for ev in events if ev.beat == event.beat]
            for event in events
        }

        for scene in scenes:
            scene.set_parent(self)

        self.active_scene = []
        self.cur_beat = -1
        self.data = {}

    def start_scene(self, scene, at=0):
        """Starts a new scene, replacing any existing active scene.

        Args:
            scene (str): Name of the scene to start.
            at (int, optional): Beat to start the scene from. Defaults to 0.
        """
        if len(self.active_scene) == 0:
            self.active_scene.append(None)

        self.active_scene[0] = self.scenes[scene]
        self.active_scene[0].start(at)

    def add_scene(self, scene, at=0):
        """Adds a scene as a new layer.

        Args:
            scene (str): Name of the scene to add.
            at (int, optional): Beat to start the scene from. Defaults to 0.
        """
        self.active_scene.append(self.scenes[scene])
        self.active_scene[-1].start(at)

    def remove_scene(self, scene):
        """Removes a scene from active layers.

        Args:
            scene (str): Name of the scene to remove.
        """
        if self.scenes[scene] in self.active_scene:
            self.active_scene.remove(self.scenes[scene])

    def request_next(self, render=True):
        """Requests the next frame from all active scenes.

        Args:
            render (bool, optional): Whether to render the frame. Defaults to True.
        """
        for scene in self.active_scene:
            scene.request_frame(render)

        self.next_beat()

    def next_beat(self):
        """Advances the beat counter and triggers any scheduled events."""
        self.cur_beat += 1
        if self.cur_beat in self.events:
            for event in self.events[self.cur_beat]:
                event.do(self)

    def set_scene_data(self, scene, *ident):
        """Sets data for a given scene.

        Args:
            scene (str): Scene name.
            *ident: Alternating keys and values.
        """
        self.scenes[scene].set_data(*ident)

    def set_generator_data(self, scene, generator, *ident):
        """Sets data for a specific generator in a scene.

        Args:
            scene (str): Scene name.
            generator (int): Generator index.
            *ident: Alternating keys and values.
        """
        self.scenes[scene].generators[generator].set_data(*ident)


class Event:
    """Represents a scheduled action to perform at a specific beat."""

    def __init__(self, beat, do):
        """Initializes the event.

        Args:
            beat (int): Beat number at which the event occurs.
            do (Callable[[SceneManager], None]): The action to perform.
        """
        self.beat = beat
        self.do = do

    @staticmethod
    def swap_scene(sc, at=0):
        """Returns an action to replace the current scene.

        Args:
            sc (str): Scene name.
            at (int, optional): Beat to start the scene. Defaults to 0.

        Returns:
            Callable: SceneManager action.
        """
        return lambda sm: sm.start_scene(sc, at)

    @staticmethod
    def layer_scene(sc, at=0):
        """Returns an action to add a scene layer.

        Args:
            sc (str): Scene name.
            at (int, optional): Beat to start the scene. Defaults to 0.

        Returns:
            Callable: SceneManager action.
        """
        return lambda sm: sm.add_scene(sc, at)

    @staticmethod
    def remove_scene(sc):
        """Returns an action to remove a scene.

        Args:
            sc (str): Scene name.

        Returns:
            Callable: SceneManager action.
        """
        return lambda sm: sm.remove_scene(sc)


class Scene(DataStoringObject):
    """Encapsulates a group of generators and controls their lifecycle."""

    def __init__(self, name, generators):
        """Initializes the scene.

        Args:
            name (str): Scene name.
            generators (Iterable[Generator]): Generators involved in the scene.
        """
        super().__init__()

        self.parent = None
        self.name = name
        self.generators = generators
        self.start_beat = 0
        self.internal_beat = 0

    def set_parent(self, parent):
        """Sets the parent SceneManager.

        Args:
            parent (SceneManager): Parent manager.
        """
        self.parent = parent

    def request_frame(self, render=True):
        """Requests a frame update from all generators.

        Args:
            render (bool, optional): Whether to render the frame. Defaults to True.
        """
        beat = self.internal_beat
        if render:
            for generator in self.generators:
                if beat >= generator.start_beat and generator.condition(beat):
                    if beat != self.start_beat and beat != generator.start_beat:
                        generator.request_clear(generator, beat - 1)
                    generator.request(generator, beat)

        self.internal_beat += 1

    def start(self, at):
        """Starts the scene from the specified beat.

        Args:
            at (int): Beat to start from.
        """
        for generator in self.generators:
            generator.set_parent(self.parent)
            generator.set_scene(self)
            generator.on_create(generator)

        self.start_beat = at
        self.internal_beat = at
        self.request_frame()


class Generator(DataStoringObject):
    """Defines a unit of animation logic within a scene."""

    def __init__(self, start_beat, condition, on_create, request, request_clear):
        """Initializes the generator.

        Args:
            start_beat (int): Beat at which the generator starts.
            condition (Callable[[int], bool]): Condition for activation.
            on_create (Callable[[Generator], None]): Called when scene starts.
            request (Callable[[Generator, int], None]): Called to render.
            request_clear (Callable[[Generator, int], None]): Called to clear previous state.
        """
        super().__init__()

        self.parent = None
        self.scene = None
        self.start_beat = start_beat
        self.condition = condition
        self.on_create = on_create
        self.request = request
        self.request_clear = request_clear

    def set_parent(self, parent):
        """Sets the parent SceneManager.

        Args:
            parent (SceneManager): Parent manager.
        """
        self.parent = parent

    def set_scene(self, scene):
        """Sets the owning Scene.

        Args:
            scene (Scene): The scene this generator belongs to.
        """
        self.scene = scene

    @staticmethod
    def combine_conditions(*cond):
        """Combines multiple conditions using logical AND.

        Args:
            *cond (Callable[[int], bool]): Conditions to combine.

        Returns:
            Callable[[int], bool]: Combined condition.
        """
        return lambda b: all(c(b) for c in cond)

    @staticmethod
    def always():
        """Returns a condition that always evaluates to True."""
        return lambda b: True

    @staticmethod
    def every_n_beats(beat):
        """Returns a condition that is true every N beats."""
        return lambda b: b % beat == 0

    @staticmethod
    def every_on_off(on, off):
        """Returns a condition for on-off beat cycling (e.g. flashing).

        Args:
            on (int): Number of beats the condition is True.
            off (int): Number of beats the condition is False.

        Returns:
            Callable[[int], bool]: Beat-based condition.
        """
        return lambda b: (b % (on + off)) < on

    @staticmethod
    def every_off_on(off, on):
        """Returns a condition for off-on beat cycling.

        Args:
            off (int): Number of beats the condition is False.
            on (int): Number of beats the condition is True.

        Returns:
            Callable[[int], bool]: Beat-based condition.
        """
        return lambda b: (b % (on + off)) >= off

    @staticmethod
    def before_n(beat):
        """Returns a condition that is True before a given beat."""
        return lambda b: b < beat

    @staticmethod
    def at_beat(beat):
        """Returns a condition that is True only at a specific beat."""
        return lambda b: b == beat

    @staticmethod
    def no_create():
        """Returns a no-op for the on_create function."""
        return lambda g: None

    @staticmethod
    def no_request():
        """Returns a no-op for the request function."""
        return lambda g, b: None
