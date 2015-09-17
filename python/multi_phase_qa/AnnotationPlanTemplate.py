__author__ = 'ha'


PLANS_ONE_FINDING = {
  "accepted_code": [[(0,"accept")]],

  "rejected_code": [[(0,"reject")]],

   "accepted_qa1":[
      [(0, "accept"), (0, "accept")],
      [(0, "reject"), (0, "accept")]
  ],

  "rejected_qa1":[
      [(0, "accept"), (0, "reject")],
      [(0, "reject"), (0, "reject")]
  ],

   "accepted_qa2":[
      [(0, "accept"), (0, "accept"), (0, "accept")],
      [(0, "accept"), (0, "reject"), (0, "accept")],
      [(0, "reject"), (0, "accept"), (0, "accept")],
      [(0, "reject"), (0, "reject"), (0, "accept")]
  ],

   "rejected_qa2":[
      [(0, "accept"), (0, "accept"), (0, "reject")],
      [(0, "accept"), (0, "reject"), (0, "reject")],
      [(0, "reject"), (0, "reject"), (0, "reject")],
      [(0, "reject"), (0, "accept"), (0, "reject")]
  ],

   "accepted_qa3":[
      [(0, "accept"), (0, "accept"), (0, "accept"), (0, "accept")],
      [(0, "accept"), (0, "accept"), (0, "reject"), (0, "accept")],
      [(0, "accept"), (0, "reject"), (0, "accept"), (0, "accept")],
      [(0, "accept"), (0, "reject"), (0, "reject"), (0, "accept")],
      [(0, "reject"), (0, "accept"), (0, "accept"), (0, "accept")],
      [(0, "reject"), (0, "reject"), (0, "accept"), (0, "accept")],
      [(0, "reject"), (0, "reject"), (0, "reject"), (0, "accept")]
  ],

   "rejected_qa3":[
      [(0, "accept"), (0, "accept"), (0, "accept"), (0, "reject")],
      [(0, "accept"), (0, "accept"), (0, "reject"), (0, "reject")],
      [(0, "accept"), (0, "reject"), (0, "accept"), (0, "reject")],
      [(0, "accept"), (0, "reject"), (0, "reject"), (0, "reject")],
      [(0, "reject"), (0, "accept"), (0, "accept"), (0, "reject")],
      [(0, "reject"), (0, "reject"), (0, "accept"), (0, "reject")],
      [(0, "reject"), (0, "reject"), (0, "reject"), (0, "reject")]
  ],
}
plans = []
for k,v in zip(PLANS_ONE_FINDING.keys(), PLANS_ONE_FINDING.values()):
  plan = {"state": k}
  for steps in v:
    plan["steps"] = steps
    plans.append(plan)

PLANS_OPPS_WITH_ONE_FINDING = plans


PLANS_TWO_FINDINGS = {
  "accepted_code": [[(0,"accept")]],

  "rejected_code": [[(0, "reject") , (1, "reject")]],

  "rejected_moreFindings_code": [[(0,"reject")]],

  "accepted_qa1": [
    [(0, "accept") , (0, "accept")],
    [(0, "reject"), (1, "reject"), (1, "accept")],
    [(0, "reject"), (1, "accept"), (1, "accept")],
  ],

  "rejected_qa1": [
    [(0, "accept") , (1, "reject"), (1, "reject")],
  ],

  "rejected_moreFindings_qa1": [[(0,"accept"), (0, "reject")]],

   "accepted_qa2":[
      [(0, "accept"), (0, "accept"), (0, "accept")],
      [(0, "accept"), (0, "reject"), (1, "accept"), (1, "accept"), (1, "accept")]
  ],
}

PLANS_TWO_FINDINGS = {}

plans = []
for k,v in zip(PLANS_TWO_FINDINGS.keys(), PLANS_TWO_FINDINGS.values()):
  plan = {"state": k}
  for steps in v:
    plan["steps"] = steps
    plans.append(plan)

PLANS_OPPS_WITH_TWO_FINDINGS = plans