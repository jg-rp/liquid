from liquid import DictLoader
from liquid import Environment
from liquid.exceptions import TemplateNotFound
from liquid.loader import TemplateSource


class MatterDictLoader(DictLoader):
    def __init__(
        self,
        templates: dict[str, str],
        matter: dict[str, dict[str, object]],
    ):
        super().__init__(templates)
        self.matter = matter

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        try:
            source = self.templates[template_name]
        except KeyError as err:
            raise TemplateNotFound(template_name) from err

        return TemplateSource(
            source=source,
            filename=template_name,
            uptodate=None,
            matter=self.matter.get(template_name),
        )


def test_matter_loader() -> None:
    """Test that template loaders can add to render context."""
    loader = MatterDictLoader(
        templates={
            "some": "Hello, {{ you }}{{ username }}!",
            "other": "Goodbye, {{ you }}{{ username }}.",
            "thing": "{{ you }}{{ username }}",
        },
        matter={
            "some": {"you": "World"},
            "other": {"username": "Smith"},
        },
    )

    env = Environment(loader=loader)

    template = env.get_template("some")
    assert template.render() == "Hello, World!"

    template = env.get_template("other")
    assert template.render() == "Goodbye, Smith."

    template = env.get_template("thing")
    assert template.render() == ""


def test_matter_global_priority() -> None:
    """Test that matter variables take priority over globals."""
    loader = MatterDictLoader(
        templates={"some": "Hello, {{ you }}!"},
        matter={"some": {"you": "Liquid"}},
    )

    env = Environment(loader=loader, globals={"you": "World"})
    template = env.get_template("some", globals={"you": "Jinja"})

    assert template.render() == "Hello, Liquid!"


def test_matter_local_priority() -> None:
    """Test that render args take priority over matter variables."""
    loader = MatterDictLoader(
        templates={"some": "Hello, {{ you }}!"},
        matter={"some": {"you": "Liquid"}},
    )

    env = Environment(loader=loader)
    template = env.get_template("some")

    assert template.render(you="John") == "Hello, John!"
