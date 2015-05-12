
################################################################################
# The Pyretic Project                                                          #
# frenetic-lang.org/pyretic                                                    #
# author: Joshua Reich (jreich@cs.princeton.edu)                               #
# author: Christopher Monsanto (chris@monsan.to)                               #
# author: Cole Schlesinger (cschlesi@cs.princeton.edu)                         #
################################################################################
# Licensed to the Pyretic Project by one or more contributors. See the         #
# NOTICES file distributed with this work for additional information           #
# regarding copyright and ownership. The Pyretic Project licenses this         #
# file to you under the following license.                                     #
#                                                                              #
# Redistribution and use in source and binary forms, with or without           #
# modification, are permitted provided the following conditions are met:       #
# - Redistributions of source code must retain the above copyright             #
#   notice, this list of conditions and the following disclaimer.              #
# - Redistributions in binary form must reproduce the above copyright          #
#   notice, this list of conditions and the following disclaimer in            #
#   the documentation or other materials provided with the distribution.       #
# - The names of the copyright holds and contributors may not be used to       #
#   endorse or promote products derived from this work without specific        #
#   prior written permission.                                                  #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT    #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the     #
# LICENSE file distributed with this work for specific language governing      #
# permissions and limitations under the License.                               #
################################################################################

# This module is designed for import *.
import functools
import itertools
import struct
import time
from ipaddr import IPv4Network
from bitarray import bitarray
import logging

from pyretic.core import util
from pyretic.core.network import *
from pyretic.core.classifier import Rule, Classifier
from pyretic.core.util import frozendict, singleton

from multiprocessing import Lock, Condition
import copy

from pyretic.evaluations import stat

NO_CACHE=False

basic_headers = ["srcmac", "dstmac", "srcip", "dstip", "tos", "srcport", "dstport",
                 "ethtype", "protocol"]
tagging_headers = ["vlan_id", "vlan_pcp"]
native_headers = basic_headers + tagging_headers
location_headers = ["switch", "inport", "outport"]
compilable_headers = native_headers + location_headers
content_headers = [ "raw", "header_len", "payload_len"]

################################################################################
# Policy Language                                                              #
################################################################################

class Policy(object):
    """
    Top-level abstract class for policies.
    All Pyretic policies have methods for

    - evaluating on a single packet.
    - compilation to a switch Classifier
    """
    def eval(self, pkt):
        """
        evaluate this policy on a single packet

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        raise NotImplementedError

    def invalidate_classifier(self):
        self._classifier = None

    def compile(self):
        """
        Produce a Classifier for this policy

        :rtype: Classifier
        """
        if NO_CACHE: 
            self._classifier = self.generate_classifier()
        return self._classifier

    def __add__(self, pol):
        """
        The parallel composition operator.

        :param pol: the Policy to the right of the operator
        :type pol: Policy
        :rtype: Parallel
        """
        if isinstance(pol,parallel):
            return parallel([self] + pol.policies)
        else:
            return parallel([self, pol])

    def __rshift__(self, other):
        """
        The sequential composition operator.

        :param pol: the Policy to the right of the operator
        :type pol: Policy
        :rtype: Sequential
        """
        if isinstance(other,sequential):
            return sequential([self] + other.policies)
        else:
            return sequential([self, other])

    def __div__(self, other):
        raise NotImplementedError
        #if isinstance(other, disjoint):
         #   return disjoint([self] + other.policies)
        #else:
         #   return disjoint([self, other])


    def __eq__(self, other):
        """Syntactic equality."""
        raise NotImplementedError

    def __ne__(self,other):
        """Syntactic inequality."""
        return not (self == other)

    def name(self):
        return self.__class__.__name__

    def __repr__(self):
        return "%s : %d" % (self.name(),id(self))

    def netkat_compile(self, switch_cnt, outport = False):
        pred_policy = None
        for i in range(1, switch_cnt + 1):
            if pred_policy is None:
                pred_policy = match(switch = i)
            else:
                pred_policy |= match(switch = i)

        if pred_policy is None:
            pred_policy = identity
        pol = pred_policy >> self
        import subprocess

        f = open('/tmp/in.json', 'w')
        f.write(compile_to_netkat(pol))
        f.close()

        try:
            output = subprocess.check_output(['curl', '-X', 'POST', 'localhost:9000/compile', '--data-binary', '@/tmp/in.json', '-D', '/tmp/header.txt'])
            f = open('/tmp/out.json', 'w')
            f.write(output)
            f.close()
        except subprocess.CalledProcessError:
            print "error in calling frenetic"
        
        cls = json_to_classifier(output, outport)
        f = open('/tmp/header.txt')
        time = 0
        for line in f.readlines():
            if line.startswith('x-compile-time:'):
                time = float(line[line.index(":") + 1:-1])
                break

        return (cls, time)

class Filter(Policy):
    """
    Abstact class for filter policies.
    A filter Policy will always either 

    - pass packets through unchanged
    - drop them

    No packets will ever be modified by a Filter.
    """
    def eval(self, pkt):
        """
        evaluate this policy on a single packet

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        raise NotImplementedError

    def __or__(self, pol):
        """
        The Boolean OR operator.

        :param pol: the filter Policy to the right of the operator
        :type pol: Filter
        :rtype: Union
        """
        if isinstance(pol,Filter):
            return union([self, pol])
        else:
            raise TypeError

    def __and__(self, pol):
        """
        The Boolean AND operator.

        :param pol: the filter Policy to the right of the operator
        :type pol: Filter
        :rtype: Intersection
        """
        if isinstance(pol,Filter):
            return intersection([self, pol])
        else:
            raise TypeError

    def __sub__(self, pol):
        """
        The Boolean subtraction operator.

        :param pol: the filter Policy to the right of the operator
        :type pol: Filter
        :rtype: Difference
        """
        if isinstance(pol,Filter):
            return difference(self, pol)
        else:
            raise TypeError

    def __invert__(self):
        """
        The Boolean negation operator.

        :param pol: the filter Policy to the right of the operator
        :type pol: Filter
        :rtype: negate
        """
        return negate([self])

    def __hash__(self):
        """ Hash function for using Filters in sets and dictionaries. """
        return hash(repr(self))


class Singleton(Filter):
    """Abstract policy from which Singletons descend"""

    _classifier = None

    def compile(self):
        """
        Produce a Classifier for this policy

        :rtype: Classifier
        """
        if NO_CACHE: 
            self.__class__._classifier = self.generate_classifier()
        if self.__class__._classifier is None:
            self.__class__._classifier = self.generate_classifier()
        return self.__class__._classifier

    def generate_classifier(self):
        return Classifier([Rule(identity, {self}, [self])])

