from pyramid.events import subscriber
from pyramid.events import BeforeRender
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.security import Allow, Everyone, remember, forget
from pyramid.view import view_config, forbidden_view_config

from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('betty')

from sqlalchemy.sql import func
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound

from .models import *
from .models.model import *
from .models import user as __user
from .models.user import User
from .models.item import Item

from .utility import post_stripe_payment

import chezbetty.datalayer as datalayer

import traceback



@view_config(route_name='about', renderer='templates/public/about.jinja2')
def about(request):
    return {}


@view_config(route_name='items', renderer='templates/public/items.jinja2')
def items(request):
    items = DBSession.query(Item)\
                     .filter(Item.enabled==True)\
                     .filter(Item.in_stock>0)\
                     .order_by(Item.name).all()
    out_of_stock_items = DBSession.query(Item)\
                     .filter(Item.enabled==True)\
                     .filter(Item.in_stock==0)\
                     .order_by(Item.name).all()
    disabled_items = DBSession.query(Item)\
                     .filter(Item.enabled==False)\
                     .order_by(Item.name).all()
    return {'items': items,
            'out_of_stock_items': out_of_stock_items,
            'disabled_items': disabled_items}


@view_config(route_name='paydebt', renderer='templates/public/paydebt.jinja2')
def paydebt(request):
    uniqname = request.matchdict['uniqname']
    user = User.from_uniqname(uniqname, local_only=True)

    # Calculate all of the important balance metrics server side
    values = {}
    for newval in [0, 10, 25, 50, 100]:
        amount      = newval - user.balance  # how much will go into the user's account
        total       = (amount + Decimal('0.3')) / Decimal('0.971') # how much we must charge to offset stripe
        fee         = total - amount         # how much more to make stripe happy
        total_cents = (total*100).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        values[newval] = {
            'amount': amount,
            'total': total,
            'fee': fee,
            'total_cents': total_cents
        }

    return {'user': user,
            'stripe_pk': request.registry.settings['stripe.publishable_key'],
            'values': values}


@view_config(route_name='paydebt_submit',
             request_method='POST',
             renderer='json')
def paydebt_submit(request):
    uniqname = request.matchdict['uniqname']
    user = User.from_uniqname(uniqname, local_only=True)

    token = request.POST['stripeToken']
    amount = Decimal(request.POST['betty_amount'])
    total_cents = int(request.POST['betty_total_cents'])

    post_stripe_payment(
            datalayer,
            request,
            token,
            amount,
            total_cents,
            user,
            user)

    return {}
