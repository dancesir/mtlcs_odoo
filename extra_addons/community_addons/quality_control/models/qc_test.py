# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class QcTest(models.Model):
    """A test is a group of questions to with the values that make them valid.
    """
    _name = 'qc.test'
    _description = 'Quality control test'

    @api.multi
    def _links_get(self):
        link_obj = self.env['res.request.link']
        return [(r.object, r.name) for r in link_obj.search([])]

    active = fields.Boolean(u'有效', default=True)
    name = fields.Char(
        string=u'模版名称', required=True, translate=True, select=True)
    test_lines = fields.One2many(
        comodel_name='qc.test.question', inverse_name='test',
        string=u'明细', copy=True)
    object_id = fields.Reference(
        string=u'关联对象', selection=_links_get,)
    fill_correct_values = fields.Boolean(
        string=u'预先填充合格值')
    type = fields.Selection(
        [('generic', u'普通'),
         ('related', u'引用')],
        string=u'类型', select=True, required=True, default='generic')
    category = fields.Many2one(
        comodel_name='qc.test.category', string=u'分类')
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'qc.test'))


class QcTestQuestion(models.Model):
    """Each test line is a question with its valid value(s)."""
    _name = 'qc.test.question'
    _description = 'Quality control question'
    _order = 'sequence, id'

    @api.one
    @api.constrains('ql_values')
    def _check_valid_answers(self):
        if self.type == 'quantitative':
            return
        for value in self.ql_values:
            if value.ok:
                return
        raise exceptions.Warning(
            _("There isn't any value with OK marked. You have to mark at "
              "least one."))

    @api.one
    @api.constrains('min_value', 'max_value')
    def _check_valid_range(self):
        if self.type == 'qualitative':
            return
        if self.min_value > self.max_value:
            raise exceptions.Warning(
                _("Minimum value can't be higher than maximum value."))

    sequence = fields.Integer(
        string=u'序列', required=True, default="10")
    test = fields.Many2one(comodel_name='qc.test', string=u'模版')
    name = fields.Char(
        string=u'内容', required=True, select=True, translate=True)
    type = fields.Selection(
        [('qualitative', u'定性'),
         ('quantitative', u'定量')], string='Type', required=True)
    ql_values = fields.One2many(
        comodel_name='qc.test.question.value', inverse_name="test_line",
        string=u'定性值', copy=True)
    notes = fields.Text(string=u'备注')
    min_value = fields.Float(string=u'最小', digits=(16, 5))
    max_value = fields.Float(string=u'最大', digits=(15, 5))
    uom_id = fields.Many2one(comodel_name='product.uom', string=u'单位')


class QcTestQuestionValue(models.Model):
    _name = 'qc.test.question.value'
    _description = 'Possible values of qualitative questions.'

    test_line = fields.Many2one(
        comodel_name="qc.test.question", string="Test question")
    name = fields.Char(
        string='Name', required=True, select=True, translate=True)
    ok = fields.Boolean(
        string=u'合格',
        help="When this field is marked, the answer is considered correct.")