@singleton
class identity(Singleton):
    """The identity policy, leaves all packets unchanged."""
    def eval(self, pkt):
        """
        evaluate this policy on a single packet

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        return {pkt}

    def intersect(self, other):
        return other

    def covers(self, other):
        return True

    def __eq__(self, other):
        return ( id(self) == id(other)
            or ( isinstance(other, match) and len(other.map) == 0) )

    
    def __repr__(self):
        return "identity"

passthrough = identity   # Imperative alias
true = identity          # Logic alias
all_packets = identity   # Matching alias


@singleton
class drop(Singleton):
    """The drop policy, produces the empty set of packets."""
    def eval(self, pkt):
        """
        evaluate this policy on a single packet

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        return set()

    def generate_classifier(self):
        if not self._classifier:
            self._classifier =  Classifier([Rule(identity,set(),[self])])
        return self._classifier

    def intersect(self, other):
        return self

    def covers(self, other):
        return False

    def __eq__(self, other):
        return id(self) == id(other)

    def __repr__(self):
        return "drop"

none = drop
false = drop             # Logic alias
no_packets = drop        # Matching alias


@singleton
class Controller(Singleton):
    def eval(self, pkt):
        return set()

    def __eq__(self, other):
        return id(self) == id(other)

    def __repr__(self):
        return "Controller"
    
class match(Filter):
    """
    Match on all specified fields.
    Matched packets are kept, non-matched packets are dropped.

    :param *args: field matches in argument format
    :param **kwargs: field matches in keyword-argument format
    """
   
    def __init__(self, *args, **kwargs):

        def _get_processed_map(*args, **kwargs):
            map_dict = dict(*args, **kwargs)
            for field in ['srcip', 'dstip']:
                try:
                    val = map_dict[field]
                    map_dict.update({field: util.string_to_network(val)})
                except KeyError:
                    pass
            return map_dict

        self.map = util.frozendict(_get_processed_map(*args, **kwargs))
        self._classifier = self.generate_classifier()
        super(match,self).__init__()

    def eval(self, pkt):
        """
        evaluate this policy on a single packet

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        return _match(**self.map).eval(pkt)

    def generate_classifier(self):
        c = _match(**self.map).generate_classifier()
        
        return c

    def __eq__(self, other):
        return ( (isinstance(other, match) and self.map == other.map)
                 or (len(self.map) == 0 and other == identity) )

    def intersect(self, pol):
        def _intersect_ip(ipfx, opfx):
            most_specific = None
            if ipfx in opfx:
                most_specific = ipfx
            elif opfx in ipfx:
                most_specific = opfx
            else:
                most_specific = None
            return most_specific

        if pol == identity:
            return self
        elif pol == drop:
            return drop
        elif not isinstance(pol,match):
            raise TypeError
        fs1 = set(self.map.keys())
        fs2 = set(pol.map.keys())
        shared = fs1 & fs2
        most_specific_src = None
        most_specific_dst = None

        for f in shared:
            if (f=='srcip'):
                most_specific_src = _intersect_ip(self.map[f], pol.map[f])
                if most_specific_src is None:
                    return drop
            elif (f=='dstip'):
                most_specific_dst = _intersect_ip(self.map[f], pol.map[f])
                if most_specific_dst is None:
                    return drop
            elif (self.map[f] != pol.map[f]):
                return drop

        d = self.map.update(pol.map)

        if most_specific_src is not None:
            d = d.update({'srcip' : most_specific_src})
        if most_specific_dst is not None:
            d = d.update({'dstip' : most_specific_dst})

        return match(**d)

    def __and__(self,pol):
        if isinstance(pol,match):
            return self.intersect(pol)
        else:
            return super(match,self).__and__(pol)

    ### hash : unit -> int
    def __hash__(self):
        return hash(self.map)

    def covers(self,other):
        # Return identity if self matches every packet that other matches (and maybe more).
        # eg. if other is specific on any field that self lacks.
        def map_check(a, b):
            ''' 
            if set(a.keys()) - set(b.keys()):
                return False
            '''
            for (f,v) in a.items():
                if not f in b:
                    return False
                other_v = b[f]
                if (f=='srcip' or f=='dstip'):
                    if v != other_v:
                        if not other_v in v:
                            return False
                elif v != other_v:
                    return False
            return True
            
        try:
            return map_check(self.map, other.map)
        except AttributeError:
            if len(self.map.keys()) == 0:
                return True
            elif other == identity:
                return False
            elif other == drop:
                return True
        return True

    def __repr__(self):
        return "match: %s" % ' '.join(map(str,self.map.items()))

class _match(match):
    def __init__(self, *args, **kwargs):
        super(_match,self).__init__(*args, **kwargs)

        self.map = self.translate_virtual_fields()

    def generate_classifier(self):
        r1 = Rule(self,{identity},[self])
        r2 = Rule(identity,set(),[None])
        return Classifier([r1, r2])

    def eval(self,pkt):
        for field, pattern in self.map.iteritems():
            try:
                v = pkt[field]
                if not field in ['srcip', 'dstip']:
                    if pattern is None or pattern != v:
                        return set()
                else:
                    v = util.string_to_IP(v)
                    if pattern is None or not v in pattern:
                        return set()
            except Exception, e:
                if pattern is not None:
                    return set()
        return {pkt}

    def translate_virtual_fields(self):
        from pyretic.core.runtime import virtual_field
        _map = {}
        _vf  = {}

        for field, pattern in self.map.iteritems():
            if field in compilable_headers:
                _map[field] = pattern
            else:
                _vf[field] = pattern

        _map.update(
          virtual_field.map_to_vlan(
            virtual_field.compress(_vf)))

        return util.frozendict(**_map)

class modify(Policy):
    """
    Modify on all specified fields to specified values.

    :param *args: field assignments in argument format
    :param **kwargs: field assignments in keyword-argument format
    """
    ### init : List (String * FieldVal) -> List KeywordArg -> unit
    def __init__(self, *args, **kwargs):
        #TODO(Josh, Cole): why this check is here?
        #if len(args) == 0 and len(kwargs) == 0:
        #    raise TypeError
        self.map = dict(*args, **kwargs)
        self.has_virtual_headers = not \
            reduce(lambda acc, f:
                       acc and (f in compilable_headers),
                   self.map.keys(),
                   True)
        self._classifier = self.generate_classifier()
        super(modify,self).__init__()

    def eval(self, pkt):
        """
        evaluate this policy on a single packet

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        return _modify(**self.map).eval(pkt)

    def generate_classifier(self):
        c = _modify(**self.map).generate_classifier()
        return c


    def __repr__(self):
        return "modify: %s" % ' '.join(map(str,self.map.items()))

    def __eq__(self, other):
        return ( isinstance(other, modify)
           and (self.map == other.map) )

