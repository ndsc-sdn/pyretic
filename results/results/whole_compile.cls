classifier size: 32
print : match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 1)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 3)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 3)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([modify: ('outport', 3) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([])
 identity
  -> set([]) 
---------------------------------
classifier size: 32
print : match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 1)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 3)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 3)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([modify: ('outport', 3) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([])
 identity
  -> set([]) 
---------------------------------
classifier size: 32
print : match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 1)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 3)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 3)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([modify: ('outport', 3) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([])
 identity
  -> set([]) 
---------------------------------
classifier size: 32
print : match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([Controller, modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 1)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 3)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 3)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([modify: ('outport', 3) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([])
 identity
  -> set([]) 
---------------------------------
classifier size: 32
print : match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([Controller, modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4)])
 match: ('vlan_pcp', 0) ('switch', 1) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('switch', 1) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 1)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('vlan_pcp', 0) ('switch', 3) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 0)
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 4), Controller])
 match: ('switch', 3) ('vlan_pcp', 0) ('vlan_id', 0)
  -> set([])
 match: ('switch', 3)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.1/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 1)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.1/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.2/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 3)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.2/32')) ('vlan_id', 5)
  -> set([])
 match: ('dstip', IPv4Network('10.0.0.3/32')) ('switch', 2) ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([modify: ('outport', 2)])
 match: ('vlan_pcp', 0) ('dstip', IPv4Network('10.0.0.3/32')) ('vlan_id', 5)
  -> set([])
 match: ('vlan_pcp', 0) ('vlan_id', 5)
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([modify: ('outport', 1) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.1/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([modify: ('outport', 3) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.2/32'))
  -> set([])
 match: ('switch', 2) ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([modify: ('outport', 2) ('vlan_pcp', 0) ('vlan_id', 5)])
 match: ('dstip', IPv4Network('10.0.0.3/32'))
  -> set([])
 identity
  -> set([]) 
---------------------------------