import collections
import dataclasses
import typing
import uuid


class Styler(typing.Protocol):
    def apply(self, target: str | int) -> None:
        ...


class _DefaultDict[K, V]:
    def __call__(self) -> dict[K, list[V]]:
        return collections.defaultdict(list)


@dataclasses.dataclass
class TagStyler:
    tag_to_classes: dict[str | int, list[str]] = dataclasses.field(default_factory=_DefaultDict[str | int, str]())
    class_to_tags: dict[str, list[str | int]] = dataclasses.field(default_factory=_DefaultDict[str, str | int]())
    class_to_stylers: dict[str, list[Styler]] = dataclasses.field(default_factory=_DefaultDict[str, Styler]())
    _apply_tag_buffer: list[str | int] = dataclasses.field(default_factory=list)
    _apply_class_buffer: list[str] = dataclasses.field(default_factory=list)

    def tag(self, *classes: str, tag: str | int | None = None) -> str | int:
        if tag is None:
            tag = str(uuid.uuid4())
        self.tag_to_classes[tag].extend(classes)
        self._apply_tag_buffer.append(tag)

        return tag

    def style(self, class_: str, *stylers: Styler):
        self.class_to_stylers[class_].extend(stylers)
        self._apply_class_buffer.append(class_)

    def apply(self):
        tags = set(self._apply_tag_buffer)
        for class_ in self._apply_class_buffer:
            for tag in self.class_to_tags[class_]:
                tags.add(tag)
        for tag in tags:
            for class_ in self.tag_to_classes[tag]:
                for styler in self.class_to_stylers[class_]:
                    styler.apply(tag)
        self._apply_class_buffer.clear()
        self._apply_tag_buffer.clear()