class _modify(modify):
    def __init__(self, *args, **kwargs):
        super(_modify,self).__init__(*args, **kwargs)
        # Translate virtual-fields
        self.map = self.translate_virtual_fields()

    def generate_classifier(self):
        r = Rule(identity,{self},[self])
        return Classifier([r])

    def eval(self,pkt):
        return {pkt.modifymany(self.map)}

    def translate_virtual_fields(self):
        from pyretic.core.runtime import virtual_field
        _map = {}
        _vf  = {}

        for field, pattern in self.map.iteritems():
            if field in compilable_headers:
                _map[field] = pattern
            else:
                _vf[field] = pattern

        _map.update(
          virtual_field.map_to_vlan(
            virtual_field.compress(_vf)))

        return _map

# FIXME: Srinivas =).
class Query(Filter):
    """
    Abstract class representing a data structure
    into which packets (conceptually) go and with which callbacks can register.
    """
    ### init : unit -> unit
    def __init__(self):
        from multiprocessing import Lock
        self.callbacks = []
        self.bucket = set()
        self.bucket_lock = Lock()
        super(Query,self).__init__()

    def eval(self, pkt):
        """
        evaluate this policy on a single packet

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
          
        with self.bucket_lock:
            self.bucket.add(pkt)
            
            '''print "-------- in bucket eval ----------"
            print id(self)
            print pkt
            import traceback
            traceback.print_stack()
            print '-------- end eval ----------'
            '''
        return set()
        
    ### register_callback : (Packet -> X) -> unit
    def register_callback(self, fn):
        self.callbacks.append(fn)

    def __repr__(self):
        return "Query"


class FwdBucket(Query):
    """
    Class for registering callbacks on individual packets sent to
    the controller.
    """
    def __init__(self):
        super(FwdBucket, self).__init__()
        self.log = logging.getLogger('%s.FwdBucket' % __name__)
        self._classifier = self.generate_classifier()

    def generate_classifier(self):
        return Classifier([Rule(identity,{Controller},[self])])

    def apply(self):
        with self.bucket_lock:
            for pkt in self.bucket:
                self.log.info('In FwdBucket apply(): packet is:\n' + str(pkt))
                for callback in self.callbacks:
                    callback(pkt)
            self.bucket.clear()
    
    def __repr__(self):
        return "FwdBucket %s" % str(id(self))

    def __eq__(self, other):
        # TODO: if buckets eventually have names, equality should
        # be on names.
        return isinstance(other, FwdBucket) and id(self) == id(other)


class PathBucket(FwdBucket):
    """
    Class for registering callbacks on individual packets sent to controller,
    but in addition to the packet, the entire trajectory of the packet is also
    provided to the callbacks.
    """
    def __init__(self, require_original_pkt=False):
        super(PathBucket, self).__init__()
        self.runtime_topology_policy_fun = None
        self.runtime_fwding_policy_fun = None
        self.runtime_egress_policy_fun = None
        self.require_original_pkt = require_original_pkt

    def generate_classifier(self):
        return Classifier([Rule(identity,{self},[self])])

    def apply(self, original_pkt=None):
        with self.bucket_lock:
            packet_set = set()
            if self.require_original_pkt and original_pkt:
                packet_set.add(original_pkt)
            else:
                packet_set = self.bucket
            for pkt in packet_set:
                self.log.info('In PathBucket apply(): packet is:\n' + str(pkt))
                paths = self.get_trajectories(pkt)
                for callback in self.callbacks:
                    callback(pkt, paths)
            self.bucket.clear()

    def set_topology_policy_fun(self, topo_pol_fun):
        self.runtime_topology_policy_fun = topo_pol_fun

    def set_fwding_policy_fun(self, fwding_pol_fun):
        self.runtime_fwding_policy_fun = fwding_pol_fun

    def set_egress_policy_fun(self, egress_pol_fun):
        self.runtime_egress_policy_fun = egress_pol_fun

    def get_trajectories(self, pkt):
        from pyretic.core.language_tools import ast_map, default_mapper

        def data_plane_mapper(parent, children):
            if isinstance(parent, Query):
                return drop
            else:
                return default_mapper(parent, children)

        def packet_paths(pkt, topo, fwding, egress):
            """Takes a packet, a topology policy, a forwarding policy, and a
            filter to detect network egress, and returns a list of "packet
            paths". A "packet path" is just an ordered list of located packets
            denoting the trajectory of the input packet at switch ingresses,
            except for the last element of the packet path which denotes packet
            state at network egress.
            """
            at_egress = egress.eval(pkt)
            if len(at_egress) == 1: # the pkt is already at network egress
                return [pkt]

            # Move packet one hop, then recursively enumerate paths.
            pkts_moved = (fwding >> topo).eval(pkt)
            full_paths = []
            for p in pkts_moved:
                suffix_paths = packet_paths(p, topo, fwding, egress)
                for sp in suffix_paths:
                    full_paths.append([pkt] + sp)

            # Move packet one hop, then terminate paths if necessary
            pkts_egressed = (fwding >> egress).eval(pkt)
            for p in pkts_egressed:
                full_paths.append([pkt, p])

            return full_paths

        if (self.runtime_topology_policy_fun and self.runtime_fwding_policy_fun
            and self.runtime_egress_policy_fun):
            topo = self.runtime_topology_policy_fun()
            fwding = ast_map(data_plane_mapper,
                             self.runtime_fwding_policy_fun())
            egress = self.runtime_egress_policy_fun()
            return packet_paths(pkt, topo, fwding, egress)
        else:
            return []


class CountBucket(Query):
    """
    Class for registering callbacks on counts of packets sent to
    the controller.
    """
    def __init__(self):
        super(CountBucket, self).__init__()
        self.matches = {}
        self.runtime_stats_query_fun = None
        self.runtime_existing_stats_query_fun = None
        self.outstanding_switches = set()
        self.switches_in_query = set()
        self.packet_count_table = 0
        self.byte_count_table = 0
        self.packet_count_persistent = 0
        self.byte_count_persistent = 0
        self.in_update_cv = Condition()
        self.in_update = False
        self.new_bucket = True
        self.max_num_callbacks = 0
        self.max_num_callbacks_lock = Lock()
        # TODO(ngsrinivas) find a way to avoid having a log *per* bucket
        self.log = logging.getLogger('%s.CountBucket' % __name__)
        self._classifier = self.generate_classifier()

    def __repr__(self):
        return "CountBucket " + str(id(self))

    def is_new_bucket(self):
        return self.new_bucket

    def get_matches(self):
        """ Return matches contained in bucket as a string """
        output = ""
        with self.in_update_cv:
            while self.in_update:
                self.in_update_cv.wait()
            for m in self.matches:
                output += str(m) + '\n'
        return output

    def generate_classifier(self):
        return Classifier([Rule(identity,{self},[self])])

    def apply(self):
        with self.bucket_lock:
            for pkt in self.bucket:
                self.log.info('In CountBucket ' + str(id(self)) + ' apply():'
                               + ' Packet is:\n' + repr(pkt))
                self.packet_count_persistent += 1
                self.byte_count_persistent += pkt['payload_len']
            self.bucket.clear()
        self.log.debug('In bucket ' +  str(id(self)) + ' apply(): ' +
                       'persistent packet count is ' +
                       str(self.packet_count_persistent))

    def start_update(self):
        """
        Use a condition variable to mediate access to bucket state as it is
        being updated.

        Why condition variables and not locks? The main reason is that the state
        update doesn't happen in just a single function call here, since the
        runtime processes the classifier rule by rule and buckets may be touched
        in arbitrary order depending on the policy. They're not all updated in a
        single function call. In that case,

        (1) Holding locks *across* function calls seems dangerous and
        non-modular (in my opinion), since we need to be aware of this across a
        large function, and acquiring locks in different orders at different
        points in the code can result in tricky deadlocks (there is another lock
        involved in protecting bucket updates in runtime).

        (2) The "with" semantics in python is clean, and splitting that into
        lock.acquire() and lock.release() calls results in possibly replicated
        failure handling code that is boilerplate.

        """
        with self.in_update_cv:
            self.in_update = True
            self.runtime_stats_query_fun = None
            self.outstanding_switches = set()
            self.switches_in_query = set()
            self.clear_transient_counters()

    def finish_update(self):
        with self.in_update_cv:
            self.in_update = False
            self.in_update_cv.notify_all()
        if self.new_bucket:
            self.pull_existing_stats()
            self.new_bucket = False
        self.log.info("Updated bucket %d" % id(self))
       

    class match_entry(object):
        def __init__(self,match,priority,version):
            self.match = util.frozendict(match)
            self.priority = priority
            self.version = version

        def __hash__(self):
            return hash(self.match) ^ hash(self.priority) ^ hash(self.version)

        def __eq__(self,other):
            try:
                return (self.match == other.match and 
                        self.priority == other.priority and 
                        self.version == other.version)
            except:
                return False

        def __repr__(self):
            return ('(match=' + repr(self.match) + 
                    ',priority=' + repr(self.priority) + 
                    ',version=' + repr(self.version) + ')')

    class match_status(object):
        def __init__(self,to_be_deleted=False,existing_rule=False):
            self.to_be_deleted = to_be_deleted
            self.existing_rule = existing_rule

        def __hash__(self):
            return hash(self.to_be_deleted) ^ hash(self.existing_rule)

        def __eq__(self,other):
            try:
                return (self.to_be_deleted == other.to_be_deleted and 
                        self.existing_rule == other.existing_rule)
            except:
                return False
            
        def __repr__(self):
            return '(to_be_deleted=%s,existing_rule=%s)' % \
                (self.to_be_deleted,self.existing_rule)

    def add_match(self, match, priority, version):
        """Add a match to list of classifier rules to be queried for counts,
        corresponding to a given version of the classifier.
        """
        k = self.match_entry(match, priority, version)
        if not k in self.matches:
            self.matches[k] = self.match_status() 

    def delete_match(self, match, priority, version, to_be_deleted=False,
                     existing_rule=False):
        """If a rule is deleted from the classifier, mark this rule (until we
        get the flow_removed message with the counters on it).
        """
        k = self.match_entry(match, priority,version)
        if k in self.matches:
            self.matches[k].to_be_deleted = True

    def handle_flow_removed(self, match, priority, version, flow_stat):
        """Act on a flow removed message pertaining to a bucket by
           1. removing the rule from the matches structure, and
           2. adding its counters into the bucket's persistent counts.
        """
        packet_count = flow_stat['packet_count']
        byte_count   = flow_stat['byte_count']
        if packet_count > 0:
            self.log.debug(("In bucket %d handle_flow_removed\n" +
                            "got counts %d %d\n" +
                            "match %s") %
                           (id(self), packet_count, byte_count,
                            str(match) + ' ' + str(priority) + ' ' +
                            str(version)) )
        with self.in_update_cv:
            while self.in_update:
                self.in_update_cv.wait()
            k = self.match_entry(self.str_convert_match(match),
                                 priority, version)
            if k in self.matches:
                self.log.debug("Deleted flow exists in the bucket's matches")
                status = self.matches[k]
                assert status.to_be_deleted
                if not status.existing_rule: # Note: If pre-existing rule was
                    # removed, then forget that this rule ever
                    # existed. We don't count it.
                    if packet_count > 0:
                        self.log.info(("Adding persistent pkt count %d"
                                        + " to bucket %d") % (
                                packet_count, id(self) ) )
                        self.log.debug(("persistent count is now %d" %
                                        (self.packet_count_persistent +
                                         packet_count) ) )
                    self.packet_count_persistent += packet_count
                    self.byte_count_persistent += byte_count
                # Note that there is no else action. We just forget
                # that this rule was ever associated with the bucket
                # if we get a "flow removed" message before we got
                # the first ever stats reply from an existing rule.
                del self.matches[k]

    def add_pull_stats(self, fun):
        """
        Point to function that issues stats queries in the
        runtime.
        """
        self.runtime_stats_query_fun = fun

    def add_pull_existing_stats(self, fun):
        """Point to function that issues stats queries *only for rules already
        existing when the bucket was created* in the runtime.
        """
        self.runtime_existing_stats_query_fun = fun

    def pull_helper(self, pull_function):
        """Issue stats queries from the runtime using a provided runtime stats
        pulling function."""
        queries_issued = False
        with self.in_update_cv:
            while self.in_update: # ensure buckets not updated concurrently
                self.in_update_cv.wait()
            if pull_function:
                # Note: If a query is already in progress, this will wipe out
                # all its intermediate results for it.
                self.outstanding_switches = set()
                self.switches_to_query = set()
                queries_issued = pull_function() # return value denotes whether
                                                 # we expect a stats_reply in
                                                 # future
        return queries_issued

    def pull_stats(self):
        """Issue stats queries from the runtime on user program's request."""
        queries_issued = self.pull_helper(self.runtime_stats_query_fun)
        self.increment_max_num_callbacks()
        # If no queries were issued, then no matches, so just call userland
        # registered callback routines
        if not queries_issued:
            self.clear_transient_counters()
            self.log.info("Didn't issue stat queries; directly returning!")
            self.call_callbacks([self.packet_count_persistent,
                                 self.byte_count_persistent])

    def call_callbacks(self, args):
        """ Pace callbacks according to pull_stats issued by application. """
        self.log.debug("Max # callback responses left: %d" %
                        self.max_num_callbacks)
        with self.max_num_callbacks_lock:
            if self.max_num_callbacks > 0:
                self.max_num_callbacks -= 1
                for f in self.callbacks:
                    f(args)

    def increment_max_num_callbacks(self):
        """ Pace callbacks according to pull_stats issued by application. """
        with self.max_num_callbacks_lock:
            self.max_num_callbacks += 1

    def pull_existing_stats(self):
        """Issue stats queries from the runtime to track counters on rules
        already on switches.
        """
        self.pull_helper(self.runtime_existing_stats_query_fun)

    def add_outstanding_switch_query(self,switch):
        self.outstanding_switches.add(switch)
        self.switches_in_query.add(switch)

    def str_convert_match(self, m):
        """ Convert incoming flow stat matches into a form compatible with
        stored match entries. """
        new_dict = {}
        for k,v in m.iteritems():
            if not (k == 'srcip' or k == 'dstip'):
                new_dict[k] = v
            else:
                new_dict[k] = str(v)
        return new_dict

    def clear_transient_counters(self):
        self.packet_count_table = 0
        self.byte_count_table   = 0

    def handle_flow_stats_reply(self,switch,flow_stats):
        """
        Given a flow_stats_reply from switch s, collect only those
        counts which are relevant to this bucket.

        Very simple processing for now: just collect all packet and
        byte counts from rules that have a match that is in the set of
        matches this bucket is interested in.
        """
        def entries_print_helper(pfx_string=""):
            """ Pretty print bucket match entries. """
            out = ""
            for k in self.matches.keys():
                out += pfx_string + str(k) + "\n"
            return out

        def stat_in_bucket(flow_stat, s):
            """Return a matching entry for the given flow_stat in
            bucket.matches."""
            f = copy.copy(flow_stat['match'])
            f['switch'] = s
            fme = self.match_entry(self.str_convert_match(f),
                                   flow_stat['priority'],
                                   flow_stat['cookie'])
            if fme in self.matches.keys():
                return fme
            return None

        self.log.debug("Got a reply from switch %s" % switch)
        with self.in_update_cv:
            while self.in_update:
                self.log.debug("Waiting for update to finish.")
                self.in_update_cv.wait()
            self.log.debug("Current set of outstanding switches is:")
            self.log.debug(str(self.outstanding_switches))
            if switch in self.outstanding_switches:
                for f in flow_stats:
                    if 'match' in f:
                        me = stat_in_bucket(f, switch)
                        extracted_pkts = f['packet_count']
                        extracted_bytes = f['byte_count']
                        if extracted_pkts > 0 and not me:
                            self.log.debug("Packet not counted: \n%s %s %s" %
                                           (str(f['match']),
                                            "priority=%d" % f['priority'],
                                            "version=%d" % f['cookie']))
                            self.log.debug("Existing keys: \n%s" %
                                           entries_print_helper())
                        if me:
                            if extracted_pkts > 0:
                                self.log.debug('In bucket ' + str(id(self)) +
                                               ': found matching stats_reply:')
                                self.log.debug(str(me))
                                self.log.debug('packets: ' +
                                               str(extracted_pkts) + ' bytes: '
                                               + str(extracted_bytes))
                            if not self.matches[me].existing_rule:
                                self.packet_count_table += extracted_pkts
                                self.byte_count_table   += extracted_bytes
                            else: # pre-existing rule when bucket was created
                                self.log.debug(('In bucket %d: removing' +
                                                'pre-existing rule counts %d' +
                                                ' %d') % id(self))
                                self.packet_count_persistent -= extracted_pkts
                                self.byte_count_persistent -= extracted_bytes
                                self.clear_existing_rule_flag(me)
                    else:
                        raise RuntimeError("weird flow entry")
                self.outstanding_switches.remove(switch)
                self.log.debug("Current set of outstanding switches is:")
                self.log.debug(str(self.outstanding_switches))
        # If have all necessary data, call user-land registered callbacks
        self.log.info( ('*** Bucket %d flow_stats_reply\n' % id(self)) +
                        ('table pktcount %d persistent pktcount %d total %d' % (
                    self.packet_count_table,
                    self.packet_count_persistent,
                    self.packet_count_table + self.packet_count_persistent ) ) )
        if not self.outstanding_switches:
            self.log.debug("No outstanding switches; calling callbacks")
            self.call_callbacks([(self.packet_count_table +
                                  self.packet_count_persistent),
                                 (self.byte_count_table   +
                                  self.byte_count_persistent)])
            self.clear_transient_counters()

    def clear_existing_rule_flag(self, entry):
        """Clear the "existing rule" flag for the provided entry in
        self.matches. This method should only be called in the context of
        holding the bucket's in_update_cv since it updates the matches
        structure.
        """
        assert k in self.matches
        self.matches[k].existing_rule = False

    def __eq__(self, other):
        # TODO: if buckets eventually have names, equality should
        # be on names.
        return id(self) == id(other)

