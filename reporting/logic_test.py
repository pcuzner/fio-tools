#!/usr/bin/env python

__author__ = 'paul'

import sys

tb_required = float(sys.argv[1])
gb_required = tb_required * 1024
cost = 0
total_cost = 0

if gb_required > 1024000:
    charge = gb_required - 1024000
    cost = charge * 0.0224
    total_cost  = cost
    print "charge for %d at rate 0.0224 is %d" % (charge, cost)
    gb_required = gb_required - (gb_required - 1024000)

if gb_required > 512000:
    charge = gb_required - 512000
    cost = charge * 0.0228
    total_cost += cost
    print "charge for %d at rate 0.0228 is %d" % (charge, cost)
    gb_required = gb_required - (gb_required - 512000)

if gb_required > 51200:
    charge = gb_required - 51200
    cost = charge * 0.0232
    total_cost += cost
    print "charge for %d at rate 0.0232 is %d" % (charge, cost)
    gb_required = gb_required - (gb_required - 51200)

if gb_required > 1024:
    charge = gb_required - 1024
    cost = charge * 0.0236
    total_cost += cost
    print "charge for %d at rate 0.0236 is %d" % (charge, cost)
    gb_required = gb_required - (gb_required - 1024)

if gb_required > 0:
    charge = gb_required
    cost = gb_required * 0.024
    total_cost += cost
    print "charge for %d at rate 0.024 is %d" % (charge, cost)






print tb_required
print gb_required
print str(total_cost)
