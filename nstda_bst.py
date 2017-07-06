# -*- coding: utf-8 -*-
import datetime
from dateutil import relativedelta as rdelta
from openerp import tools, models, fields, api, exceptions, _

# from openerp.tools.translate import _
# from email import _name
# from openerp import tools
# from openerp import SUPERUSER_ID

    
####################################################################################################


class nstda_bst(models.Model):
    
    _name = 'nstda.bst'
    _auto = False