################################################################################
# Combinator Policies                                                          #
################################################################################

class CombinatorPolicy(Policy):
    """
    Abstract class for policy combinators.

    :param policies: the policies to be combined.
    :type policies: list Policy
    """
    ### init : List Policy -> unit
    def __init__(self, policies=[]):
        self.policies = list(policies)
        self._classifier = None
        super(CombinatorPolicy,self).__init__()

    def compile(self):
        """
        Produce a Classifier for this policy

        :rtype: Classifier
        """
        if NO_CACHE: 
            self._classifier = self.generate_classifier()
        if not self._classifier:
            self._classifier = self.generate_classifier()
        return self._classifier

    def __repr__(self):
        return "%s:\n%s" % (self.name(),util.repr_plus(self.policies))

    def __eq__(self, other):
        return ( self.__class__ == other.__class__
           and   self.policies == other.policies )


class negate(CombinatorPolicy,Filter):
    """
    Combinator that negates the input policy.

    :param policies: the policies to be negated.
    :type policies: list Filter
    """
    def eval(self, pkt):
        """
        evaluate this policy on a single packet

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        if self.policies[0].eval(pkt):
            return set()
        else:
            return {pkt}

    def generate_classifier(self):
        inner_classifier = self.policies[0].compile()
        return ~inner_classifier


class parallel(CombinatorPolicy):
    """
    Combinator for several policies in parallel.

    :param policies: the policies to be combined.
    :type policies: list Policy
    """
    def __new__(self, policies=[]):
        # Hackety hack.
        if len(policies) == 0:
            return drop
        else:
            rv = super(parallel, self).__new__(parallel, policies)
            rv.__init__(policies)
            return rv

    def __init__(self, policies=[]):
        if len(policies) == 0:
            raise TypeError
        super(parallel, self).__init__(policies)

    def __add__(self, pol):
        if isinstance(pol,parallel):
            return parallel(self.policies + pol.policies)
        else:
            return parallel(self.policies + [pol])

    def eval(self, pkt):
        """
        evaluates to the set union of the evaluation
        of self.policies on pkt

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        output = set()
        for policy in self.policies:
            output |= policy.eval(pkt)
        return output

    def generate_classifier(self):
        if len(self.policies) == 0:  # EMPTY PARALLEL IS A DROP
            return drop.compile()
        classifiers = map(lambda p: p.compile(), self.policies)
        return reduce(lambda acc, c: acc + c, classifiers)


