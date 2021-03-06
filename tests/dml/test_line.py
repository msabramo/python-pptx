# encoding: utf-8

"""
Test suite for pptx.dml.line module
"""

from __future__ import absolute_import, print_function, unicode_literals

import pytest

from pptx.dml.color import ColorFormat
from pptx.dml.fill import FillFormat
from pptx.dml.line import LineFormat
from pptx.enum.dml import MSO_FILL
from pptx.oxml.shapes.shared import CT_LineProperties
from pptx.shapes.autoshape import Shape

from ..oxml.unitdata.dml import an_ln
from ..unitutil.mock import call, class_mock, instance_mock, property_mock


class DescribeLineFormat(object):

    def it_knows_the_line_width(self, width_get_fixture):
        line, expected_line_width = width_get_fixture
        assert line.width == expected_line_width

    def it_can_change_its_width(self, width_set_fixture):
        line, width, expected_xml = width_set_fixture
        line.width = width
        assert line._ln.xml == expected_xml

    def it_has_a_fill(self, fill_fixture):
        line, FillFormat_, ln_, fill_ = fill_fixture
        fill = line.fill
        FillFormat_.from_fill_parent.assert_called_once_with(ln_)
        assert fill is fill_

    def it_has_a_color(self, color_fixture):
        line, fill_, expected_solid_calls, color_ = color_fixture
        color = line.color
        assert fill_.solid.mock_calls == expected_solid_calls
        assert color is color_

    # fixtures -------------------------------------------------------

    @pytest.fixture(params=[
        (MSO_FILL.SOLID,      False),
        (MSO_FILL.BACKGROUND, True),
        (None,                True),
    ])
    def color_fixture(self, request, line, fill_prop_, fill_, color_):
        pre_call_fill_type, solid_call_expected = request.param
        fill_.type = pre_call_fill_type
        expected_solid_calls = [call()] if solid_call_expected else []
        return line, fill_, expected_solid_calls, color_

    @pytest.fixture
    def fill_fixture(self, line, FillFormat_, ln_, fill_):
        return line, FillFormat_, ln_, fill_

    @pytest.fixture(params=[(None, 0), (12700, 12700)])
    def width_get_fixture(self, request, shape_):
        w, expected_line_width = request.param
        shape_.ln = self.ln_bldr(w).element
        line = LineFormat(shape_)
        return line, expected_line_width

    @pytest.fixture(params=[
        (None, None), (None, 12700), (12700, 12700), (12700, 25400),
        (25400, None),
    ])
    def width_set_fixture(self, request, shape_):
        initial_width, width = request.param
        shape_.ln = shape_.get_or_add_ln.return_value = (
            self.ln_bldr(initial_width).element
        )
        line = LineFormat(shape_)
        expected_xml = self.ln_bldr(width).xml()
        return line, width, expected_xml

    # fixture components ---------------------------------------------

    @pytest.fixture
    def color_(self, request):
        return instance_mock(request, ColorFormat)

    @pytest.fixture
    def fill_(self, request, color_):
        return instance_mock(request, FillFormat, fore_color=color_)

    @pytest.fixture
    def fill_prop_(self, request, fill_):
        return property_mock(request, LineFormat, 'fill', return_value=fill_)

    @pytest.fixture
    def FillFormat_(self, request, fill_):
        FillFormat_ = class_mock(request, 'pptx.dml.line.FillFormat')
        FillFormat_.from_fill_parent.return_value = fill_
        return FillFormat_

    @pytest.fixture
    def line(self, shape_):
        return LineFormat(shape_)

    @pytest.fixture
    def ln_(self, request):
        return instance_mock(request, CT_LineProperties)

    def ln_bldr(self, w):
        ln_bldr = an_ln().with_nsdecls()
        if w is not None:
            ln_bldr.with_w(w)
        return ln_bldr

    @pytest.fixture
    def shape_(self, request, ln_):
        shape_ = instance_mock(request, Shape)
        shape_.get_or_add_ln.return_value = ln_
        return shape_
