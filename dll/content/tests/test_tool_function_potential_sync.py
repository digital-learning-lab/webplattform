from django.test import override_settings

from dll.content.models import Tool, ToolFunction, Potential
from dll.content.tests.test_content_views import BaseTestCase


class ToolFunctionPotentialTestCase(BaseTestCase):
    def setUp(self):
        super(ToolFunctionPotentialTestCase, self).setUp()
        self.function = ToolFunction.objects.create(title="Test")
        self.potential = Potential.objects.create(name="Test")
        self.potential.function = self.function
        self.potential.save()

    @override_settings(SITE_ID=1)
    def test_tool_function_add(self):
        tool = Tool.objects.drafts().first()
        tool.functions.add(self.function)
        tool.save()
        self.assertEqual(tool.functions.count(), 1)
        self.assertEqual(tool.potentials.count(), 1)
        self.assertEqual(tool.potentials.first(), self.potential)

    @override_settings(SITE_ID=2)
    def test_tool_potential_add(self):
        tool = Tool.objects.drafts().first()
        tool.potentials.add(self.potential)
        tool.save()
        self.assertEqual(tool.functions.count(), 1)
        self.assertEqual(tool.potentials.count(), 1)
        self.assertEqual(tool.potentials.first(), self.potential)

    @override_settings(SITE_ID=1)
    def test_tool_function_remove(self):
        tool = Tool.objects.drafts().first()
        tool.functions.add(self.function)
        tool.save()
        self.assertEqual(tool.functions.count(), 1)
        self.assertEqual(tool.potentials.count(), 1)
        self.assertEqual(tool.potentials.first(), self.potential)
        tool.functions.remove(self.function)
        tool.save()
        self.assertEqual(tool.functions.count(), 0)
        self.assertEqual(tool.potentials.count(), 0)

    @override_settings(SITE_ID=2)
    def test_tool_potential_remove(self):
        tool = Tool.objects.drafts().first()
        tool.potentials.add(self.potential)
        tool.save()
        self.assertEqual(tool.functions.count(), 1)
        self.assertEqual(tool.potentials.count(), 1)
        self.assertEqual(tool.potentials.first(), self.potential)
        tool.potentials.remove(self.potential)
        tool.save()
        self.assertEqual(tool.functions.count(), 0)
        self.assertEqual(tool.potentials.count(), 0)