class union(parallel,Filter):
    """
    Combinator for several filter policies in parallel.

    :param policies: the policies to be combined.
    :type policies: list Filter
    """
    def __new__(self, policies=[]):
        # Hackety hack.
        if len(policies) == 0:
            return drop
        else:
            rv = super(parallel, self).__new__(union, policies)
            rv.__init__(policies)
            return rv

    def __init__(self, policies=[]):
        if len(policies) == 0:
            raise TypeError
        super(union, self).__init__(policies)

    ### or : Filter -> Filter
    def __or__(self, pol):
        if isinstance(pol,union):
            return union(self.policies + pol.policies)
        elif isinstance(pol,Filter):
            return union(self.policies + [pol])
        else:
            raise TypeError


class sequential(CombinatorPolicy):
    """
    Combinator for several policies in sequence.

    :param policies: the policies to be combined.
    :type policies: list Policy
    """
    def __new__(self, policies=[]):
        # Hackety hack.
        if len(policies) == 0:
            return identity
        else:
            rv = super(sequential, self).__new__(sequential, policies)
            rv.__init__(policies)
            return rv

    def __init__(self, policies=[]):
        if len(policies) == 0:
            raise TypeError
        super(sequential, self).__init__(policies)

    def __rshift__(self, pol):
        if isinstance(pol,sequential):
            return sequential(self.policies + pol.policies)
        else:
            return sequential(self.policies + [pol])

    def eval(self, pkt):
        """
        evaluates to the set union of each policy in 
        self.policies on each packet in the output of the 
        previous.  The first policy in self.policies is 
        evaled on pkt.

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        prev_output = {pkt}
        output = prev_output
        for policy in self.policies:
            if not prev_output:
                return set()
            if policy == identity:
                continue
            if policy == drop:
                return set()
            output = set()
            for p in prev_output:
                output |= policy.eval(p)
            prev_output = output
        return output

    def generate_classifier(self):
        assert(len(self.policies) > 0)
        classifiers = map(lambda p: p.compile(),self.policies)
        for c in classifiers:
            assert(c is not None)
        return reduce(lambda acc, c: acc >> c, classifiers)
        

class intersection(sequential,Filter):
    """
    Combinator for several filter policies in sequence.

    :param policies: the policies to be combined.
    :type policies: list Filter
    """
    def __new__(self, policies=[]):
        # Hackety hack.
        if len(policies) == 0:
            return identity
        else:
            rv = super(sequential, self).__new__(intersection, policies)
            rv.__init__(policies)
            return rv

    def __init__(self, policies=[]):
        if len(policies) == 0:
            raise TypeError
        super(intersection, self).__init__(policies)

    ### and : Filter -> Filter
    def __and__(self, pol):
        if isinstance(pol,intersection):
            return intersection(self.policies + pol.policies)
        elif isinstance(pol,Filter):
            return intersection(self.policies + [pol])
        else:
            raise TypeError

################################################################################
# Derived Policies                                                             #
################################################################################

class DerivedPolicy(Policy):
    """
    Abstract class for a policy derived from another policy.

    :param policy: the internal policy (assigned to self.policy)
    :type policy: Policy
    """
    def __init__(self, policy=identity):
        self.policy = policy
        self._classifier = None
        super(DerivedPolicy,self).__init__()

    def eval(self, pkt):
        """
        evaluates to the output of self.policy.

        :param pkt: the packet on which to be evaluated
        :type pkt: Packet
        :rtype: set Packet
        """
        return self.policy.eval(pkt)

    def compile(self):
        """
        Produce a Classifier for this policy

        :rtype: Classifier
        """
        if NO_CACHE: 
            self._classifier = self.generate_classifier()
        if not self._classifier:
            self._classifier = self.generate_classifier()
        return self._classifier

    def generate_classifier(self):
        return self.policy.compile()

    def __repr__(self):
        return "[DerivedPolicy]\n%s" % repr(self.policy)

    def __eq__(self, other):
        return ( self.__class__ == other.__class__
           and ( self.policy == other.policy ) )


class difference(DerivedPolicy,Filter):
    """
    The difference between two filter policies..

    :param f1: the minuend
    :type f1: Filter
    :param f2: the subtrahend
    :type f2: Filter
    """
    def __init__(self, f1, f2):
       self.f1 = f1
       self.f2 = f2
       super(difference,self).__init__(~f2 & f1)

    def __repr__(self):
        return "difference:\n%s" % util.repr_plus([self.f1,self.f2])


class if_(DerivedPolicy):
    """
    if pred holds, t_branch, otherwise f_branch.

    :param pred: the predicate
    :type pred: Filter
    :param t_branch: the true branch policy
    :type pred: Policy
    :param f_branch: the false branch policy
    :type pred: Policy
    """
    def __init__(self, pred, t_branch, f_branch=identity):
        self.pred = pred
        self.t_branch = t_branch
        self.f_branch = f_branch
        super(if_,self).__init__((self.pred >> self.t_branch) +
                                 ((~self.pred) >> self.f_branch))

    def eval(self, pkt):
        if self.pred.eval(pkt):
            return self.t_branch.eval(pkt)
        else:
            return self.f_branch.eval(pkt)

    def __repr__(self):
        return "if\n%s\nthen\n%s\nelse\n%s" % (util.repr_plus([self.pred]),
                                               util.repr_plus([self.t_branch]),
                                               util.repr_plus([self.f_branch]))


class fwd(DerivedPolicy):
    """
    fwd out a specified port.

    :param outport: the port on which to forward.
    :type outport: int
    """
    def __init__(self, outport):
        self.outport = outport
        super(fwd,self).__init__(modify(outport=self.outport))

    def __repr__(self):
        return "fwd %s" % self.outport


class xfwd(DerivedPolicy):
    """
    fwd out a specified port, unless the packet came in on that same port.
    (Semantically equivalent to OpenFlow's forward action

    :param outport: the port on which to forward.
    :type outport: int
    """
    def __init__(self, outport):
        self.outport = outport
        super(xfwd,self).__init__((~match(inport=outport)) >> fwd(outport))

    def __repr__(self):
        return "xfwd %s" % self.outport


################################################################################
# Dynamic Policies                                                             #
################################################################################

class DynamicPolicy(DerivedPolicy):
    """
    Abstact class for dynamic policies.
    The behavior of a dynamic policy changes each time self.policy is reassigned.
    """
    ### init : unit -> unit
    def __init__(self,policy=drop):
        self._policy = policy
        self.notify = None
        self._classifier = None
        super(DerivedPolicy,self).__init__()

    def set_network(self, network):
        pass

    def attach(self,notify):
        self.notify = notify

    def detach(self):
        self.notify = None

    def changed(self):
        if self.notify:
            self.notify(self)

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, policy):
        prev_policy = self._policy
        self._policy = policy
        self.changed()

    def __repr__(self):
        return "[DynamicPolicy]\n%s" % repr(self.policy)


class DynamicFilter(DynamicPolicy,Filter):
    """
    Abstact class for dynamic filter policies.
    The behavior of a dynamic filter policy changes each time self.policy is reassigned.
    """
    def __init__(self, policy=drop):
        super(DynamicFilter, self).__init__(policy)
        self.path_notify = None

    def path_attach(self, path_notify):
        self.path_notify = path_notify

    def path_detach(self):
        self.path_notify = None

    def changed(self):
        if self.path_notify:
            self.path_notify(self)
        if self.notify:
            self.notify(self)

    def __hash__(self):
        return id(self)


class flood(DynamicPolicy):
    """
    Policy that floods packets on a minimum spanning tree, recalculated
    every time the network is updated (set_network).
    """
    def __init__(self):
        self.mst = None
        self.log = logging.getLogger('%s.flood' % __name__)
        super(flood,self).__init__()

    def set_network(self, network):
        changed = False
        if not network is None:
            updated_mst = Topology.minimum_spanning_tree(network.topology)
            if not self.mst is None:
                if self.mst != updated_mst:
                    self.mst = updated_mst
                    changed = True
            else:
                self.mst = updated_mst
                changed = True
        if changed:
            self.log.debug("Printing updated MST:\n %s" % str(updated_mst))
            self.policy = parallel([
                    match(switch=switch) >>
                        parallel(map(xfwd,attrs['ports'].keys()))
                    for switch,attrs in self.mst.nodes(data=True)])

    def __repr__(self):
        try:
            return "flood on:\n%s" % self.mst
        except:
            return "flood"


class ingress_network(DynamicFilter):
    """
    Returns True if a packet is located at a (switch,inport) pair entering
    the network, False otherwise.
    """
    def __init__(self):
        self.egresses = None
        super(ingress_network,self).__init__()

    def set_network(self, network):
        updated_egresses = network.topology.egress_locations()
        if not self.egresses == updated_egresses:
            self.egresses = updated_egresses
            self.policy = parallel([match(switch=l.switch,
                                       inport=l.port_no)
                                 for l in self.egresses])

    def __repr__(self):
        return "ingress_network"


class egress_network(DynamicFilter):
    """
    Returns True if a packet is located at a (switch,outport) pair leaving
    the network, False otherwise.
    """
    def __init__(self):
        self.egresses = None
        super(egress_network,self).__init__()

    def set_network(self, network):
        updated_egresses = network.topology.egress_locations()
        if not self.egresses == updated_egresses:
            self.egresses = updated_egresses
            self.policy = parallel([match(switch=l.switch,
                                       outport=l.port_no)
                                 for l in self.egresses])

    def __repr__(self):
        return "egress_network"

def virtual_field_tagging():
    from pyretic.core.runtime import virtual_field
    vf_matches = {}
    for name in virtual_field.fields.keys():
        vf_matches[name] = None
    
    return ((
        ingress_network() >> modify(**vf_matches))+
        (~ingress_network()))

def virtual_field_untagging():
    from pyretic.core.runtime import virtual_field
    vf_matches = {}
    for name in virtual_field.fields.keys():
        vf_matches[name] = None
    
    return ((
        egress_network() >> _modify(vlan_id=0, vlan_pcp=0))+
        (~egress_network()))


############### netkat stuff #####################
import json
def mk_filter(pred):
  return { "type": "filter", "pred": pred }

def mk_test(hv):
  return { "type": "test", "header": hv["header"], "value": hv["value"] }

def mk_mod(hv):

  return { "type": "mod", "header": hv["header"], "value": hv["value"] }

def mk_header(h, v):
  return { "header": h, "value": v }


def to_int(bytes):
  n = 0
  for b in bytes:
    n = (n << 8) + ord(b)
  # print "Ethernet: %s -> %s" % (bytes, n)
  return n

def unip(v):
  # if isinstance(v, IPAddr):
  #   bytes = v.bits
  #   n = 0
  #   for b in bytes:
  #     n = (n << 8) + ord(b)
  #   print "IPAddr: %s -> %s (len = %s) -> %s" % (v, bytes, len(bytes), n)
  #   return { "addr": n, "mask": 32 }
  if isinstance(v, IPv4Network):
    return { "addr": str(v.ip), "mask": v.prefixlen }   
  elif isinstance(v, str):
    return { "addr" : v, "mask" : 32}
  else:
    raise TypeError(type(v))

def unethaddr(v):
  return repr(v)

def physical(n):
  return { "type": "physical", "port": n }

def header_val(h, v):
  if h == "switch":
    return mk_header("switch", v)
  elif h == "inport" or h == "outport":
    return mk_header("location", physical(v))
  elif h == "srcmac":
    return mk_header("ethsrc", unethaddr(v))
  elif h == "dstmac":
    return mk_header("ethdst", unethaddr(v))
  elif h == "vlan_id":
    return mk_header("vlan", v)
  elif h == "vlan_pcp":
    return mk_header("vlanpcp", v)
  elif h == "ethtype":
    return mk_header("ethtype", v)
  elif h == "protocol":
    return mk_header("inproto", v)
  elif h == "srcip":
    return mk_header("ip4src", unip(v))
  elif h == "dstip":
    return mk_header("ip4dst", unip(v))
  elif h == "srcport":
    return mk_header("tcpsrcport", v)
  elif h == "dstport":
    return mk_header("tcpdstport", v)
  else:
    raise TypeError("bad header %s" % h)

def match_to_pred(m):
  lst = [mk_test(header_val(h, m[h])) for h in m]
  return mk_and(lst)

def mod_to_pred(m):
  lst = [ mk_mod(header_val(h, m[h])) for h in m ]
  return mk_seq(lst)


def to_pred(p):
  if isinstance(p, match):
    return match_to_pred(_match(**p.map).map)
  elif p == identity:
    return { "type": "true" }
  elif p == drop:
    return { "type": "false" }
  elif isinstance(p, negate):
    # Only policies[0] is used in Pyretic
    return { "type": "neg", "pred": to_pred(p.policies[0]) }
  elif isinstance(p, union) or isinstance(p, parallel):
    return mk_or(map(to_pred, p.policies))
  elif isinstance(p, intersection):
    return mk_and(map(to_pred, p.policies))
  elif isinstance(p, ingress_network) or isinstance(p, egress_network):
    return to_pred(p.policy)

  else:
    raise TypeError(p)

# TODO(arjun): Consider using aspects to inject methods into each class. That
# would be better object-oriented style.
def to_pol(p):
  if isinstance(p, match):
    return mk_filter(to_pred(p))
  elif p == identity:
    return mk_filter({ "type": "true" })
  elif p == drop:
    return mk_filter({ "type": "false" })
  elif isinstance(p, modify):
    return mod_to_pred(_modify(**p.map).map)
  elif isinstance(p, negate):
    return mk_filter(to_pred(p))
  elif isinstance(p, union):
    return mk_filter(to_pred(p))
  elif isinstance(p, parallel):
    return mk_union(map(to_pol, p.policies))
  #elif isinstance(p, disjoint):
    #return mk_disjoint(map(to_pol, p.policies))
  elif isinstance(p, intersection):
    return mk_filter(to_pred(p))
  elif isinstance(p, sequential):
    return mk_seq(map(to_pol, p.policies))
  elif isinstance(p, fwd):
    return mk_mod(mk_header("location", physical(p.outport)))
  elif isinstance(p, if_):
    c = to_pred(p.pred)
    return mk_union([mk_seq([mk_filter(c), to_pol(p.t_branch)]),
                     mk_seq([mk_filter({ "type": "neg", "pred": c }), to_pol(p.f_branch)])])    
  elif isinstance(p, FwdBucket):
      return {"type" : "mod", "header" : "location", "value": {"type" : "pipe", "name" : str(id(p))}}
  elif isinstance(p, ingress_network) or isinstance(p, egress_network) or isinstance(p, DynamicPolicy):
      return to_pol(p.policy)
  else:
    raise TypeError("unknown policy %s" % type(p))

def mk_union(pols):
  return { "type": "union", "pols": pols }

def mk_disjoint(pols):
  return { "type": "disjoint", "pols": pols }

def mk_seq(pols):
  return { "type": "seq", "pols": pols }

def mk_and(preds):
  return { "type": "and", "preds": preds }

def mk_or(preds):
  return { "type": "or", "preds": preds }

# Converts a Pyretic policy into NetKAT, represented
# as a JSON string.
def compile_to_netkat(pyretic_pol):
  return json.dumps(to_pol(pyretic_pol))


############## json to policy ###################

field_map = {'dlSrc' : 'srcmac', 'dlDst': 'dstmac', 'dlTyp': 'ethtype', 
                'dlVlan' : 'vlan_id', 'dlVlanPcp' : 'vlan_pcp',
                'nwSrc' : 'srcip', 'nwDst' : 'dstip', 'nwProto' : 'protocol',
                'tpSrc' : 'srcport', 'tpDst' : 'dstport', 'inPort' : 'inport'}

def create_match(pattern, switch_id):
    if switch_id > 0:
        match_map = {'switch' : switch_id}
    else:
        match_map = {}
    for k,v in pattern.items():
        # HACKETY HACK: remove nwProto from netkat generated classifier
        if v is not None and k != "dlTyp" and k != "nwProto":
            match_map[field_map[k]] = v

    return match(**match_map)

def create_action(action, inport):
    if len(action) == 0:
        return set()
    else:
        res = set()

        for act_list in action:
            mod_dict = {}
            for act in act_list:
                if act[0] == "Modify":
                    hdr_field = act[1][0][3:]
                    if hdr_field == "Vlan" or hdr_field == "VlanPcp":
                        hdr_field = 'dl' + hdr_field
                    else:
                        hdr_field = hdr_field[0].lower() + hdr_field[1:]
                    hdr_field = field_map[hdr_field]
                    value = act[1][1]
                    if hdr_field == 'srcmac' or hdr_field == 'dstmac':
                        value = MAC(value)
                    mod_dict[hdr_field] = value
                elif act[0] == "Output":
                    outout_seen = True
                    out_info = act[1]
                    if out_info['type'] == 'physical':
                        mod_dict['outport'] = out_info['port']
                    elif out_info['type'] == 'controller':
                        res.add(Controller)
                    #elif out_info['type'] == 'inport' and inport is not None:
                        #mod_dict['outport'] = inport 
            
            if len(mod_dict) > 0:
                res.add(modify(**mod_dict))
        if len(res) == 0:
            res.add(identity)
    return res
        
def json_to_classifier(fname, outport = False):
    if outport:
        field_map['inPort'] = 'outport'
    data = json.loads(fname)
    rules = []
    for sw_tbl in data:
        switch_id = sw_tbl['switch_id']
        for rule in sw_tbl['tbl']:
            prio = rule['priority']
            m = create_match(rule['pattern'], switch_id)
            inport = None
            if 'inport' in m.map:
                inport = m.map['inport']
            action = create_action(rule['action'], inport)
            rules.append( (prio, Rule(m, action)))
    #rules.sort()
    rules = [v for (k,v) in rules]
    return Classifier(rules)

